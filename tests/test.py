from dataclasses import dataclass
from neomate.neomate import Neomate, BaseNode, NodeAttrError
from typing import List
import pytest
from unittest.mock import MagicMock
from typeguard import TypeCheckError
@dataclass
class Person(BaseNode):
    name : str
    age : int
    gender : bool
    hobbies : List[str]
    __nodename__ : str = "Person"

@dataclass
class InvalidPersonNodename(BaseNode):
    name : str
    age : int
    gender : bool
    hobbies : List[str]

@dataclass
class InvalidPersonAnnotation(BaseNode):
    name : str
    age : int
    gender : bool
    hobbies : List[int]

class TestNeomateCreate:
    @pytest.fixture
    def mock_driver(self):
        driver = MagicMock()
        session = MagicMock()
        tx = MagicMock()
        driver.session.return_value.__enter__.return_value =session
        session.begin_transaction.return_value.__enter__.return_value = tx
        tx.run.return_value.data.return_value = []
        return driver
    

    @pytest.fixture
    def neomate(self, mock_driver):
        neomate = Neomate(driver = mock_driver)
        return neomate
    

    def test_add_node(self, neomate, mock_driver):
        person = Person(name = "John", age = 36, gender=True, hobbies=["swimming", "basketball"])
        neomate.add(person)
        mock_driver.session.assert_called_once()
        session = mock_driver.session.return_value.__enter__.return_value
        tx = session.begin_transaction.return_value.__enter__.return_value
        tx.run.assert_called_once()
        args, kwargs = tx.run.call_args
        assert "CREATE(node:Person {name:$name, age:$age, gender:$gender, hobbies:$hobbies})", args[0]
        assert args[1] =={"name":"John", "age":36, "gender":True, "hobbies":["swimming", "basketball"]}

    def test_node_without_nodename(self, neomate):
        person = InvalidPersonNodename(name = "John", age = 36, gender=True, hobbies=["swimming", "basketball"])
        with pytest.raises(NodeAttrError) as exception_info:
            neomate.add(person)
        assert "Neomate does not found __nodename__ in attrs" == str(exception_info.value)

    def test_node_invalid_annotation_type(self, neomate):
        person = InvalidPersonAnnotation(name = "John", age = 36, gender=True, hobbies=["swimming", "basketball"])
        with pytest.raises(TypeCheckError) as exception_info:
            neomate.add(person)
        assert "not an instance of int" in str(exception_info.value)
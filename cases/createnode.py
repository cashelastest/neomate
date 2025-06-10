import sys
import os
from typing import List
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dataclasses import dataclass
from neo4j import GraphDatabase
from dotenv import load_dotenv
from neomate.neomate import Neomate
from neomate.BaseNode import BaseNode
load_dotenv()
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", os.getenv("PASSWORD")))
session = driver.session()


@dataclass
class Person(BaseNode):
    name : str
    age : int
    gender : bool
    hobbies : List[int]
    __nodename__ : str = "Person"

person = Person(name = "John", age = 36, gender=True, hobbies=["swimming", "basketball"])
neo = Neomate(driver=driver)
try:
    neo.add(person)
except Exception as error:
    print(error)
from unittest.mock import Mock,MagicMock
from neomate.NeoMate import NeoMate


class TestNeoRacoon:
    def setup_method(self):
        self.mock_session = Mock()
        self.mock_transaction = Mock()
        self.mock_session.begin_transaction.return_value = self.mock_transaction
        self.helper = NeoMate(session=self.mock_session)
        

    def test_add_node(self):
        self.helper.add_node("Person", name = "Sanya")
        self.mock_transaction.run.assert_called_once_with("""CREATE(a:Person{name:'Sanya'})""")
        
        
    def test_add_node_strong_case(self):
        self.helper.add_node("Person", name = "Sanya", age = 16, hobbies = ["programming", "music"])
        self.mock_transaction.run.assert_called_once_with("""CREATE(a:Person{name:'Sanya',age:16,hobbies:['programming', 'music']})""")
        
        
    def test_creating_relationships_fail_data(self):
        self.mock_transaction.run.return_value = Mock(single = Mock(return_value={"r":0}))
        self.helper.create_relationships(
            "Person'","name", "Sanya", "Okay'", "OДНОКЛАССНИКИ"
        )
        assert self.mock_transaction.rollback.called
        assert not self.mock_transaction.commit.called
    
    def test_creating_relationships_right_data(self):
        self.mock_transaction.run.return_value = Mock(single = Mock(return_value={"r":1}))
        self.helper.create_relationships(
            "Person","name", "Sanya", "Okay", "OДНОКЛАССНИКИ"
        )
        assert self.mock_transaction.commit.called
        
    def test_get_node(self):
        magic = MagicMock()
        magic.__iter__ .return_value= [{'a':{"name":"Alex"}}]
        self.mock_transaction.run.return_value = magic
        result = self.helper.get_node("Person", name="Alex")
        assert self.mock_transaction.commit.called
        assert result ==[{"name":"Alex"}]
        

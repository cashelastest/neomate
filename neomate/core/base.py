from contextlib import contextmanager
from logger.logger import Logger
from utils.utils import query_maker


    
class NeoBase:
    def __init__(self, session:object):
        self.session = session
        self.logger = Logger().create_logger()
        
        
    @contextmanager
    def trans(self):
        """
        creates transaction in error case - rolls back, otherwise - commits changes
        """
        transaction = self.session.begin_transaction()
        try:
            yield transaction
            transaction.commit()

        except Exception as e:
            transaction.rollback()
            self.logger.error("Error ", exc_info=True)
            
            
    def add_node(self, type:str, **kwargs):

        query = f"""CREATE(a:{type}"""
        if kwargs:
            query +="{"+ query_maker(kwargs) +"})"
        with self.trans() as tx:
            tx.run(query)

        
    def create_relationships(self, type1: str,type2:str, property1: str, value1, value2, relationship_name: str):
        """Creates relationship between two nodes of the same type.

    Args:
        type1 (str): Type of both start and end nodes
        property1 (str): Property name to match nodes by
        value1 (str | int): Property value to find start node
        value2 (str | int): Property value to find end node
        relate_name (str): Name of relationship to create

    Raises:
        Exception: If either start or end node not found
        Exception: If relationship creation fails

    Example:
        >>> create_relationships("Person", "name", "John", "Jane", "KNOWS")
        # Creates (John)-[:KNOWS]->(Jane) relationship
    """
        def format_value(value):
            return f'"{value}"' if isinstance(value, str) else str(value)
        
        query = f"""
            MATCH (a:{type1}),(b:{type2}) 
            WHERE a.{property1}={format_value(value1)} AND b.{property1}={format_value(value2)}
            CREATE (a)-[r:{relationship_name}]->(b)
            RETURN count(a) as a, count(b) as b, count(r) as r
        """

        with self.trans() as tx:
            response = tx.run(query)
            result = response.single()['r']
            if result != 0:
                self.logger.info(f"Successfully created relationship between {type1} {property1} {value1} and {type1} {property1}={value2}")
            else:
                self.logger.error(f"ERROR! Did not find elements with this check: {type1} {property1} {value1} and {type1} {property1}={value2}")
                raise
                
                
    def get_node(self,type:str,query_type = None, **kwargs)->dict|None:
        """Finds nodes in database by specified parameters.

        Args:
            type (str): Name of node type to search for
            query_type (str, optional): Type of condition joining ('AND' or 'OR'). 
                If None, defaults to 'OR'
            **kwargs: Search parameters in format field_name=value

        Returns:
            list[dict]: List of dictionaries containing node properties. 
                Empty list if no nodes found.

        Examples:
            >>> get_node("Person", name="John", age=25)  # Finds Person with name OR age
            >>> get_node("Person", query_type="and", name="John", age=25)  # Must match both
        """
        query = f"""
        MATCH (a:{type}) WHERE 
        """
        i = 0
        answer = list()
        for key,value in kwargs.items():
            if isinstance(value, str):
                query += f"""a.{key}='{value}'"""
            else:
                query += f"a.{key}={value}"
            i+=1
            if i >=len(kwargs):
                continue
            elif query_type == "and":
                query +=" AND "
            else:
                query+=" OR "
        query += " RETURN a"
        with self.trans() as tx:
            result = tx.run(query)
            answer = [dict(res["a"]) for res in result]
        if answer:
            self.logger.info(f"Succesfully found nodes for in {type} for {kwargs} params")
            return answer
        else:
            self.logger.error(f"Can`t find anything with this type and  params {type} {kwargs}")
            
            
    def add_nodes(self, type:str, lst:list):
        """Creates multiple nodes in a single transaction.

    Args:
        type (str): Default type for nodes if not specified in data
        lst (list): List of dictionaries where each dict contains:
            - NODE_TYPE (optional): Override default node type
            - Other key-value pairs: Node properties

    Note:
        - Creates all nodes in a single Cypher query for better performance
        - Each node can have different type if NODE_TYPE is specified
        - Strings are automatically quoted in query generation
    """
        query = """CREATE"""
        for index, element in enumerate(lst):
            query +=f"(a{index}:{element["NODE_TYPE"] if "NODE_TYPE" in element.keys() else type}" + "{" +query_maker(element)+"}),"
        query = query[:-1]
        with self.trans() as tx:
            tx.run(query)
            

    def delete_all_nodes(self, delete_relationships:bool):
        """
        deletes all nodes
        Args:
            delete_relationships (bool): param, if True -> deletes relationships
        """
        query = f"""MATCH (a) {'DETACH DELETE' if delete_relationships else 'DELETE'} a"""
        with self.trans() as tx:
            tx.run(query)

    

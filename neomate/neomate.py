from dataclasses import dataclass
from typing import *
from neo4j import Driver
from neomate.NeoError import NodeAttrError
from .logger import get_logger
from logging import Logger
from neomate.BaseNode import BaseNode
@dataclass
class Neomate:
    driver: Driver
    logger:Logger = get_logger()
    
    def run_query(self, query, params=None):
        if params is None:
            params = {}
        
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                try:
                    result = tx.run(query, params)
                    data = result.data()
                    tx.commit()
                    return data
                except Exception as e:
                    tx.rollback()
                    self.logger.error(f"Transaction rolled back: {e}")
                    raise
    def add(self, node):
        if not isinstance(node, BaseNode):
            raise Exception(f"{node.__class__.__name__ } is not an instance of BaseNode")
        node.check_types_by_annotations()
        if not hasattr(node, "__nodename__"):
            raise NodeAttrError(node.__class__.__name__, "__nodename__", "Neomate does not found __nodename__ in attrs")
        nodename = getattr(node, "__nodename__")
        params = vars(node)
        if params.get("__nodename__"):
            del params["__nodename__"]
        query = f"CREATE (node:{nodename}  {self._generate_params(params) })"
        self.logger.info(f'Generated query for adding {nodename}:\n{query}')
        self.run_query(query, params)
        self.logger.info(f"Successfully added {nodename} to db")

            

    def _generate_params(self, params):
        if not params:
            return ""
        return "{" + ", ".join([f"{name}: ${name}" for name in params.keys()]) + "}"

    def add_all(self, node):
        pass
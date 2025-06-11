from dataclasses import dataclass,fields
from typing import Dict, List, Any
from typeguard import typechecked
from neomate.Connection import NeoConnection
from neomate.logger import get_logger
from neomate.utils import sync_async_method
from logging import Logger
@dataclass
class CypherQuery:
    field_name :str

    def __eq__(self, value):
        text_query = f"node.{self.field_name} = ${self.field_name}"
        params = {self.field_name:value}
        return CypherQueryWhere(text_query, params)

@dataclass
class CypherQueryWhere:
    query :str
    params : Dict[str, Any]

@dataclass
class QueryBuilder:
    nodename : str
    model : Any
    logger : Logger = get_logger()
    filter : CypherQueryWhere = None
    _limit : int = None

    @typechecked
    def where(self, query:CypherQueryWhere):
        self.filter = query
        return self

    @typechecked
    def limit(self,value:int):
        self._limit = value
        return self
    
    @typechecked
    def build(self):
        query = f"MATCH (node:{self.nodename})\n"
        query +=f"WHERE {self.filter.query}\n"
        query += "RETURN node\n"
        if self._limit:
            query+= f"LIMIT {self._limit}"
        return query, self.filter.params

    def _create_safe_models(self, node_data):
        model_defaults = {}
        for field in fields(self.model):
            if field.name in node_data:
                model_defaults[field.name] = node_data[field.name]
            elif field.default != field.default_factory:
                model_defaults[field.name] = field.default
            else:
                model_defaults[field.name] = None
                self.logger.critical(f"Model has additional field: {field.name}. Neomate setted None value")
        return self.model(**model_defaults)
    
    @sync_async_method
    async def run(self):
        query, params = self.build()
        
        node_data = await NeoConnection.run_query(query, params)
        try:
            model_list_object = [self._create_safe_models(node['node']) for node in node_data]
        except Exception as e:
            self.logger.error(f"Error in creating objects:{e}")
            raise
        return model_list_object
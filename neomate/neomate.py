from dataclasses import fields
from typing import *

from neomate.NeoError import NodeAttrError
from .logger import get_logger
from logging import Logger
from neomate.BaseNode import BaseNode
from neomate.Query import  QueryBuilder
from neomate.Connection import NeoConnection

from neomate.utils import sync_async_method
class Neomate:
    def __init__(self, driver, logger:Logger = get_logger()):
        self.logger = logger
        NeoConnection(driver)

    @staticmethod
    def _get_model_info(model):
        if isinstance(model, type):
            return model, model.__name__
        else:
            return model.__class__, model.__class__.__name__

    @staticmethod
    def _check_is_model(model):
        model_class, model_name = Neomate._get_model_info(model)
        
        if isinstance(model, type):
            if not issubclass(model, BaseNode):
                raise Exception(f"{model_name} is not a subclass of BaseNode")
        else:
            if not isinstance(model, BaseNode):
                raise Exception(f"{model_name} is not an instance of BaseNode")

    @staticmethod  
    def _check_model_annotations(model):
        model_class, model_name = Neomate._get_model_info(model)
        
        has_nodename = (hasattr(model_class, "__nodename__") or 
                    (not isinstance(model, type) and hasattr(model, "__nodename__")))
        
        if not has_nodename:
            raise NodeAttrError(model_name, "__nodename__", "Neomate does not found __nodename__ in attrs")
        if not isinstance(model, type):
            model.check_types_by_annotations()

    def add(self, node):
        self._check_is_model(node)
        self._check_model_annotations(node)
        nodename = getattr(node, "__nodename__")
        params = vars(node)
        if params.get("__nodename__"):
            del params["__nodename__"]
        query = f"CREATE (node:{nodename}  {self._generate_params(params) })"
        self.logger.info(f'Generated query for adding {nodename}:\n{query}')
        NeoConnection.add_to_pool(nodename, params)
        self.logger.info(f"Successfully added {nodename} to pool")


    def _generate_params(self, params):
        if not params:
            return ""
        return "{" + ", ".join([f"{name}: ${name}" for name in params.keys()]) + "}"

    def add_all(self, node):
        pass


    def get(self, model):
        self._check_is_model(model)
        self._check_model_annotations(model)
        nodename = getattr(model, "__nodename__")
        return QueryBuilder(nodename=nodename, model=model)
    
    @sync_async_method
    async def commit(self):
        await NeoConnection.commit()


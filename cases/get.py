import sys
import os
from typing import List
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dataclasses import dataclass
from neo4j import GraphDatabase, AsyncGraphDatabase
from dotenv import load_dotenv
from neomate.neomate import Neomate
from neomate.BaseNode import BaseNode
load_dotenv()

driver = AsyncGraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", os.getenv("PASSWORD")))
session = driver.session()


@dataclass
class Person(BaseNode):
    name : str
    age : int
    gender : bool
    hobbies : List[str]
    __nodename__ : str = "Person"

neo = Neomate(driver=driver)
BaseNode.create_models()
async def main():
    builder = await neo.get(Person).where(Person.name == "John1").limit(20).run()
    print(builder)
import asyncio
asyncio.run(main())

# builder = neo.get(Person).where(Person.name == "John1").limit(20).run()
# print(builder)
from neo4j import  Driver, AsyncDriver
from neomate.logger import get_logger
from neomate.utils import sync_async_method
from collections import defaultdict

class NeoConnection:
    _driver = None
    _session = None
    _instance =None
    _pool = defaultdict(list)
    logger = get_logger()

    def __new__(cls, driver:Driver | AsyncDriver):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._driver = driver
            cls._session = driver.session()
        return cls._instance
    
    @classmethod
    def _get_session(cls):
        if not cls._session:
            cls._session = cls._driver.session()
        return cls._session
    
    @classmethod
    def _is_async(cls):
        return isinstance(cls._driver, AsyncDriver)

    @classmethod
    async def _async_run_query(cls, query, params=None, transaction_type = "read"):
        if params is None:
            params = {}
        if transaction_type not in ("read", "write"):
            cls.logger.error("transaction type must be read or write")
            raise ValueError(f"Invalid transaction_type: {transaction_type}")
        session = cls._get_session()
        async def transaction_work(tx):
            result = await tx.run(query, params)
            return await result.data()
        if transaction_type=="read":
            return await session.execute_read(transaction_work)
        return await session.execute_write(transaction_work)
    
    @classmethod
    def _sync_run_query(cls, query, params=None, transaction_type = "read"):
        if params is None:
            params = {}
        if transaction_type not in ("read", "write"):
            cls.logger.error("transaction type must be read or write")
            raise ValueError(f"Invalid transaction_type: {transaction_type}")
        session = cls._get_session()
        def transaction_work(tx):
            result = tx.run(query, params)
            return result.data()
        if transaction_type=="read":
            return session.execute_read(transaction_work)
        return session.execute_write(transaction_work)
    
    @classmethod
    @sync_async_method
    async def run_query(cls, query, params=None, transaction_type="read"):
        try:
            if cls._is_async():
                return await cls._async_run_query(query, params, transaction_type)
            return cls._sync_run_query(query, params, transaction_type)
        except Exception as e:
            cls.logger.error(f"Query failed: {query}, Error: {e}")
            raise

    @classmethod
    def add_to_pool(cls,nodename, params):
        cls._pool[nodename].append(params)


    @classmethod
    @sync_async_method
    async def commit(cls):
        for nodename, node_data in cls._pool.items():
            if not node_data:
                continue
            query = f"""
            UNWIND $nodes as node_data
            CREATE(node: {nodename})
            SET node = node_data"""
            await cls.run_query(query, {"nodes":node_data}, "write")

        cls._pool.clear()
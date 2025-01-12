
class BaseMigration:
    version = None
    description = None
    
    def __init__(self, neo_mate):
        self.neo_mate = neo_mate
    def up(self):
        raise NotImplementedError
    
    def down(self):
        raise NotImplementedError

class MigrationManager:
    def __init__(self, neo_mate):
        self.neo_mate = neo_mate
    def init_history(self):
        with self.neo_mate.trans() as tx:
            tx.run("""
                   MERGE (h:_MigrationHistory)
                   ON CREATE SET h.applied_migrations = []
                   """)
    def get_applied_migrations(self):
        
        with self.neo_mate.trans() as tx:
            result = tx.run("""
                   MATCH(h:_MigrationHistory)
                   RETURN h.applied_migrations as migrations
                   """)
            result = result.single()
            result = result.get('migrations', [])
            print(result)
            return result
    def record_migrations(self, version):
        with self.neo_mate.trans() as tx:
            result = tx.run("""
                   MATCH (h:_MigrationHistory)
                   SET h.applied_migrations = 
                   h.applied_migrations + $version
                   RETURN h as h
                   """,version = version)
            result = result.single()
            result = result.get('migrations', [])
            print(result)
            return result
from neomate.neomate.orm import Types
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

            return result
    def validate_schema(self):
        schema = self.neo_mate.base.__subclasses__()[0]
        # print("schema", vars(schema))
        
        new_schema = {k:v for k,v in vars(schema).items() if "__" not in k or k == "__nodename__"}
        old_schemas = self.get_schema()
        s = Types.from_dict(old_schemas[0])
        print(s)
        print(new_schema)
        validated_schema = {k:v for k,v in new_schema.items() if k not in s.keys() or v != s[k]}
        print(validated_schema)
        if validated_schema:
            print(new_schema)
            print(s)
            print("end")
        
    def get_schema(self):
        with self.neo_mate.trans() as tx:
            schema = tx.run("""
                            MATCH (schema:_Schema) - [:HAS_PROPERTY] -> (p:_Property)
                            RETURN schema, collect(p) as properties
                            """)
            result = [el for el in schema.data()]
        # print(result)
        return result

    def init_schemas(self):
        classes = self.neo_mate.base.__subclasses__()
        self.neo_mate.delete_all_nodes(type = '_Schema',delete_relationships = True)
        self.neo_mate.delete_all_nodes(type = '_Property',delete_relationships = True)

        for cls in classes:
            
            print(1)
            nodename = vars(cls).get("__nodename__", cls.__name__)
            
            # type = getattr((cls), "type")
            a = {k:v.__dict__ for k,v in vars(cls).items() if "__" not in k}
            print(a)
            properties =[ f"""{v.to_dict(k)} """ for k, v in vars(cls).items() if '__' not in k]
            # properties.append(f"""__nodename__: '{nodename}' """)
            with self.neo_mate.trans() as tx:
                tx.run(f"""
                       CREATE (p:_Schema {{ nodename: "{nodename}"}})
                       """)
            for prop in properties:
                print(f"""
                           CREATE (p:_Property{{{prop}}})
                           """)
                with self.neo_mate.trans() as tx:
 
                    tx.run(f"""
                    CREATE (p:_Property{{{prop}}})
                    WITH p
                    MATCH (s:_Schema)
                    WHERE s.nodename = "{nodename}"
                    CREATE (s)-[:HAS_PROPERTY]->(p)
                    """)
        
            # cypher_query = f"""CREATE (a:_Schema{{{properties}}})"""
            # cypher_query = f"""CREATE (a:_Schema{cls})"""
            # with self.neo_mate.trans() as tx:
            #     tx.run(cypher_query)
            # print(cypher_query)
        
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
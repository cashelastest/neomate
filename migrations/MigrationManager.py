from neomate.neomate.orm import Types
from neomate.logger.logger import Logger

logger = Logger().create_logger()
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
        schemas = self.neo_mate.base.__subclasses__()
        validated_results = []
        
        for schema in schemas:
            new_schema = {
                k: v for k, v in vars(schema).items() 
                if "__" not in k or k == "__nodename__"
            }
            
            old_schemas = self.get_schema()
            
            for old_schema in old_schemas:
                s = Types.from_dict(old_schema)
                validate_schema = {'creates':[],'changes':[],'deletes':[]}
                nodename = new_schema.get("__nodename__", s.get("___nodename__"))
                for key, value in new_schema.items():
                    if key == "__nodename__" and value != s.get('__nodename__'):
                        query = Types.set_nodename(s.get("__nodename__"), value)
                        
                        for q in query:
                            self.query_runner(query=q)
                        print(query)
                        nodename = value
                        validate_schema['__nodename__'] = nodename
                        logger.info(f"nodename changed from {s[key]} to {value}")
                        continue
                        
                    if key not in s.keys():
                        logger.info(f'Create new attribute {key}')
                        
                        
                        validate_schema["creates"].append((value, nodename, key))
                        continue
                        
                    if value != s[key]:
                        result = Types.compare_dicts(s[key].__dict__, value.__dict__)
                        for prop, val in result[1].items():
                            validate_schema['changes'].append((nodename,key,{prop:val}))
                            
                        logger.info(f"result is {result} for {key}")
                

                for key in s.keys():
                    if key not in new_schema.keys():
                        validate_schema['deletes'].append((nodename, key))
                        logger.info(f"deleting field {key}")
                
                if validate_schema:
                    validated_results.append({
                        'schema_name': schema.__name__,
                        'changes': validate_schema
                    })
                    print(f"Changes for {schema.__name__}:", validate_schema)
                    print("end")
        
        return validate_schema
            
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
    def query_runner(self,query):
        with self.neo_mate.trans() as tx:
            tx.run(query)
    def makemigrations(self):

        validated_schema = self.validate_schema()
        query =''
        for node in validated_schema['creates']:
            query = Types.create_node_attr(*node)
            self.query_runner(query)

            print("creating property \n", query)
        for node in validated_schema['deletes']:
            query = Types.delete_node_attr(*node)
            self.query_runner(query)
            print("deletes nodes \n", query)
        for node in validated_schema['changes']:
            for key,value in node[2].items():
                
                query = Types.add_prop_to_node_attr(node[0],node[1], (key,value))
                self.query_runner(query)

            
            print("creating attrs to ", query)
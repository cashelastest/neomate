class SchemaValidator():
    def __init__(self, neomate):
        self.neomate = neomate
    def get_data_from_migrations(self):
        query = """
    MATCH (p:_Migration)
    WITH p
    ORDER BY p.id DESC
    LIMIT 1
    MATCH (p)-[:HAS_SCHEMA]->(a:_Schema)
    MATCH (a)- [:HAS_PROPERTY] -> (b: _Property)
    RETURN a as schema, collect(b) as properties
        """
        with self.neomate.trans() as tx:
            res = tx.run(query)
            result = res.single()
        print(result['properties'][0])
        return result['properties']
    def validate_data(self, cls):
        print(cls)
        classes_items = cls.keys()
        migrated_properites = self.get_data_from_migrations()
        for property in migrated_properites:
            if not property['field_name'] in classes_items:
                return False
            class_item = cls[property['field_name']]
            
            if class_item.type in __builtins__.values():
                type = class_item.type.__name__ 
            else:
                type = str(class_item.type)
            if property['type'] != type:
                print('type doesnt match',property['type'], type)
                return False
            if class_item.is_must_have and not property['is_must_have']:
                print("noooo")
                return False
            return True
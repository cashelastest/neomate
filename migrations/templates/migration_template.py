"""
from neomate.migrations.MigrationManager import BaseMigration

class {classname}(BaseMigration):
    \"\"\"
    {description}
    \"\"\"
    version = "{version}"
    
    def up(self):
        query = \"\"\"
        {up_query}
        \"\"\"
        with self.neo_mate.trans() as tx:
            tx.run(query)
    
    def down(self):
        query = \"\"\"
        {down_query}
        \"\"\"
        with self.neo_mate.trans() as tx:
            tx.run(query)
"""
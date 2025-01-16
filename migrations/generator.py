import os
from datetime import datetime



class MigrationGenerator:
    def __init__(self):
        self.template_path = os.path.join(
            os.path.dirname(__file__),
            "templates",
            "migration_template.py"
        )
    def get_template(self):
        with open(self.template_path, "r") as file:
            return file.read()
    def create_migrations(self,name,description):
        timestamp = datetime.now().strftime("%d.%m.%Y_%H%M%S")
        classname = f"Migration_{name.title().replace(" ", "")}"
        template = self.get_template()
        content = template.format(
            classname=classname,
            description = description,
            version = timestamp,
            up_query = "// TODO: write ur migration",
            down_query = "// TODO: write ur down migration"
        )
        
        migrations_dir = os.path.join(os.getcwd(), "migrations","versions")
        os.makedirs(migrations_dir, exist_ok = True)
        
        filename = f"{timestamp}_{name.lower().replace(" ","_")}.py"
        filepath = os.path.join(migrations_dir,filename)
        with open(filepath, 'w') as file:
            file.write(content)
        return filename
from importlib import util
import click
import os
import sys
from neomate.migrations.generator import MigrationGenerator
from neomate.migrations.MigrationManager import MigrationManager
from neomate.logger.logger import Logger

logger = Logger().create_logger()
class SessionManager:
    _instance = None
    _neo_mate = None
    
    def __init__(self):
        if not SessionManager._instance:
            SessionManager._instance = self 
            self.manager = None
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = SessionManager()
        return cls._instance
        
    @classmethod
    def set_neo_mate(cls, neo_mate):
        cls._neo_mate = neo_mate
        instance = cls.get_instance()
        instance.manager = MigrationManager(neo_mate)
    
    @classmethod
    def get_neo_mate(cls):
        if cls._neo_mate:
            return cls._neo_mate
        
@click.group()
def cli():
    pass

@cli.command()
@click.argument("name")
@click.option('--description', '--desc', '-d', default = "")
def create(name, description):
    generator = MigrationGenerator()
    filename = generator.create_migrations(name=name,description=description)
    logger.info(f'created migration: {filename}')


@cli.command()
def migrate():
    versions_dir = os.path.join(os.getcwd(), "migrations", "versions")
    sys.path.append(os.getcwd())
    neo_mate = SessionManager.get_neo_mate()
    migration_files = sorted([el for el in os.listdir(versions_dir)
                            if el.endswith('.py') and el[0].isdigit()
                            ])
    manager = SessionManager.get_instance().manager
    manager.init_history()
    applied = manager.get_applied_migrations()
    
    for file in migration_files:
        file_path = os.path.join(versions_dir, file)
        spec = util.spec_from_file_location(file[:-3], file_path)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        migration_class = None
        for element in dir(module):
            
            if element.startswith("Migration_"):
                print(element)
                migration_class = getattr(module, element)
                break
            
        if not migration_class:
            continue
            
        migration = migration_class(neo_mate)
        print(migration)
        migration.up()
        if migration.version not in applied:
            print(file)
            
            manager.record_migrations(migration.version)
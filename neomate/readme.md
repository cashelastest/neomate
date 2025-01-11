# NeoMate

A lightweight and intuitive ORM for Neo4j in Python, providing type validation, relationship management, and elegant query building.

## Features

- Type validation system using dataclasses
- Transaction management with automatic rollback on errors
- Relationship creation and management
- Flexible node querying with AND/OR conditions
- Colored logging for better debugging
- Bulk node creation support
- Bidirectional relationship support
- Custom type validation

## Installation

```bash
pip install neomate
```

## Quick Start

```python
from neomate import NeoMate, Types
from neo4j import GraphDatabase

# Define your model
class Person:
    __nodename__ = "Person"  # Optional: customize node type name
    
    name = Types(str, is_must_have=True)
    age = Types(int, default=0)
    hobbies = Types(list, is_must_have=False)

# Connect to Neo4j
uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
session = driver.session()

# Initialize NeoMate
neo = NeoMate(session)

# Create a person
person = Person()
person.name = "Alex"
person.hobbies = ["programming", "music"]

# Save to database
neo.create_node(person)

# Query nodes
results = neo.get_node("Person", name="Alex")
```

## Type Validation

The `Types` class supports:
- Basic Python types (str, int, list, etc.)
- Custom classes
- Optional fields with `is_must_have=False`
- Default values
- Bidirectional relationships

```python
class User:
    name = Types(str, is_must_have=True)
    friend = Types("User", relate_name="FRIEND", bidiractional=True)
```

## Transaction Management

All database operations are automatically wrapped in transactions:

```python
# Automatic transaction management
neo.add_node("Person", name="John")

# Multiple nodes in single transaction
nodes = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30}
]
neo.add_nodes("Person", nodes)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Created by Alex

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="neomate",
    version="0.1.0",  
    author="MrRac",
    author_email="trew5804@gmail.com",
    description="Lightweight Neo4j ORM with type validation and relationship management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/neomate",
    packages=find_packages(exclude=['tests*']),
    

    install_requires=[
        "neo4j-driver>=4.4.0",  
        "colorlog>=6.7.0",   
        "dataclasses;python_version<'3.7'",  
    ],
    

    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-mock>=3.10.0',
            'black',  
            'flake8', 
        ],
    },
    

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Neo4j",
        "Typing :: Typed",
    ],
    
    python_requires=">=3.7",
 
    package_data={
        'neomate': ['py.typed', '*.pyi'],
    },

    project_urls={
        "Bug Tracker": "https://github.com/cashelastest/neomate/issues",
        "Documentation": "https://github.com/cashelastest/neomate#readme",
        "Source Code": "https://github.com/cashelastest/neomate",
    },
    
    keywords="neo4j, orm, database, graph database, type validation, relationship management",
)

    MATCH (p:_Migration)
    WITH p
    ORDER BY p.id DESC
    LIMIT 1
    MATCH (p)-[:HAS_PROPERTY]->(a:_Property)
    RETURN a
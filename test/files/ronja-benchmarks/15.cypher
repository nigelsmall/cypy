MATCH (admin:Administrator {name:{adminName}}),(resource:Resource {name:{resourceName}}) MATCH p=(admin)-[:MEMBER_OF]->()-[:ALLOWED_INHERIT]->(company)-[:WORKS_FOR|HAS_ACCOUNT]-(resource) WHERE NOT ((admin)-[:MEMBER_OF]->()-[:DENIED]->(company)) RETURN count(p) AS accessCount
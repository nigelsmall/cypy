/* Cypher test file
 *
 * This is a multi-line comment
 */

// Built-in constants, null checks and boolean operators
RETURN ((true OR false) AND ((NOT true XOR null) IS NULL)) IS NOT NULL;

// Integers, addition, subtraction and unary plus/minus
RETURN 0+12-34+-56-+78,
       0 + 12 - 34 + -56 - +78;

// Floating point numbers, multiplication, division, modulus and exponentiation
RETURN 0.0*1.23/2.34*-3.45/+4.56%7^8.9,
       0.0 * 1.23 / 2.34 * -3.45 / +4.56 % 7 ^ 8.9;

// Strings
RETURN
'first line
second line
third line', 'abc' + 'def',
'Abc \'Def\' "Xyz" Åäö', "Abc \"Def\" 'Xyz' Åäö",
'\\ \' \" \b \f \n \r \t \uABCD \U0001F644';

// Brackets and nesting
RETURN [1, [2.1, 2.2, 2.3], 3],
       [['one', 'eins'], ["two", 'zwei'], ['three', 'drei']],
       {one: 1,
        `number ``two```: (a {name: 'Alice'})-[:KNOWS {since: 1999}]->(b {name: 'Bob'}),
        `π`: 3.1415926,
        four: {en: 'four', de: 'vier'},
        five: [1, 2, 3, 4, 5],
        six: [(1 + 2), [3, 4], {e: 5, f: 6}]};

// Colons
MATCH (a:First {x: true})-[:AND]->(: Second),
      (:`The Third`)-[: AND {y:true}]->(: `The Fourth`)
SET a:Firth:Sixth
RETURN a, {b: count(*), c: ':', `d:e`: 'f'};

// Arrows
MATCH (a)--(b)->(c)<-(d)<->(e),
      (f) -- (g) -> (h) <- (i) <-> (j),
      (k)-[:Z]-(l)-[:Z]->(m)<-[:Z]-(n)<-[:Z]->(o),
      (p) -[:Z]- (q) -[:Z]-> (r) <-[:Z]- (s) <-[:Z]-> (t),
      (u) - [:Z] - (v) - [:Z] -> (w) <- [:Z] - (x) <- [:Z] -> (y)
RETURN a.x, b.y, c.z;

// Parameters
RETURN $value, $`other value`, $```slightly awkward`` value`;

// MATCH and WHERE
MATCH (n:Person)-[:KNOWS]->(m:Person)
WHERE n.name = 'Alice';
MATCH (n)-->(m);
MATCH (n {name: 'Alice'})-->(m);
MATCH p = (n)-->(m);
OPTIONAL MATCH (n)-[r]->(m);

// CREATE
CREATE (n {name: $value});
CREATE (n $map);
UNWIND $listOfMaps AS properties
CREATE (n) SET n = properties;
CREATE (n)-[r:KNOWS]->(m);
CREATE (n)-[:LOVES {since: $value}]->(m);

// SET
SET n.property1 = $value1,
    n.property2 = $value2;
SET n = $map;
SET n += $map;
SET n:Person;

// Import
LOAD CSV FROM
'https://neo4j.com/docs/cypher-refcard/3.2/csv/artists.csv' AS line
CREATE (:Artist {name: line[1], year: toInt(line[2])});
LOAD CSV WITH HEADERS FROM
'https://neo4j.com/docs/cypher-refcard/3.2/csv/artists-with-headers.csv' AS line
CREATE (:Artist {name: line.Name, year: toInt(line.Year)});
LOAD CSV FROM
'https://neo4j.com/docs/cypher-refcard/3.2/csv/artists-fieldterminator.csv'
AS line FIELDTERMINATOR ';'
CREATE (:Artist {name: line[1], year: toInt(line[2])});

// RETURN
RETURN *;
RETURN n AS columnName;
RETURN DISTINCT n;
RETURN n ORDER BY n.property;
RETURN n ORDER BY n.property ASC;
RETURN n ORDER BY n.property ASCENDING;
RETURN n ORDER BY n.property DESC;
RETURN n ORDER BY n.property DESCENDING;
RETURN n SKIP $skipNumber;
RETURN n LIMIT $limitNumber;
RETURN n SKIP $skipNumber LIMIT $limitNumber;
RETURN count(*);

// WITH
MATCH (user)-[:FRIEND]-(friend)
WHERE user.name = $name
WITH user, count(friend) AS friends
WHERE friends > 10
RETURN user;
MATCH (user)-[:FRIEND]-(friend)
WITH user, count(friend) AS friends
ORDER BY friends DESC
  SKIP 1
  LIMIT 3
RETURN user;

// UNION
MATCH (a)-[:KNOWS]->(b)
RETURN b.name
UNION
MATCH (a)-[:LOVES]->(b)
RETURN b.name;
MATCH (a)-[:KNOWS]->(b)
RETURN b.name
UNION ALL
MATCH (a)-[:LOVES]->(b)
RETURN b.name;

// MERGE
MERGE (n:Person {name: $value})
  ON CREATE SET n.created = timestamp()
  ON MATCH SET
    n.counter = coalesce(n.counter, 0) + 1,
    n.accessTime = timestamp();
MATCH (a:Person {name: $value1}),
      (b:Person {name: $value2})
MERGE (a)-[r:LOVES]->(b);
MATCH (a:Person {name: $value1})
MERGE
  (a)-[r:KNOWS]->(b:Person {name: $value3});

// DELETE
DELETE n, r;
DETACH DELETE n;
MATCH (n)
DETACH DELETE n;

// REMOVE
REMOVE n:Person;
REMOVE n.property;

// FOREACH
FOREACH (r IN relationships(path) |
  SET r.marked = true);
FOREACH (value IN coll |
 CREATE (:Person {name: value}));

// CALL and YIELD
CALL db.labels() YIELD label;
CALL java.stored.procedureWithArgs;
CALL db.labels() YIELD label
RETURN count(label) AS count;

// Patterns
MATCH (n:Person)
MATCH (n:Person:Swedish)
MATCH (n:Person {name: $value})
MATCH ()-[r {name: $value}]-()
MATCH (n)-->(m)
MATCH (n)--(m)
MATCH (n:Person)-->(m)
MATCH (m)<-[:KNOWS]-(n)
MATCH (n)-[:KNOWS|:LOVES]->(m)
MATCH (n)-[r]->(m)
MATCH (n)-[*1..5]->(m)
MATCH (n)-[*]->(m)
MATCH (n)-[:KNOWS]->(m {property: $value})
MATCH shortestPath((n1:Person)-[*..6]-(n2:Person))
MATCH allShortestPaths((n1:Person)-[*..6]->(n2:Person))
MATCH size((n)-->()-->())
RETURN *;

// Lists
RETURN ['a', 'b', 'c'] AS list;
RETURN size($list) AS len, $list[0] AS value;
RETURN range($firstNum, $lastNum, $step) AS list;
MATCH (a)-[r:KNOWS*]->()
RETURN r AS rels;
RETURN matchedNode.list[0] AS value,
       size(matchedNode.list) AS len;
RETURN list[$idx] AS value,
       list[$startIdx..$endIdx] AS slice;
UNWIND $names AS name
MATCH (n {name: name})
RETURN avg(n.age);
MATCH (a)
RETURN [(a)-->(b) WHERE b.name = 'Bob' | b.age];
MATCH (person)
RETURN person { .name, .age};

// INDEX
CREATE INDEX ON :Person(name);
MATCH (n:Person) WHERE n.name = $value;
MATCH (n:Person)
WHERE n.name IN [$value];
MATCH (n:Person)
USING INDEX n:Person(name)
WHERE n.name = $value;
DROP INDEX ON :Person(name);

// Labels
CREATE (n:Person {name: $value});
MERGE (n:Person {name: $value});
MATCH (n) SET n:Spouse:Parent:Employee;
MATCH (n:Person);
MATCH (n:Person) WHERE n.name = $value;
MATCH (n) WHERE (n:Person);
MATCH (n) RETURN labels(n);
MATCH (n) REMOVE n:Person;

// Maps
RETURN {name: 'Alice', age: 38,
        address: {city: 'London', residential: true}};
WITH {person: {name: 'Anne', age: 25}} AS p
RETURN p.person.name;
MERGE (p:Person {name: $map.name})
  ON CREATE SET p = $map;
MATCH (matchedNode:Person)
RETURN matchedNode;
RETURN $map.name, $map.age, $map.children[0]

// Predicates
MATCH (n) WHERE n.property <> $value;
MATCH (n) WHERE exists(n.property);
MATCH (n) WHERE n.number >= 1 AND n.number <= 10;
MATCH (n) WHERE 1 <= n.number <= 10;
MATCH (n) WHERE n:Person;
MATCH (n) WHERE variable IS NULL;
MATCH (n) WHERE NOT exists(n.property) OR n.property = $value;
MATCH (n) WHERE n.property = $value;
MATCH (n) WHERE n["property"] = $value;
MATCH (n) WHERE n.property STARTS WITH 'Tob' OR
                n.property ENDS WITH 'n' OR
                n.property CONTAINS 'goodie';
MATCH (n) WHERE n.property =~ 'Tob.*';
MATCH (n) WHERE (n)-[:KNOWS]->(m);
MATCH (n) WHERE NOT (n)-[:KNOWS]->(m)
MATCH (n) WHERE n.property IN [$value1, $value2];

// List Predicates
RETURN all(x IN $coll WHERE exists(x.property));
RETURN any(x IN $coll WHERE exists(x.property));
RETURN none(x IN $coll WHERE exists(x.property));
RETURN single(x IN $coll WHERE exists(x.property));

// List Expressions
RETURN size($list);
RETURN head($list), last($list), tail($list);
RETURN [x IN $list WHERE x.prop <> $value | x.prop];
RETURN extract(x IN $list | x.prop);
RETURN filter(x IN $list WHERE x.prop <> $value);
RETURN reduce(s = "", x IN $list | s + x.prop);

// CONSTRAINT
CREATE CONSTRAINT ON (p:Person)
       ASSERT p.name IS UNIQUE;
DROP CONSTRAINT ON (p:Person)
     ASSERT p.name IS UNIQUE;
CREATE CONSTRAINT ON (p:Person)
       ASSERT exists(p.name);
DROP CONSTRAINT ON (p:Person)
     ASSERT exists(p.name);
CREATE CONSTRAINT ON ()-[l:LIKED]-()
       ASSERT exists(l.when);
DROP CONSTRAINT ON ()-[l:LIKED]-()
     ASSERT exists(l.when);

// CASE
MATCH (n)
RETURN CASE n.eyes
 WHEN 'blue' THEN 1
 WHEN 'brown' THEN 2
 ELSE 3
END;
MATCH (n)
RETURN CASE
 WHEN n.eyes = 'blue' THEN 1
 WHEN n.age < 40 THEN 2
 ELSE 3
END;

// Functions
MATCH (n) RETURN coalesce(n.property, $defaultValue);
RETURN timestamp();
MATCH (n) RETURN id(n);
RETURN toInteger($expr);
RETURN toFloat($expr);
RETURN toBoolean($expr);
MATCH (n) RETURN keys(n);
MATCH (n) RETURN properties(n);

// Path Functions
MATCH path=(a)-[:TO]->(b) RETURN length(path);
MATCH path=(a)-[:TO]->(b) RETURN nodes(path);
MATCH path=(a)-[:TO]->(b) RETURN relationships(path);
MATCH path=(a)-[:TO]->(b) RETURN extract(x IN nodes(path) | x.prop);

// Spatial Functions
RETURN point({x: {x}, y: {y}});
RETURN distance(point({x: {x1}, y: {y1}}), point({x: {x2}, y: {y2}}));

// Aggregating Functions
RETURN count(*);
RETURN count(variable);
RETURN count(DISTINCT variable);
RETURN collect(n.property);
RETURN sum(n.property);
RETURN percentileDisc(n.property, $percentile);
RETURN stDev(n.property);

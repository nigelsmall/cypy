MATCH (a:Person) WHERE has(a.email) RETURN count(a)
from cypy import Graph, Node, Relationship


def main():
    g = Graph()
    a = Node(name="Alice")
    b = Node(name="Bob")
    c = Node(name="Carol")
    d = Node(name="Dave")
    ab = Relationship(a, "KNOWS", b)
    ac = Relationship(a, "LIKES", c)
    cb = Relationship(c, "DISLIKES", b)
    cd = Relationship(c, "MARRIED_TO", d)
    dd = Relationship(d, "WORKS_FOR", d)
    g |= ab | ac | cb | cd | dd
    for node in g.nodes():
        print(node)
    for relationship in g.relationships():
        print(relationship)


if __name__ == "__main__":
    main()

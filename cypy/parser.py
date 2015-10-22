#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from sys import argv
from parsimonious.grammar import Grammar


grammar = Grammar("""\
Query        = RegularQuery
RegularQuery = SingleQuery
SingleQuery  = (Clause _?)+
_            = ~"[ \\r\\n]+"
Clause       = Match
             / Create
             / Return

Identifier = ~"[A-Z 0-9 _?]*"i

Expression   = Disjunction
             / XDisjunction
             / Conjunction
             / Complement
             / Proposition

Disjunction  = XDisjunction (_? ~"OR"i _? XDisjunction)+
XDisjunction = Conjunction (_? ~"XOR"i _? Conjunction)+
Conjunction  = Proposition (_? ~"AND"i _? Proposition)+
Complement   = ~"NOT"i _? Proposition
Proposition  = Comparison
             / Arithmetic
             / Value

Comparison   = Equality
             / Inequality
             / LessThan
             / MoreThan
             / LessThanOrEqual
             / MoreThanOrEqual
Equality          = Arithmetic _? "=" _? Arithmetic
Inequality        = Arithmetic _? "<>" _? Arithmetic
LessThan          = Arithmetic _? "<" _? Arithmetic
MoreThan          = Arithmetic _? ">" _? Arithmetic
LessThanOrEqual   = Arithmetic _? "<=" _? Arithmetic
MoreThanOrEqual   = Arithmetic _? ">=" _? Arithmetic

Arithmetic        = SumOrDifference
                  / ProductOrQuotient
                  / Exponent
                  / Value
SumOrDifference   = Sum
                  / Difference
Sum               = ProductOrQuotient (_? "+" _? Arithmetic)+
Difference        = ProductOrQuotient _? "-" _? Arithmetic
ProductOrQuotient = Product
                  / Quotient
                  / Remainder
                  / Value
Product           = Exponent (_? "*" _? Arithmetic)+
Quotient          = Exponent _? "/" _? Arithmetic
Remainder         = Exponent _? "%" _? Arithmetic
Exponent          = Value _? "^" _? Arithmetic

Value             = Parenthetical
                  / Positive
                  / Negative
                  / MemberAccess
                  / Subscript
                  / Number
                  / StringLiteral
                  / Parameter
                  / IsNull
Parenthetical     = "(" _? Expression _? ")"
Positive          = "+" _? Expression
Negative          = "-" _? Expression
MemberAccess      = Identifier _? "." _? Identifier
Subscript         = Identifier _? "[" _? Expression _? "]"
Number            = Integer ("." Fraction)?
Integer           = ~"[0-9]+"
Fraction          = ~"\.[0-9]+"
StringLiteral     = '""'
Parameter         = "{" Identifier "}"
IsNull            = Expression ~"IS NULL"i

Pattern              = PatternPart (_? "," _? PatternPart)*
PatternPart          = (Identifier _? "=" _?)? AnonymousPatternPart
AnonymousPatternPart = PatternElement
PatternElement       = NodePattern (_? PatternElementChain)*
NodePattern          = ("(" Identifier? NodeLabels? _? Properties? ")")
                     / Identifier
NodeLabels           = (_? ":" _? Identifier)+
Properties           = "{" _? (Property (_? "," _? Property)*)? _? "}"
Property             = PropertyKey _? ":" _? PropertyValue
PropertyKey          = Identifier
PropertyValue        = Expression
RelationshipPattern  = (LeftArrowHead Dash+ _? RelationshipDetail? _? Dash+ RightArrowHead)
                     / (LeftArrowHead Dash+ _? RelationshipDetail? _? Dash+)
                     / (Dash+ _? RelationshipDetail? _? Dash+ RightArrowHead)
                     / (Dash+ _? RelationshipDetail? _? Dash+)
PatternElementChain  = RelationshipPattern _? NodePattern
LeftArrowHead        = "<"
Dash                 = "-"
RightArrowHead       = ">"
RelationshipDetail   = "[" Identifier? RelationshipTypes? "]"
RelationshipTypes    = ":" Identifier (_? "|" _? Identifier)*

Match        = (~"OPTIONAL MATCH"i _? Pattern (_? Where)?)
             / (~"MATCH"i _? Pattern (_? Where)?)
Where        = ~"WHERE"i _? Expression

Create       = (~"CREATE UNIQUE"i _? Pattern)
             / (~"CREATE"i _? Pattern)

Return       = (~"RETURN DISTINCT"i _? ReturnBody)
             / (~"RETURN"i _? ReturnBody)
ReturnBody   = ReturnItems (_? Order)? (_? Skip)? (_? Limit)?
ReturnItems  = Identifier
Order        = ~"ORDER BY"i
Skip         = ~"SKIP"i
Limit        = ~"LIMIT"i

""")


def main():
    script, args = argv[0], argv[1:]
    filename = args[0]
    with open(filename) as f:
        print(grammar.parse(f.read()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# CyPy: Cypher Framework for Python
# Copyright 2015 Nigel Small
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from sys import argv
from parsimonious.grammar import Grammar


grammar = Grammar("""\

Query        = RegularQuery
RegularQuery = SingleQuery
SingleQuery  = (Clause _?)*
Clause       = Match
             / Unwind
             / With
             / Return

_            = ~"\\s+"

Identifier = ~"[A-Z _][A-Z 0-9 _]*"i

Expression   = Expression12

Expression12 = Expression11 (_ ~"OR"i _ Expression11)*

Expression11 = Expression10 (_ ~"XOR"i _ Expression10)*

Expression10 = Expression9 (_ ~"AND"i _ Expression9)*

Expression9 = (~"NOT"i _ Expression9) / Expression8

Expression8 = eq
            / ne
            / lt
            / gt
            / lte
            / gte

eq  = Expression7 (_? "=" _? Expression7)*
ne  = Expression7 (_? "<>" _? Expression7)*
lt  = Expression7 (_? "<" _? Expression7)*
gt  = Expression7 (_? ">" _? Expression7)*
lte = Expression7 (_? "<=" _? Expression7)*
gte = Expression7 (_? ">=" _? Expression7)*

Expression7 = Add
            / Subtract
Add         = Expression6 (_? "+" _? Expression6)*
Subtract    = Expression6 (_? "-" _? Expression6)*

Expression6 = Multiply
            / Divide
            / Modulo
Multiply    = Expression5 (_? "*" _? Expression5)*
Divide      = Expression5 (_? "/" _? Expression5)*
Modulo      = Expression5 (_? "%" _? Expression5)*

Expression5 = Expression4 (_? "^" _? Expression4)*

Expression4   = Expression3
              / UnaryAdd
              / UnarySubtract
UnaryAdd      = "+" _? Expression4
UnarySubtract = "-" _? Expression4


Expression3 = ContainerIndex
            / CollectionSlice
            / RegexMatch
            / In
            / StartsWith
            / EndsWith
            / Contains
            / IsNull
            / IsNotNull
ContainerIndex  = Expression2 (_? "[" _? Expression _? "]")*
CollectionSlice = Expression2 (_? "[" _? Expression? _? ".." _? Expression? _? "]")*
RegexMatch      = Expression2 (_? "=~" _? Expression2)*
In              = Expression2 (_? ~"IN"i _? Expression2)*
StartsWith      = Expression2 (_? ~"STARTS\\s+WITH"i _? Expression2)*
EndsWith        = Expression2 (_? ~"ENDS\\s+WITH"i _? Expression2)*
Contains        = Expression2 (_? ~"CONTAINS"i _? Expression2)*
IsNull          = Expression2 (_? ~"IS\\s+NULL"i)*
IsNotNull       = Expression2 (_? ~"IS\\s+NOT\\s+NULL"i)*

Expression2     = Expression1 (_? "." _? PropertyKey)*

Expression1     = Number
                / StringLiteral
                / Parameter
                / Parenthetical
                / Identifier
Number          = Integer ("." Fraction)?
Integer         = ~"[0-9]+"
Fraction        = ~"\.[0-9]+"
StringLiteral   = '""'
Parameter       = "{" Identifier "}"
Parenthetical   = "(" _? Expression _? ")"

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

Match        = (~"OPTIONAL\\s+MATCH"i / ~"MATCH"i) _? Pattern _? Where?
Where        = ~"WHERE"i _? Expression

Unwind       = ~"UNWIND"i

With         = ~"WITH"i

Return       = (~"RETURN\\s+DISTINCT"i / ~"RETURN"i) _ ReturnBody
ReturnBody   = ReturnItems (_ Order)? (_ Skip)? (_ Limit)?
ReturnItems  = ReturnItem (_? "," _? ReturnItem)*
ReturnItem   = Expression (_ ~"AS"i _ Identifier)?
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

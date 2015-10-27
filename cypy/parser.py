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

EXPRESSION_GRAMMAR = """\
Expression     = Disjunction

Disjunction    = XDisjunction (_? ~"OR"i _? XDisjunction)*
XDisjunction   = Conjunction (_? ~"XOR"i _? Conjunction)*
Conjunction    = Proposition (_? ~"AND"i _? Proposition)*
Complement     = ~"NOT"i _? Proposition
Proposition    = Complement
               / Comparison

Comparison     = Equality
               / Inequality
               / LtComparison
               / GtComparison
               / LteComparison
               / GteComparison
               / SumOrDiff

Equality       = SumOrDiff _? "=" _? SumOrDiff
Inequality     = SumOrDiff _? "<>" _? SumOrDiff
LtComparison   = SumOrDiff _? "<" _? SumOrDiff
GtComparison   = SumOrDiff _? ">" _? SumOrDiff
LteComparison  = SumOrDiff _? "<=" _? SumOrDiff
GteComparison  = SumOrDiff _? ">=" _? SumOrDiff

SumOrDiff      = Sum
               / Difference
               / ProdOrQuot
Sum            = ProdOrQuot (_? "+" _? ProdOrQuot)+
Difference     = ProdOrQuot _? "-" _? ProdOrQuot

ProdOrQuot     = Product
               / Quotient
               / Remainder
               / Exponent
Product        = Exponent (_? "*" _? Exponent)+
Quotient       = Exponent _? "/" _? Exponent
Remainder      = Exponent _? "%" _? Exponent

Exponent       = UnaryOperation (_? "^" _? UnaryOperation)?

UnaryOperation = UnaryAdd
               / UnarySubtract
               / Expression3
UnaryAdd       = "+" _? UnaryOperation
UnarySubtract  = "-" _? UnaryOperation


Expression3 = ContainerIndex
            / CollectionSlice
            / RegexMatch
            / In
            / StartsWith
            / EndsWith
            / Contains
            / IsNull
            / IsNotNull
            / Expression2
ContainerIndex  = Expression2 _? "[" _? Expression _? "]"
CollectionSlice = Expression2 _? "[" _? Expression? _? ".." _? Expression? _? "]"
RegexMatch      = Expression2 _? "=~" _? Expression2
In              = Expression2 _? ~"IN"i _? Expression2
StartsWith      = Expression2 _? ~"STARTS\\s+WITH"i _? Expression2
EndsWith        = Expression2 _? ~"ENDS\\s+WITH"i _? Expression2
Contains        = Expression2 _? ~"CONTAINS"i _? Expression2
IsNull          = Expression2 _? ~"IS\\s+NULL"i
IsNotNull       = Expression2 _? ~"IS\\s+NOT\\s+NULL"i

Expression2     = PropertyLookup
                / Expression1
PropertyLookup  = Expression1 _? "." _? PropertyKey

Expression1     = Number
                / StringLiteral
                / Parameter
                / Parenthetical
                / FunctionCall
                / Identifier
Number          = Integer Fraction?
Integer         = ~"[0-9]+"
Fraction        = ~"\.[0-9]+"
StringLiteral   = SingleQuotedString / DoubleQuotedString
SingleQuotedString = "'" ~"[^']*" "'"
DoubleQuotedString = "\\"" ~"[^\\"]*" "\\""
Parameter       = "{" Identifier "}"
Parenthetical   = "(" _? Expression _? ")"
FunctionCall    = Identifier _? "(" ~"DISTINCT"i? (_? Expression (_? "," _? Expression)*)? _? ")"
"""

PATTERN_GRAMMAR = """\
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
RelationshipPattern  = (~"<-+" _? RelationshipDetail? _? ~"-+>")
                     / (~"<-+" _? RelationshipDetail? _? ~"-+")
                     / (~"-+" _? RelationshipDetail? _? ~"-+>")
                     / (~"-+" _? RelationshipDetail? _? ~"-+")
PatternElementChain  = RelationshipPattern _? NodePattern
RelationshipDetail   = "[" Identifier? RelationshipTypes? "]"
RelationshipTypes    = ":" Identifier (_? "|" _? Identifier)*
"""

READ_ONLY_QUERY_GRAMMAR = """\
ReadOnlyClause = Match
               / Unwind
               / With
               / Return

Match        = (~"OPTIONAL\\s+MATCH"i / ~"MATCH"i) _ Pattern (_ Where)?
Where        = ~"WHERE"i _ Expression

Unwind       = ~"UNWIND"i

With         = (~"WITH\\s+DISTINCT"i / ~"WITH"i) _ ReturnBody

Return       = (~"RETURN\\s+DISTINCT"i / ~"RETURN"i) _ ReturnBody
ReturnBody   = ReturnItems (_ Order)? (_ Skip)? (_ Limit)?
ReturnItems  = ReturnItem (_? "," _? ReturnItem)*
ReturnItem   = Expression (_ ~"AS"i _ Identifier)?
Order        = ~"ORDER\\s+BY"i _? Expression _? (~"ASC"i / ~"DESC"i)?
Skip         = ~"SKIP"i _? Expression
Limit        = ~"LIMIT"i _? Expression
"""

CORE_GRAMMAR = """\
_              = ~"\\s+"
Identifier     = ~"[A-Z_][0-9A-Z_]*"i
"""


grammar = Grammar("""\
Query          = RegularQuery
RegularQuery   = SingleQuery
SingleQuery    = (Clause _?)* ";"?
Clause         = ReadOnlyClause

""" + "\n\n".join([
    READ_ONLY_QUERY_GRAMMAR,
    EXPRESSION_GRAMMAR,
    PATTERN_GRAMMAR,
    CORE_GRAMMAR,
]))


def main():
    script, args = argv[0], argv[1:]
    filename = args[0]
    with open(filename) as f:
        print(grammar.parse(f.read()))


if __name__ == "__main__":
    main()

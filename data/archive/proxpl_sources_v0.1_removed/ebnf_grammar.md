# ProXPL Formal EBNF Grammar & Lexical Specification

## 1. Lexical Grammar & Tokens

### 1.1 Lexical Rules
ProXPL source code is encoded in UTF-8. Comments follow standard line `//` and block `/* ... */` syntax.

```ebnf
Letter          = "a" ... "z" | "A" ... "Z" | "_" | UnicodeLetter ;
DecimalDigit    = "0" ... "9" ;
HexDigit        = DecimalDigit | "a" ... "f" | "A" ... "F" ;
OctalDigit      = "0" ... "7" ;
BinaryDigit     = "0" | "1" ;

Identifier      = Letter { Letter | DecimalDigit } ;
IntegerLiteral  = DecimalDigit { DecimalDigit }
                | "0x" HexDigit { HexDigit }
                | "0o" OctalDigit { OctalDigit }
                | "0b" BinaryDigit { BinaryDigit } ;

FloatLiteral    = DecimalDigit { DecimalDigit } "." DecimalDigit { DecimalDigit } [ Exponent ] ;
Exponent        = ( "e" | "E" ) [ "+" | "-" ] DecimalDigit { DecimalDigit } ;
StringLiteral   = '"' { UnescapedChar | EscapedSeq } '"' ;
RawString       = 'r"' { AnyChar } '"' ;
```

### 1.2 Keywords & Symbols
Keywords reserved by the ProXPL grammar:
`fn`, `let`, `mut`, `const`, `struct`, `enum`, `trait`, `impl`, `type`, `async`, `await`, `spawn`, `channel`, `match`, `if`, `else`, `while`, `for`, `in`, `return`, `defer`, `pub`, `use`, `unsafe`, `tensor`, `as`, `where`, `break`, `continue`, `self`, `Self`.

Operator Precedence (Highest to Lowest):
1. Field access (`.`), Call (`()`), Index (`[]`)
2. Unary prefix (`!`, `-`, `&`, `&mut`, `*`)
3. Type casting (`as`)
4. Multiplicative (`*`, `/`, `%`)
5. Additive (`+`, `-`)
6. Bitwise Shift (`<<`, `>>`)
7. Bitwise AND (`&`)
8. Bitwise XOR (`^`)
9. Bitwise OR (`|`)
10. Comparison (`==`, `!=`, `<`, `<=`, `>`, `>=`)
11. Logical AND (`&&`)
12. Logical OR (`||`)
13. Assignment (`=`, `+=`, `-=`, `*=`, `/=`)

## 2. Syntactic EBNF Grammar

```ebnf
SourceFile      = { ModuleItem } ;

ModuleItem      = [ "pub" ] ( FunctionDecl | StructDecl | EnumDecl | TraitDecl | ImplBlock | TypeAlias | UseDecl ) ;

UseDecl         = "use" Path [ "::" ( "*" | "{" IdentifierList "}" ) ] ";" ;

FunctionDecl    = [ "async" ] "fn" Identifier [ Generics ] "(" [ ParameterList ] ")" [ "->" Type ] Block ;

ParameterList   = Parameter { "," Parameter } [ "," ] ;
Parameter       = [ "mut" ] Identifier ":" Type ;

StructDecl      = "struct" Identifier [ Generics ] "{" { StructField } "}" ;
StructField     = [ "pub" ] Identifier ":" Type ";" ;

EnumDecl        = "enum" Identifier [ Generics ] "{" { EnumVariant } "}" ;
EnumVariant     = Identifier [ TupleFields | StructFields ] ;

TraitDecl       = "trait" Identifier [ Generics ] "{" { TraitItem } "}" ;
ImplBlock       = "impl" [ Generics ] [ Identifier "for" ] Type "{" { ImplItem } "}" ;

Block           = "{" { Statement } [ Expression ] "}" ;

Statement       = LetStmt | DeferStmt | AssignmentStmt | ExprStmt ;

LetStmt         = "let" [ "mut" ] Identifier [ ":" Type ] "=" Expression ";" ;
DeferStmt       = "defer" Expression ";" ;
AssignmentStmt = Expression AssignOp Expression ";" ;

Expression      = PrimaryExpr | BinaryExpr | UnaryExpr | MatchExpr | IfExpr | AsyncBlock | TensorExpr ;

TensorExpr      = "tensor" "<" Type "," ShapeSpec ">" "::" Identifier "(" [ ExpressionList ] ")" ;
MatchExpr       = "match" Expression "{" { MatchArm } "}" ;
MatchArm        = Pattern "=>" Expression ";" ;
IfExpr          = "if" Expression Block [ "else" ( Block | IfExpr ) ] ;
AsyncBlock      = "async" Block ;
```

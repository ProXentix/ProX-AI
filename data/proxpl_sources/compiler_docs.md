# ProXPL Compiler & Toolchain Architecture (`proxc`)

The ProXPL compiler (`proxc`) is a high-performance modular multi-stage compilation framework designed for static analysis, type inference, tensor IR lowering, and vectorization.

## 1. Compiler Pipeline Stages

```text
Source Code (.prox / .proxpl)
             │
             ▼
      Lexer & Parser
             │
             ▼
  Abstract Syntax Tree (AST)
             │
             ▼
  High-Level IR (H-IR) ──► Type Checker & Linear Borrow Checker
             │
             ▼
 Tensor & Async Lowering ──► LLVM IR / CUDA PTX Codegen
             │
             ▼
 Native Machine Code / GPU Binary (.so / .cubin)
```

## 2. Abstract Syntax Tree (AST) Specification

The ProXPL AST is represented via strongly typed immutable data structures:

```proxpl
pub enum Expr {
    Literal(LiteralValue),
    Identifier(Symbol),
    TensorAllocation { shape: Vec<usize>, dtype: DType },
    FunctionCall { name: Symbol, args: Vec<Expr> },
    AsyncBlock { body: Vec<Stmt> },
    MatchExpr { target: Box<Expr>, arms: Vec<MatchArm> },
}

pub enum Stmt {
    LetBinding { name: Symbol, mutable: bool, type_annotation: Option<Type>, init: Expr },
    Assignment { target: Expr, value: Expr },
    DeferAction { action: Expr },
    ReturnStmt(Option<Expr>),
}
```

## 3. Type System & Inference Rules

ProXPL uses Hindley-Milner type inference extended with const-generics and tensor-shape unification:

$$\frac{\Gamma \vdash e_1 : \text{tensor}\langle T, [M, K]\rangle \quad \Gamma \vdash e_2 : \text{tensor}\langle T, [K, N]\rangle}{\Gamma \vdash \text{matmul}(e_1, e_2) : \text{tensor}\langle T, [M, N]\rangle}$$

## 4. Compiler CLI Options (`proxc`)

- `--emit=llvm-ir`: Emits human-readable LLVM IR text files.
- `--emit=ptx`: Emits CUDA PTX kernel assembly files.
- `-O3`: Enables vectorization, tensor-core fusion, and loop unrolling.
- `--check-borrow`: Executes strict affine linear type analysis.

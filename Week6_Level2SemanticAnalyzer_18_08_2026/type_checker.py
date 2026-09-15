"""
Week 6 - Semantic Analysis (Type Checker)

Walks the AST, reports semantic errors with line numbers,
and inserts Cast nodes for implicit conversions.
"""

from SymbolTable import DataType
from ast_nodes import Var, Const, Assign, BinOp, RelOp, Cast, Ternary, Print
from type_rules import is_numeric, promote, SemanticError


class TypeChecker:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.errors = []

    def error(self, message, lineno):
        self.errors.append(SemanticError(message, lineno))

    def check(self, stmts):
        """Type check a list of statements."""
        new_stmts = []

        for stmt in stmts:
            new_stmt = self.check_stmt(stmt)
            new_stmts.append(new_stmt)

        return new_stmts

    def check_stmt(self, stmt):
        if isinstance(stmt, Assign):
            return self.check_assign_stmt(stmt)

        elif isinstance(stmt, Print):
            stmt.expr, _ = self.check_expr(stmt.expr)
            return stmt

        return stmt

    def check_assign_stmt(self, stmt):
        stmt.var, left_type = self.check_var(stmt.var)
        stmt.expr, right_type = self.check_expr(stmt.expr)

        if left_type != right_type:
            if is_numeric(left_type) and is_numeric(right_type):
                stmt.expr = Cast(
                    left_type,
                    stmt.expr,
                    lineno=stmt.expr.lineno
                )
            else:
                self.error(
                    f"cannot assign {right_type} to {left_type}",
                    stmt.lineno,
                )

        return stmt

    def check_expr(self, node):
        if isinstance(node, Const):
            return node, node.type

        if isinstance(node, Var):
            return self.check_var(node)

        if isinstance(node, BinOp):
            return self.check_binop(node)

        if isinstance(node, RelOp):
            return self.check_relop(node)

        if isinstance(node, Cast):
            return self.check_cast(node)

        if isinstance(node, Ternary):
            return self.check_ternary(node)

        return node, DataType.INT

    def check_var(self, node):
        entry = self.symbol_table.getSymbol(node.name)

        if entry is None:
            self.error(
                f"undeclared variable '{node.name}'",
                node.lineno
            )
            return node, DataType.INT

        return node, entry.getDataType()

    def check_binop(self, node):
        node.left, left_type = self.check_expr(node.left)
        node.right, right_type = self.check_expr(node.right)

        if not is_numeric(left_type) or not is_numeric(right_type):
            self.error("invalid arithmetic operands", node.lineno)
            return node, DataType.INT

        result_type = promote(left_type, right_type)

        if left_type != result_type:
            node.left = Cast(
                result_type,
                node.left,
                lineno=node.left.lineno
            )

        if right_type != result_type:
            node.right = Cast(
                result_type,
                node.right,
                lineno=node.right.lineno
            )

        return node, result_type

    def check_relop(self, node):
        node.left, left_type = self.check_expr(node.left)
        node.right, right_type = self.check_expr(node.right)

        if not is_numeric(left_type) or not is_numeric(right_type):
            self.error("invalid comparison", node.lineno)
            return node, DataType.INT

        result_type = promote(left_type, right_type)

        if left_type != result_type:
            node.left = Cast(
                result_type,
                node.left,
                lineno=node.left.lineno
            )

        if right_type != result_type:
            node.right = Cast(
                result_type,
                node.right,
                lineno=node.right.lineno
            )

        return node, DataType.INT

    def check_ternary(self, node):
        node.cond, _ = self.check_expr(node.cond)
        node.then_expr, then_type = self.check_expr(node.then_expr)
        node.else_expr, else_type = self.check_expr(node.else_expr)

        if then_type == else_type:
            return node, then_type

        if is_numeric(then_type) and is_numeric(else_type):
            result = promote(then_type, else_type)

            if then_type != result:
                node.then_expr = Cast(
                    result,
                    node.then_expr,
                    lineno=node.then_expr.lineno,
                )

            if else_type != result:
                node.else_expr = Cast(
                    result,
                    node.else_expr,
                    lineno=node.else_expr.lineno,
                )

            return node, result

        self.error("incompatible ternary branches", node.lineno)
        return node, then_type

    def check_cast(self, node):
        node.expr, expr_type = self.check_expr(node.expr)

        if node.target_type == DataType.STRING:
            self.error("invalid cast", node.lineno)
            return node, DataType.STRING

        if not is_numeric(expr_type):
            self.error("invalid cast", node.lineno)

        return node, node.target_type


def check_program(program):
    errors = []

    for function in program.getFunctions():
        checker = TypeChecker(function.getLocalSymbolTable())

        checked_stmts = checker.check(
            function.getStatementsAstList()
        )

        function.setStatementsAstList(checked_stmts)

        errors.extend(checker.errors)

    return errors


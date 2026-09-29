"""
TinyCStr Level 1 Parser (Stages 1a -> 1b)

Read docs/grammar_ast_reference.md and docs/sly_parser_cheatsheet.md
before editing this file.

Fill in the TODOs in order: finish every Stage 1a TODO before starting Stage 1b.

Reminder (see docs/grammar_ast_reference.md): a `decl` statement builds
NO AST node. It only adds a SymbolTableEntry to the current function's
local SymbolTable. 
"""
from sly import Parser

from tinycstr_lexer import TinyCStrLexer
from ast_nodes import Num, Var, Assign, Print, BinOp
from SymbolTable import SymbolTableEntry, DataType
from Function import Function
from Program import Program


class TinyCStrParser(Parser):
    tokens = TinyCStrLexer.tokens

    # TODO(week-3, stage-1b): precedence table. Do NOT add this until
    # Stage 1a is fully working. Read docs/sly_parser_help.md ##1
    # before filling this in -- the tuple's ORDER matters and it is the
    # opposite of what most people guess.
    precedence = (
        ('left',PLUS,MINUS),
        ('left',TIMES,DIVIDE,REMAINDER),
    )

    def __init__(self):
        self.had_error = False

    # ------------------------------------------------------------------
    # Stage 1a: program / function / statement structure
    # ------------------------------------------------------------------
    # TODO(week-3, stage-1a): program -> func_def
    # Build a Program(), addFunction(p.func) to it, return the
    # Program. This is the grammar's start symbol -- parser.parse(...)
    # returns whatever this rule returns.
    #
    @_('func_def')
    def program(self, value):
        p=Program()
        p.addFunction(value[0])
        return p

    # TODO(week-3, stage-1a): 
    # func_def -> INT ID LPAREN RPAREN LBRACE decl_stmt_list stmt_list RBRACE
    # Build Function(DataType.INT, ID.name). return type and name 
    # decl_stmt_list is a list of decls it gives symbol table. 
    # stmt_list is a list of stmts it gives ast_list.
    @_('INT ID LPAREN RPAREN LBRACE decl_stmt_list stmt_list RBRACE')
    def func_def(self, value):
        f=Function(value[0],value[1])
        for symbol_entry in value[5]:
            f.localSymbolTable.addSymbol(symbol_entry)
        f.setStatementsAstList(value[6])
        return f


    # TODO(week-3, stage-1a): decl_stmt_list -> decl_stmt_list decl | empty
    # Build a flat Python list by appending each stmt (SymbolTableEntry)
    # onto the list accumulated so far.
    #
    @_('decl_stmt_list decl')
    def decl_stmt_list(self, value):
        return value[0]+value[1]
    #
    @_('empty')
    def decl_stmt_list(self, value):
        return []
    #
    @_('')
    def empty(self, value):
        pass


    # TODO(week-3, stage-1a): decl -> INT id_list SEMICOLON
    # p.id_list is a list of names (see id_list below). For each name,
    # build a SymbolTableEntry(name, DataType.INT). Return a LIST of
    # these entries (not a single one, since `int a,b,c;` declares three).
    #
    @_('INT id_list SEMICOLON')
    def decl(self, value):
        Symbol_entry_list=[]
        for name in value[1]:
            Symbol_entry_list.append(SymbolTableEntry(name,value[0]))
            return Symbol_entry_list
    
    # TODO(week-3, stage-1a): id_list -> id_list COMMA ID | ID
    # Build a flat Python list of name strings.
    @_('id_list COMMA ID')
    def id_list(self,value):
        return value[0]+[value[2]]
    @_("ID")
    def id_list(self,value):
        return [value[0]]
    
    # TODO(week-3, stage-1a): stmt_list -> stmt_list stmt | empty
    # Build a flat Python list by appending each AST node 
    # (Assign/Print) onto the list accumulated so far.
    #
    @_('stmt_list stmt')
    def stmt_list(self, value):
        return value[0]+[value[1]]
    #
    @_('empty')
    def stmt_list(self, value):
        return []
    #
    # @_('')
    # def empty(self, p):
    #     pass




    # TODO(week-3, stage-1a): stmt -> assign | print_stmt
    # (two separate @_(...) rules, each just returning ast of assign
    # / print_stmt respectively 
    @_('assign')
    def stmt(self,value):
        return value[0]

    @_('print_stmt')
    def stmt(self,value):
        return value[0]

    
    # TODO(week-3, stage-1a): assign -> ID ASSIGN expr SEMICOLON
    # Build Assign(Var(p.ID), p.expr).
    #
    @_('ID ASSIGN expr SEMICOLON')
    def assign(self, value):
        return Assign(Var(value[0]),value[2])

    # TODO(week-3, stage-1a): print_stmt -> PRINT expr SEMICOLON
    # Build Print(p.expr).
    #
    @_('PRINT expr SEMICOLON')
    def print_stmt(self, value):
        return Print(value[1])

    # TODO(week-3, stage-1a): expr -> NUMBER | ID
    # NUMBER -> Num(int(p.NUMBER)), ID -> Var(p.ID). No arithmetic yet --
    # that's all of Stage 1b below.
    #
    @_('NUMBER')
    def expr(self, value):
        return Num(value[0])
    #
    @_('ID')
    def expr(self, value):
        return Var(value[0])

    # ------------------------------------------------------------------
    # Stage 1b: arithmetic expressions.
    # Do not start this section until every Stage 1a golden AST test
    # passes.
    # ------------------------------------------------------------------
    # TODO(week-3, stage-1b): add the precedence table above FIRST.
    # Then extend expr with + - * / and parentheses, building BinOp
    # nodes. Run with SLY's debug log on (docs/sly_parser_cheatsheet.md
    # #4) to see the shift-reduce conflicts actually being resolved --
    # the lab plan explicitly asks you to look at this, not just trust
    # that it worked.
    #
    @_('expr PLUS expr')
    def expr(self, value):
        return BinOp('+', value[0],value[2])

    @_('expr MINUS expr')
    def expr(self, value):
        return BinOp('-', value[0],value[2])

    @_('expr TIMES expr')
    def expr(self, value):
        return BinOp('*', value[0],value[2])

    @_('expr DIVIDE expr')
    def expr(self, value):
        return BinOp('/', value[0],value[2])

    @_('expr REMAINDER expr')
    def expr(self, value):
        return BinOp('%', value[0],value[2])

    @_('LPAREN expr RPAREN')
    def expr(self, value):
        return value[1]
    # (MINUS, TIMES, DIVIDE similarly; LPAREN expr RPAREN just returns
    # the inner expr unchanged -- parentheses don't need their own node)

    def error(self, token):
        """
        TODO(week-3, stage-1a): report a syntax error. Set
        self.had_error = True (main.py's -parse stage checks this), 
        and print a message to stderr including the offending token's value
        and line number if `token` is not None (a None token means the
        error was at end-of-input). 
        Keep this simple for Level 1 --
        structured error recovery is not required this week.
        """
        #raise NotImplementedError("implement TinyCStrParser.error()")
        self.had_error=True
        print(f"Syntax error at {token.value} in the number{token.lineno}")


if __name__ == '__main__':
    from ast_nodes import pretty

    sample = "int main(){\n  int a;\n  a = 5;\nb=10;\nc=5;\n d=17;\ne=15;f=a+b-c/d*e;\n print f;\n}\n"
    lexer = TinyCStrLexer()
    parser = TinyCStrParser()
    program = parser.parse(lexer.tokenize(sample))
    for func in program.getFunctions():
        print(f"Function {func.getName()}")
        for stmt in func.getStatementsAstList():
            print(pretty(stmt, indent=1))

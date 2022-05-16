import compiler
from compiler.ast import Const
from compiler.ast import Name
from compiler.ast import AssName
from compiler.ast import Node
from compiler.ast import Stmt
from compiler.ast import Assign
from compiler.ast import CallFunc
from compiler.ast import IfExp
from compiler.ast import And
from compiler.ast import Or
from compiler.ast import Subscript
from explicate import InjectFrom
from compiler.ast import Break
from compiler.ast import While
from compiler.ast import If
from closure import GetFunPtr, GetFreeVars, CreateClosure
import utils


class FlattenVisitor(compiler.visitor.ASTVisitor):
    '''
    Visitor class to walk the ast and flatten it
    '''

    def __init__(self):
        self.env = {}
        self.flattened_stmts = []
        self.indent = 0
        self.stack_offset = 0
        self.stack_offset_map = {}

    def get_ast(self):
        '''
        Return the flattened ast
        return: the flattened ast
        '''
        prog = ""
        for stmt in self.flattened_stmts:
            prog += stmt + "\n"
        return compiler.parse(prog)

    def rvalue(self, lval):
        '''
        Return the right hand side of an assignment given the left hand side
        param: lval: the left hand side of an assignment
        return: the right hand side of an assignment, or None if not found
        '''
        return self.env.get(lval)

    def lvalue(self, rval):
        '''
        Return the left hand side of an assignment given the right hand side
        param: rval: the right hand side of an assignment
        return: the left hand side of an assignment, or None if not found
        '''
        for lval in self.env.keys():
            if self.rvalue(lval) == rval:
                return lval
        return None

    def add_stmt(self, stmt):
        '''
        Add a statement to the flattened list of statements.
        Also indent the statement based the current indentation level in self.indent
        param: stmt: the statement(s) to add
        return: No return value
        '''
        if isinstance(stmt, list):
            for s in stmt:
                s = " " * self.indent + str(s)
                self.flattened_stmts.append(s)
        else:
            s = " " * self.indent + str(stmt)
            self.flattened_stmts.append(s)

    def visitStmt(self, node):
        '''
        Visits a Stmt node and flattens it. This could come from a Module node, 
        or an IfExp inside a Let node because of the boxing and unboxing.
        param: node: the Stmt node to visit
        return: list of flattened statements from the immediate ancestor of Stmt
        '''
        stmts = []
        for child in node.nodes:
            stmt = self.visit(child)
            stmts.append(stmt)
            # If the child_stmt is an inject_from, don't add it to the flattened_stmts
            # because it is already in the flattened_stmts of the ancestor.
            # This is a temporary fix, need a better, more consistent solution
            # if not isinstance(child, InjectFrom):
            self.add_stmt(stmt)
        self.flattened_stmts = utils.flatten_list(self.flattened_stmts)
        return utils.flatten_list(stmts)

    def visitPrintnl(self, node):
        '''
        Visits a Printnl node and flattens it. Can only come from a Stmt node.
        param: node: the Printnl node to visit
        return: Flattened Print expression to Stmt
        '''
        expr = "print("
        for child in node.nodes:
            expr += str(self.visit(child)) + ","
        expr = expr[:-1] + ")"
        # self.add_stmt(expr)
        return expr

    def visitAssign(self, node):
        '''
        Visits an Assign node and flattens it. 
        This could come any node except a Module node, a Const node, an AssName node or a Name node
        param: node: the Assign node to visit
        return: Flattened assignment
        '''
        assignment = ""
        for child in node.nodes:
            lval = self.visit(child)
            rval = self.visit(node.expr)
            assignment = str(lval) + " = " + str(rval)
            if (isinstance(child, Subscript)):
                # if the lval is a subscript, then assign back the lval to the subscript
                var = self.visit(child.expr)
                index = self.visit(child.subs[0])
                self.add_stmt(assignment)
                rval = lval
                lval = str(var) + "[" + str(index) + "]"
                assignment = self.visit(
                    Assign([AssName(lval, "OP_ASSIGN")], Name(rval)))
            self.env[lval] = rval
            self.stack_offset += 4
            self.stack_offset_map[lval] = self.stack_offset
        return assignment

    def visitAssName(self, node):
        '''
        Visits an AssName node and flattens it.
        This can only come from an Assign node.
        param: node: the AssName node to visit
        return: Name of the left hand side of the assignment
        '''
        return node.name

    def visitDiscard(self, node):
        '''
        Visits a Discard node and flattens it.
        This can come from any node.
        param: node: the Discard node to visit
        return: Flattened Discard node
        '''
        return self.visit(node.expr)

    def visitConst(self, node):
        '''
        Visits a Const node and flattens it.
        This can come from any node. This is always an integer
        param: node: the Const node to visit
        return: The string representation of the integer
        '''
        return str(node.value)

    def visitName(self, node):
        '''
        Visits a Name node and flattens it.
        This can come from any node. This is always a variable or a function name because 
        the "True" and "False" are taken care of in the explicate pass
        param: node: the Name node to visit
        return: The name of the variable or function
        '''
        return node.name

    def visitGetFunPtr(self, node):
        '''
        Visits a GetFunPtr node and flattens it.
        This can come from any node. This is always a function name
        param: node: the GetFunPtr node to visit
        return: The name of the function
        '''
        return self.visit(CallFunc(Name("get_fun_ptr"), [self.visit(node.func)]))

    def visitGetFreeVars(self, node):
        '''
        Visits a GetFreeVar node and flattens it.
        This can come from any node. This is always a variable name
        param: node: the GetFreeVar node to visit
        return: The name of the variable
        '''
        return self.visit(CallFunc(Name("get_free_vars"), [self.visit(node.func)]))

    def visitCreateClosure(self, node):
        '''
        Visits a CreateClosure node and flattens it.
        This can come from any node. This is always a function name
        param: node: the CreateClosure node to visit
        return: The name of the function
        '''
        args = []
        args.append(self.visit(node.func))
        args.append(self.visit(node.free_vars))
        
        return self.visit(CallFunc(Name("create_closure"), args))

    def visitTypeError(self, node):
        '''
        This is only called when the explicate pass fails. 
        param: node: the TypeError node to visit.
        return: Returns a function call to the error function in runtime.c called pyob_error
        '''
        # FIXME: There is a bug here. We don't handle String nodes when parsing an AST.
        # This will crash the program because the outut is of the form "pyobj_error(Some message string that the compiler.parse can't handle)".
        return self.visit(CallFunc(Name("error_pyobj"), ["0"]))

    def visitIsTrue(self, node):
        '''
        This is only called when there is a boolean operation. This is only called from a "not" node
        param: node: the IsTrue node to visit
        return: Returns a function call to the is_true function in runtime.c called is_true
        '''
        return self.visit(CallFunc(Name("is_true"), [self.visit(node.obj)]))

    def visitIsInt(self, node):
        '''
        This is to verify if the pyobj is an integer. This is usually called during the explicate pass from an IfExp in a Let node
        or a Compare node or a not node.
        param: node: the IsInt node to visit
        return: Returns a function call to the is_int function in runtime.c
        '''
        return self.visit(CallFunc(Name("is_int"), [self.visit(node.obj)]))

    def visitIsBool(self, node):
        '''
        This is to verify if the pyobj is a bool. This is usually called during the explicate pass from an IfExp in a Let node
        or a Compare node or a not node.
        param: node: the IsBool node to visit
        return: Returns a function call to the is_bool function in runtime.c
        '''
        return self.visit(CallFunc(Name("is_bool"), [self.visit(node.obj)]))

    def visitIsBig(self, node):
        '''
        This is to verify if the pyobj is a big. This is usually called during the explicate pass from an IfExp in a Let node
        or a Compare node or a not node.
        param: node: the IsBig node to visit
        return: Returns a function call to the is_big function in runtime.c
        '''
        return self.visit(CallFunc(Name("is_big"), [self.visit(node.obj)]))

    def visitProjectTo(self, node):
        '''
        This is to project a pyobj to a specific type. This is usually called during the explicate pass from an IfExp in a Let node
        or a Compare node or a not node.
        param: node: the ProjectTo node to visit
        return: Returns a function call to the project_<specific_type> function in runtime.c
        '''
        return self.visit(CallFunc(Name("project_" + node.typ), [self.visit(node.arg)]))

    def visitInjectFrom(self, node, ):
        '''
        This is to inject a specific type to a pyobj. This is usually called during the explicate pass from an IfExp in a Let node
        or a Compare node or a not node.
        param: node: the InjectFrom node to visit
        return: Returns a function call to the inject_<specific_type> function in runtime.c
        '''
        # FIXME: There is a bug here. We add the inject var to the flattened_stmts list.
        # For now, we will just ignore it as its not needed and is probably a harmless bug.
        return self.visit(CallFunc(Name("inject_" + node.typ), [self.visit(node.arg)]))

    def visitLet(self, node):
        '''
        Visits a Let node and flattens it. This usually comes from the explicated ast and is used to create a new scope
        This can come from Add or UnarySub nodes
        param: node: the Let node to visit
        return: Flattened Let node
        '''
        # Not sure if this is the best way to do this. Should I be creating an assignment?
        # The book says that let statements should not be part of the output. #AskAsher or on the class-question Slack channel
        self.add_stmt(self.visit(
            Assign([AssName(self.visit(node.var), "OP_ASSIGN")], node.rhs)))
        return self.visit(node.body)

    def visitAddBig(self, node):
        '''
        Visits an AddBig node and flattens it. This usually comes from the explicated ast and is used to add two bigs
        Big can be a List or a Dict. We will encounter this only when we are adding.
        param: node: the AddBig node to visit
        return: Flattened AddBig node
        '''
        op1 = self.visit(node.left)
        op2 = self.visit(node.right)
        return self.visit(CallFunc(Name("add"), [op1, op2]))

    def visitAdd(self, node):
        '''
        Visits an Add node and flattens it. This usually comes from the explicated ast and 
        is used to add two ints or two bools or a bool and an int. We will encounter this only when we are adding.
        param: node: the Add node to visit
        return: Flattened Add node
        '''
        op1 = self.visit(node.left)
        op2 = self.visit(node.right)
        # Should this be the runtime call to add bigs instead of just '+'?
        var = op1 + " + " + op2
        tmpvar = utils.tmpvar()
        self.add_stmt(self.visit(
            Assign([AssName(tmpvar, "OP_ASSIGN")], Name(var))))
        return tmpvar

    def visitSubscript(self, node):
        '''
        Visits a Subscript node and flattens it. This usually comes from the explicated ast and is used to access a list or a dict
        param: node: the Subscript node to visit
        return: Flattened Subscript node
        '''
        var = self.visit(node.expr)
        index = self.visit(node.subs[0])
        tmpvar = utils.tmpvar()
        self.add_stmt(self.visit(
            Assign([AssName(tmpvar, "OP_ASSIGN")], Name(var + "[" + index + "]"))))
        return tmpvar

    def visitList(self, node):
        '''
        Visits a List node and flattens it. Because of the injection of the List type in explication, 
        this can come any node except a UnarySub node or a Module
        param: node: the List node to visit
        return: Flattened List node with injection of the List type
        '''
        var = "[" + ", ".join([self.visit(e) for e in node.nodes]) + "]"
        tmpvar = utils.tmpvar()
        self.add_stmt(self.visit(
            Assign([AssName(tmpvar, "OP_ASSIGN")], Name(var))))
        return tmpvar

    def visitDict(self, node):
        '''
        Visits a Dict node and flattens it. Because of the injection of the Dict type in explication,
        this can come any node except a UnarySub node or a Module
        param: node: the Dict node to visit
        return: Flattened Dict node with injection of the Dict type
        '''
        var = "{"
        for k, v in node.items:
            var = var + self.visit(k) + ": " + self.visit(v) + ", "
        var = var + "}"
        tmpvar = utils.tmpvar()
        self.add_stmt(self.visit(
            Assign([AssName(tmpvar, "OP_ASSIGN")], Name(var))))
        return tmpvar

    def visitIfExp(self, node, parent=None):
        '''
        Visits an IfExp node and flattens it. 
        For now only this makes use of the self.indent because of the if-then-else expansion
        param: node: the IfExp node to visit
        return: if-then-else statement
        '''
        # convert if-else to if-then-else
        test = self.visit(node.test)
        var = self.visit(InjectFrom("int", Const(0)))
        test = self.visit(CallFunc(Name("is_true"), [test]))
        if_exp = "if %s:" % str(test)
        self.add_stmt(if_exp)
        self.indent += 4
        then_op = self.visit(node.then)
        # FIXME: We know that Stmt coming Add is a List, Otherwise it isn't.
        # One issue is that when it is coming from a Stmt, we are doing an add_stmt of the lhs from the injection
        # This leads to one extra line of code (it is harmless since it is a discard but needs attention).
        # To reproduce this, try: 1 + 2 as your program and see the second last line of the "then" statements in the output
        then = var + " = " + \
            str(then_op[0] if isinstance(then_op, list) else then_op)
        self.add_stmt(then)
        self.indent -= 4
        else_exp = "else:"
        self.add_stmt(else_exp)
        self.indent += 4
        else_ = var + " = " + str(self.visit(node.else_))
        self.add_stmt(else_)
        self.indent -= 4
        return var

    def visitIf(self, node):
        '''
        Visits an If node and flattens it. This usually comes from the explicated ast and is used to create a if-then-else statement
        param: node: the If node to visit
        return: if-then-else statement
        '''
        test = self.visit(node.tests[0][0])
        # var = self.visit(InjectFrom("int", Const(0)))
        test = self.visit(CallFunc(Name("is_true"), [test]))
        if_exp = "if %s:" % str(test)
        self.add_stmt(if_exp)
        self.indent += 4
        self.visit(node.tests[0][1])
        # FIXME: We know that Stmt coming Add is a List, Otherwise it isn't.
        # One issue is that when it is coming from a Stmt, we are doing an add_stmt of the lhs from the injection
        # This leads to one extra line of code (it is harmless since it is a discard but needs attention).
        # To reproduce this, try: 1 + 2 as your program and see the second last line of the "then" statements in the output
        self.indent -= 4
        else_exp = "else:"
        self.add_stmt(else_exp)
        self.indent += 4
        self.visit(node.else_)
        self.indent -= 4
        return ""

    def visitWhile(self, node):
        '''
        Visits a While node and flattens it. This usually comes from the explicated ast and is used to create a while loop
        param: node: the While node to visit
        return: while loop
        '''
        InfiniteLoop = InjectFrom("int", Const(1))
        while_exp = "while %s:" % str(self.visit(InfiniteLoop))
        self.add_stmt(while_exp)
        self.indent += 4
        self.visit(If([(node.test, node.body)], Stmt([Break()])))
        self.indent -= 4
        return ""

    def visitBreak(self, node):
        '''
        Visits a Break node and flattens it. This usually comes from the explicated ast and is used to create a break statement
        param: node: the Break node to visit
        return: break statement
        '''
        return "break"

    def visitAnd(self, node):
        '''
        Visits an And node and flattens it. This can be a list of operand. 
        We need to split it into expression of two operands and then and them.
        Python has weird behavior where it return the last true operand if there is no false operand.
        or else it returns the first false operand.
        param: node: the And node to visit
        return: Flattened And node
        '''
        and_operands = [self.visit(n) for n in node.nodes[:2]]
        op1 = and_operands[0]
        op2 = and_operands[1]
        and_res = self.visit(IfExp(Name(op1), Name(op2), Name(op1)))
        deepest_var = and_res
        if len(node.nodes) > 2:
            deepest_var = self.visit(And([Name(deepest_var)] + node.nodes[2:]))
        return deepest_var

    def visitOr(self, node):
        '''
        Visits an Or node and flattens it. This can be a list of operand.
        We need to split it into expression of two operands and then or them.
        Python has a weird behavior where it returns the first true value.
        So we call is_true and return the first true value we find.
        param: node: the Or node to visit
        return: Flattened Or node
        '''
        or_operands = [self.visit(n) for n in node.nodes[:2]]
        op1 = or_operands[0]
        op2 = or_operands[1]
        or_res = self.visit(IfExp(Name(op1), Name(op1), Name(op2)))
        deepest_var = or_res
        if len(node.nodes) > 2:
            deepest_var = self.visit(Or([Name(deepest_var)] + node.nodes[2:]))
        return deepest_var

    def visitNot(self, node):
        '''
        Visits a Not node and flattens it.
        param: node: the Not node to visit
        return: Flattened Not node
        '''
        op1 = self.visit(node.expr)
        not_res = self.visit(IfExp(Name(op1), InjectFrom(
            "bool", Const(0)), InjectFrom("bool", Const(1))))
        return not_res

    def visitCompare(self, node):
        '''
        Visits a Compare node and flattens it.
        param: node: the Compare node to visit
        return: Flattened Compare node
        '''
        var = ""
        lhs = self.visit(node.expr)
        rhs = self.visit(node.ops[0][1])
        op = node.ops[0][0]
        var = lhs + " " + op + " " + rhs
        tmpvar = utils.tmpvar()
        self.add_stmt(self.visit(
            Assign([AssName(tmpvar, "OP_ASSIGN")], Name(var))))
        return tmpvar

    def visitUnarySub(self, node):
        '''
        Visits a UnarySub node and flattens it.
        param: node: the UnarySub node to visit
        return: Flattened UnarySub node
        '''
        var = "-" + str(self.visit(node.expr))
        tmpvar = utils.tmpvar()
        self.add_stmt(self.visit(
            Assign([AssName(tmpvar, "OP_ASSIGN")], Name(var))))
        return tmpvar

    def visitCallFunc(self, node):
        '''
        Visits a CallFunc node and flattens it.
        param: node: the CallFunc node to visit
        return: Flattened CallFunc node
        '''
        args = "(" + ", ".join([self.visit(arg) \
            if isinstance(arg, Node) else arg \
            for arg in node.args]) + ")"
        func = self.visit(node.node) + args
        tmpvar = utils.tmpvar()
        self.add_stmt(self.visit(
            Assign([AssName(tmpvar, "OP_ASSIGN")], Name(func))))
        if func == "input()":
            tmpvar = self.visit(InjectFrom("int", Name(tmpvar)))

        return tmpvar

    def visitFunction(self, node):
        '''
        Visits a Function node and flattens it.
        param: node: the Function node to visit
        return: Flattened Function node
        '''
        func_signature = "def " + node.name + "(" + \
            ", ".join([arg for arg in node.argnames]) + "):"
        self.add_stmt(func_signature)
        self.indent += 4
        self.visit(node.code)
        self.indent -= 4
        return ""

    def visitReturn(self, node):
        '''
        Visits a Return node and flattens it.
        I am assuming that the return is always a part of a function.
        So indent it.
        param: node: the Return node to visit
        return: Flattened Return node
        '''
        self.add_stmt("return " + str(self.visit(node.value)))
        return ""


# Helper Functions to get Flattened AST and Flattened Statements

def get_flattened_ast(node):
    flattener = compiler.visitor.walk(node,
                          FlattenVisitor())
    prog = ""
    for stmt in flattener.flattened_stmts:
        prog += stmt + "\n"
    return compiler.parse(prog)

def get_flattened_statements(node):
    flattener = compiler.visitor.walk(node,
                          FlattenVisitor())
    return flattener.flattened_stmts

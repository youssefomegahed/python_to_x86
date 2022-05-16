import compiler
from compiler.ast import Const
from compiler.ast import Name
from compiler.ast import Discard
from compiler.ast import Assign
from compiler.ast import AssName
from compiler.ast import Module
from compiler.ast import Add
from compiler.ast import Stmt
from compiler.ast import UnarySub
from compiler.ast import Printnl
from compiler.ast import Node
from compiler.ast import IfExp
from compiler.ast import And
from compiler.ast import Or
from compiler.ast import Not
from compiler.ast import Compare
from compiler.ast import List
from compiler.ast import Subscript
from compiler.ast import Dict
from compiler.ast import Function
from compiler.ast import Lambda
from compiler.ast import Return
from compiler.ast import CallFunc
from compiler.ast import While
from compiler.ast import If
import utils
from utils import LAMBDA
import freevars as fv


# from utils import INT, BOOL, BIG

class GetFunPtr(Node):
    def __init__(self, func):
        self.func = func

    def __repr__(self):
        return "GetFunPtr(%s)" % repr(self.func)


class GetFreeVars(Node):
    def __init__(self, func):
        self.func = func

    def __repr__(self):
        return "GetFreeVars(%s)" % repr(self.func)


class CreateClosure(Node):
    def __init__(self, func, free_vars):
        self.func = func
        self.free_vars = free_vars

    def __repr__(self):
        return "CreateClosure(%s, %s)" % (repr(self.func), repr(self.free_vars))


class ClosureConversionVisitor(compiler.visitor.ASTVisitor):
    def __init__(self, heap_vars):
        self.converted_ast = None
        self.function_list = []
        self.main_list = []
        self.heap_vars = heap_vars

    def visitModule(self, node):
        stmt_node = self.visit(node.node)
        stmt_node = stmt_node.nodes if isinstance(
            stmt_node, Stmt) else [stmt_node]

        self.function_list.append(
            Function(None, "main", [], [], 0, None, Stmt(self.main_list + stmt_node)))

        stmt_node = Stmt(self.function_list)

        self.converted_ast = Module(None, stmt_node)

     # Convert Lambda to closure
    # Return Function node which is a Closure
    def visitLambda(self, node):
        # get free_vars and params from lambda
        free_vars = fv.get_free_vars(node)
        fvs_name = utils.tmpvar("fvs")
        params = node.argnames

        # create closure from free vars and newbody
        # append to global list so that we can add to global scope
        # Return the last node in the body
        newbody = self.visit(node.code)

        # might want to change to functmp() or something
        global_name = utils.tmpvar(LAMBDA)

        # Since we are using closure for recursion, we need the free_vars to be in the definition
        in_closure_free_vars = []
        for var in free_vars:
            in_closure_free_vars.append(
                Assign([AssName(var, "OP_ASSIGN")],
                       Subscript(Name(fvs_name), "OP_APPLY", [Const(list(free_vars).index(var))]))
            )

        
        newbody = Stmt(in_closure_free_vars + newbody.nodes)

        func = Function(None, global_name, [
                        fvs_name] + params, [], 0, None, newbody)
        self.function_list.append(func)
        self.main_list.append(
            Assign([AssName(global_name, "OP_ASSIGN")], CreateClosure(Name(global_name), List(free_vars)))
            )

        return CreateClosure(Name(global_name), List(free_vars))

    def visitFunction(self, node):
        # get free_vars and params from lambda
        free_vars = fv.get_free_vars(node)
        fvs_name = utils.tmpvar("fvs")
        params = node.argnames

        # create closure from free vars and newbody
        # append to global list so that we can add to global scope
        newbody = self.visit(node.code)
        # might want to change to functmp() or something
        global_name = utils.tmpvar(LAMBDA+'_'+node.name)

        # Since we are using closure for recursion, we need the free_vars to be in the definition
        in_closure_free_vars = []
        for var in free_vars:
            in_closure_free_vars.append(
                Assign([AssName(var, "OP_ASSIGN")],
                       Subscript(Name(fvs_name), "OP_APPLY", [Const(list(free_vars).index(var))]))
            )

        cl_name = node.name
        if cl_name in self.heap_vars:
            cl_name = [Assign([AssName(node.name, "OP_ASSIGN")], List([CreateClosure(
            Name(global_name), List(free_vars))]))]
        else:
            cl_name = [Assign([AssName(node.name, "OP_ASSIGN")], CreateClosure(
            Name(global_name), List(free_vars)))]

        closure_for_recursion = cl_name

        newbody = Stmt(in_closure_free_vars +
                       closure_for_recursion + newbody.nodes)

        func = Function(None, global_name, [
                        fvs_name] + params, [], 0, None, newbody)
        self.function_list.append(func)

        name = node.name
        lhs = AssName(name, "OP_ASSIGN")
        rhs = CreateClosure(Name(global_name), List(free_vars))
        if name in self.heap_vars:
            lhs = Subscript(Name(name), 'OP_ASSIGN', [Const(0)])

        return Assign([lhs], rhs)

    # From book:
    # In this pass it is helpful to use a different AST class for
    # in- direct function calls, whose operator will be the result
    # of an expression such as above, versus direct calls to the
    # runtime C functions.

    # TODO(raghu): Node in a CallFunc can be lambda like this: (lambda x: x + 1)(3)
    # Handle lambda in CallFunc
    def visitCallFunc(self, node):
        # if calling input(), return input()
        if hasattr(node.node, "name") and node.node.name == "input":
            return node

        func_name = self.visit(node.node)
        args = []
        for arg in node.args:
            args.append(self.visit(arg))

        if isinstance(node.node, Lambda):
            # get free_vars and params from lambda
            return CallFunc(GetFunPtr(func_name.func), [GetFreeVars(func_name.func)] + args)
        return CallFunc(GetFunPtr(func_name), [GetFreeVars(func_name)] + args)

    # Handle Assign
    def visitAssign(self, node):
        lval = self.visit(node.nodes[0])
        rval = self.visit(node.expr)
        return Assign([lval], rval)

    def visitStmt(self, node):
        children = []
        for child in node.nodes:
            children.append(self.visit(child))
        return Stmt(children)

    def visitPrintnl(self, node):
        return Printnl([self.visit(node.nodes[0])], None)

    # Handle AssName
    def visitAssName(self, node):
        return node

    # Handle Discard
    def visitDiscard(self, node):
        return Discard(self.visit(node.expr))

    # Handle Const
    def visitConst(self, node):
        return node

    # Handle Name
    def visitName(self, node):
        return node

    def visitList(self, node):
        exp_children = []
        for child in node.nodes:
            exp_children.append(self.visit(child))
        return List(exp_children)

    def visitDict(self, node):
        exp_children = []
        for key, value in node.items:
            exp_children.append((self.visit(key), self.visit(value)))
        return Dict(exp_children)

    def visitSubscript(self, node):
        subs = [self.visit(sub) for sub in node.subs]
        return Subscript(self.visit(node.expr), node.flags, subs)

    def visitIfExp(self, node):
        return IfExp(self.visit(node.test), self.visit(node.then), self.visit(node.else_))
    
    def visitIf(self, node):
        test = self.visit(node.tests[0][0])
        body = self.visit(node.tests[0][1])
        else_ = self.visit(node.else_)
        return If([(test, body)], else_)

    def visitWhile(self, node):
        test = self.visit(node.test)
        body = self.visit(node.body)
        return While(test, body, None)

    def visitAnd(self, node):
        exp_children = []
        for child in node.nodes:
            exp_children.append(self.visit(child))
        return And(exp_children)

    def visitOr(self, node):
        exp_children = []
        for child in node.nodes:
            exp_children.append(self.visit(child))
        return Or(exp_children)

    def visitNot(self, node):
        return Not(self.visit(node.expr))

    def visitCompare(self, node):
        exp_children = []
        for op, child in node.ops:
            exp_children.append((op, self.visit(child)))
        return Compare(self.visit(node.expr), exp_children)

    def visitReturn(self, node):
        return Return(self.visit(node.value))

    def visitAdd(self, node):
        return Add((self.visit(node.left), self.visit(node.right)))

    def visitUnarySub(self, node):
        return UnarySub(self.visit(node.expr))


# # helper for creating closure converted ast from heapified ast
def get_converted_ast(heapified_ast, heap_vars):
    return compiler.visitor.walk(heapified_ast, ClosureConversionVisitor(heap_vars)).converted_ast

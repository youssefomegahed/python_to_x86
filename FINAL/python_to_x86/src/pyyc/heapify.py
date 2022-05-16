# Description:
# This program should take a uniquified AST and return a new AST
# with all the free variables replaced by a one-element list containing
# the free variable value.

# Additionally, the original free variables should be replaced by the
# heapified version wherever the free variables are used in the body of a
# function or a lambda (or the entire program).

from ast import Sub
import uniquify as unq
import freevars as fv
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


class HeapVarCollector(compiler.visitor.ASTVisitor):
    '''
    Collect all the variables that need to be heapified and
    put it in a list to be processed later by the actual
    heapifier.
    Except Name, Const, and AssName, a free_vars can
    hide in all the other nodes in the form of a lambda
    or a function. So we need to check the free_vars
    of the other nodes.
    '''

    def __init__(self):
        self.heapvars = set([])

    def visitModule(self, node):
        self.visit(node.node)

    def visitStmt(self, node):
        for child in node.nodes:
            self.visit(child)

    def visitAssign(self, node):
        self.visit(node.expr)
        for target in node.nodes:
            self.visit(target)

    def visitPrintnl(self, node):
        self.visit(node.nodes[0])

    def visitAdd(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visitIfExp(self, node):
        self.visit(node.test)
        self.visit(node.then)
        self.visit(node.else_)

    def visitIf(self, node):
        self.visit(node.tests[0][0])
        self.visit(node.tests[0][1])
        self.visit(node.else_)

    def visitWhile(self, node):
        self.visit(node.test)
        self.visit(node.body)

    def visitDiscard(self, node):
        self.visit(node.expr)

    def visitCompare(self, node):
        self.visit(node.expr)
        for op in node.ops:
            self.visit(op[1])

    def visitOr(self, node):
        for child in node.nodes:
            self.visit(child)

    def visitAnd(self, node):
        for child in node.nodes:
            self.visit(child)

    def visitNot(self, node):
        self.visit(node.expr)

    def visitList(self, node):
        for child in node.nodes:
            self.visit(child)

    def visitDict(self, node):
        for k, v in node.items:
            self.visit(k)
            self.visit(v)

    def visitSubscript(self, node):
        self.visit(node.expr)
        [self.visit(sub) for sub in node.subs]

    def visitFunction(self, node):
        self.heapvars = self.heapvars.union(fv.get_free_vars(node))
        self.visit(node.code)

    def visitLambda(self, node):
        self.heapvars = self.heapvars.union(fv.get_free_vars(node))
        self.visit(node.code)

    def visitReturn(self, node):
        self.visit(node.value)

    def visitCallFunc(self, node):
        self.visit(node.node)
        for arg in node.args:
            self.visit(arg)


class HeapifyVisitor(compiler.visitor.ASTVisitor):
    '''
    Heapify Variables(See Description).
    Look for variables in the heapvar list and replace the
    vars in the program with a one-element list. Note that
    the declaration should be a one-element list, every 
    other instance of that variable should be just a subscript
     operation.
    '''

    def __init__(self, heapvars):
        self.heapvars = heapvars
        self.globalvars = heapvars  # FIXME: This is a hack
        self.heapified_ast = None

    def visitModule(self, node):
        globalvars = [Assign([AssName(name, "OP_ASSIGN")], List([
            Const(0)])) for name in self.globalvars]

        # This is hoping that Module will always be the first node
        # and it'll always have a single Stmt as its child.
        stmt_node = self.visit(node.node)
        stmt_node.nodes = globalvars + stmt_node.nodes
        self.heapified_ast = Module(None, stmt_node)

    def visitStmt(self, node):
        children = []
        for child in node.nodes:
            children.append(self.visit(child))
        return Stmt(children)

    def visitName(self, node):
        if node.name in self.heapvars:
            return Subscript(Name(node.name), "OP_APPLY", [Const(0)])
        return node

    def visitConst(self, node):
        return node

    def visitAssName(self, node):
        return node

    def visitAssign(self, node):
        lval = node.nodes[0]
        rval = self.visit(node.expr)
        if isinstance(lval, Subscript):
            return Assign([self.visit(lval)], rval)

        # If it is not a subscript, it is definitely an AssName
        if lval.name in self.heapvars:
            return Assign([Subscript(Name(lval.name), "OP_ASSIGN", [Const(0)])], rval)

        return Assign([self.visit(lval)], rval)

    def visitAdd(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return Add((left, right))

    def visitUnarySub(self, node):
        return UnarySub(self.visit(node.expr))

    def visitPrintnl(self, node):
        # Based on the runtime, I am assumging that
        # print will only have one argument.
        expr = self.visit(node.nodes[0])
        return Printnl([expr], node.dest)

    def visitIfExp(self, node):
        test = self.visit(node.test)
        then = self.visit(node.then)
        else_ = self.visit(node.else_)
        return IfExp(test, then, else_)

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
        expr = self.visit(node.expr)
        return Not(expr)

    def visitCompare(self, node):
        exp_children = []
        for op, child in node.ops:
            exp_children.append((op, self.visit(child)))
        return Compare(self.visit(node.expr), exp_children)

    # Handle List
    def visitList(self, node):
        children = []
        for child in node.nodes:
            children.append(self.visit(child))
        return List(children)

    def visitSubscript(self, node):
        expr = self.visit(node.expr)
        flags = node.flags
        subs = [self.visit(sub) for sub in node.subs]
        return Subscript(expr, flags, subs)

    def visitDict(self, node):
        children = []
        for key, val in node.items:
            children.append((self.visit(key), self.visit(val)))
        return Dict(children)

    def visitCallFunc(self, node):
        return CallFunc(self.visit(node.node), [self.visit(arg) for arg in node.args])

    def visitFunction(self, node):
        '''
        FIXME: This is not how the book suggests to handle this.
        The function body is a Stmt node. So Loop through the 
        arguments and see if it is in the heapvar list, if yes, 
        then just add a heapified declaration for that param at 
        the beginning of the Stmt node in the function body
        '''
        decorators = node.decorators
        name = node.name
        argnames = node.argnames
        defaults = node.defaults
        flags = node.flags
        doc = node.doc
        code = self.visit(node.code)

        # Order matters here.
        for arg in argnames:
            if arg in self.heapvars:
                code.nodes.insert(
                    0, Assign([AssName(arg, "OP_ASSIGN")], List([Name(arg)])))


        return Function(decorators, name, argnames, defaults, flags, doc, code)

    def visitLambda(self, node):
        '''
        If there are nested lambdas and the free variable
        in the inner lambda depends on a free-variable which
        is a func arg to the outer lambda, then we create a
        Stmt node and add an assignment node to the beginning
        of the lambda body.
        '''
        argnames = node.argnames
        defaults = node.defaults
        flags = node.flags
        code = self.visit(node.code)
        
        # Order matters here.
        for arg in argnames:
            if arg in self.heapvars:
                code.nodes.insert(
                    0, Assign([AssName(arg, "OP_ASSIGN")], List([Name(arg)])))

        return Lambda(argnames, defaults, flags, code)

    def visitDiscard(self, node):
        return Discard(self.visit(node.expr))

    def visitReturn(self, node):
        node.value = self.visit(node.value)
        return node


# Helper function to create a heapified AST from a given AST
def get_heapified_ast(node):
    heap_vars = get_heap_vars(node)
    return compiler.visitor.walk(node, HeapifyVisitor(heap_vars)).heapified_ast

def get_heap_vars(node):
    return compiler.visitor.walk(node, HeapVarCollector()).heapvars

# explicate.py
# Prologue
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
from utils import INT, BOOL, BIG
import uniquify
from closure import GetFunPtr, GetFreeVars, CreateClosure

# Setup for Dynamic Dispatch


class GetTag(Node):
    def __init__(self, arg):
        self.arg = arg


class InjectFrom(Node):
    def __init__(self, typ, arg):
        self.typ = typ
        self.arg = arg

    def __repr__(self):
        return "InjectFrom(%s, %s)" % (repr(self.typ), repr(self.arg))


class ProjectTo(Node):
    def __init__(self, typ, arg):
        self.typ = typ
        self.arg = arg

    def __repr__(self):
        return "ProjectTo(%s, %s)" % (repr(self.typ), repr(self.arg))


class Let(Node):
    def __init__(self, var, rhs, body):
        self.var = var
        self.rhs = rhs
        self.body = body

    def __repr__(self):
        return "Let(%s, %s, %s)" % (repr(self.var), repr(self.rhs), repr(self.body))


class IsInt(Node):
    def __init__(self, obj):
        self.obj = obj

    def printName(self, funcName):
        return "%s(%s)" % (funcName, repr(self.obj))

    def __repr__(self):
        return self.printName('IsInt')


class IsBool(IsInt):
    def __repr__(self):
        return self.printName('IsBool')


class IsBig(IsInt):
    def __repr__(self):
        return self.printName('IsBig')


class AddBig(Add):
    def __repr__(self):
        return "AddBig(%s)" % (str(self.asList()))


class IsTrue(IsInt):
    def __repr__(self):
        return self.printName('IsTrue')


class TypeError(Node):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return "TypeError(%s)" % (repr(self.message))


# Explicate Nodes
class ExplicateVisitor(compiler.visitor.ASTVisitor):
    def __init__(self):
        self.explicit_ast = None

    # Handle NonP2 Specific Nodes

    # Handle Module
    def visitModule(self, node):
        self.explicit_ast = Module(None, self.visit(node.node))

    # Handle Stmt

    def visitStmt(self, node):
        children = []
        for child in node.nodes:
            children.append(self.visit(child))
        return Stmt(children)

    # Handle Printnl

    def visitPrintnl(self, node):
        return Printnl([self.visit(node.nodes[0])], None)

    # Handle Assign

    def visitAssign(self, node):
        return Assign([self.visit(node.nodes[0])], self.visit(node.expr))

    # Handle AssName

    def visitAssName(self, node):
        return node

    # Handle Discard

    def visitDiscard(self, node):
        return Discard(self.visit(node.expr))

    # Handle Const

    def visitConst(self, node):
        return InjectFrom(INT, node)

    # Handle Name

    def visitName(self, node):
        if node.name in ['True', 'False']:
            return InjectFrom(BOOL,
                              Const(0) if node.name == 'False' else Const(1))
        return node

    # Handle Add

    def visitAdd(self, node):
        '''
        Addition is a special case because we don't know the type 
        of the lhs and rhs at compile time. We can only know the 
        type of the lhs and rhs at runtime. So we need to do 
        some dynamic dispatch.

        So we use the following rules:
        1. Check if the lhs and rhs are both ints or bools. 
          If so, return a Add as bools are treated as ints in 
          python.
        2. Check if the lhs and rhs are both bigs. If so, return a
          AddBig.

        Use temporary variables to store the lhs and rhs until the 
        dynamic dispatch is done. (Accomplished by using `Let`)
        '''

        # Check if lhs and rhs are both ints or bools
        # if so, compute the sum at compile time
        lhs = node.left
        rhs = node.right
        
        if isinstance(lhs, Name):
            if lhs.name in ['True', 'False']:
                lhs = Const(0) if lhs.name == 'False' else Const(1)
        
        if isinstance(rhs, Name):
            if rhs.name in ['True', 'False']:
                rhs = Const(0) if rhs.name == 'False' else Const(1)

        if isinstance(lhs, Const) and isinstance(rhs, Const):
            return self.visit(Const(lhs.value + rhs.value))
            


        ltemp = Name(utils.tmpvar())
        rtemp = Name(utils.tmpvar())
        big_check = And([InjectFrom(INT, IsBig(ltemp)),
                        InjectFrom(INT, IsBig(rtemp))])

        ltemp_check = Or([InjectFrom(INT, IsInt(ltemp)),
                         InjectFrom(INT, IsBool(ltemp))])
        rtemp_check = Or([InjectFrom(INT, IsInt(rtemp)),
                         InjectFrom(INT, IsBool(rtemp))])

        return Let(ltemp, self.visit(node.left),
                   Let(rtemp, self.visit(node.right),
                       IfExp(And([ltemp_check, rtemp_check]),
                             InjectFrom(INT, Add((ltemp, rtemp))),
                             IfExp(big_check,
                                   InjectFrom(BIG, AddBig(
                                       (ProjectTo(BIG, ltemp), ProjectTo(BIG, rtemp)))),
                                   TypeError("Unsupported Types for Addition")))))  # Type Error

    # Handle UnarySub

    def visitUnarySub(self, node):
        return InjectFrom(INT, UnarySub(self.visit(node.expr)))

    # Handle CallFunc

    def visitCallFunc(self, node):
        name = self.visit(node.node)
        args = [self.visit(arg) for arg in node.args]
        return CallFunc(name, args)

    # Handle List

    def visitList(self, node):
        exp_children = []
        for child in node.nodes:
            exp_children.append(self.visit(child))
        return List(exp_children)

    # Handle Dict

    def visitDict(self, node):
        exp_children = []
        for key, value in node.items:
            exp_children.append((self.visit(key), self.visit(value)))
        return Dict(exp_children)

    # Handle Subscript

    def visitSubscript(self, node):
        subs = []
        for i in range(len(node.subs)):
            subs.append(self.visit(node.subs[i]))
        return Subscript(self.visit(node.expr), node.flags, subs)

    # Handle IfExp

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

    # Handle Logical Operators

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

    # Handle Compare

    def visitCompare(self, node):
        exp_children = []
        for op, child in node.ops:
            exp_children.append((op, self.visit(child)))
        return Compare(self.visit(node.expr), exp_children)

    # Handle Function

    def visitFunction(self, node):
        '''
        Function AST consists of the following items in the following order:
        decorator: [], name: str, argsnames: [], defaultvalues: [],
        flags: Some Number, doc: None, code: Bunch of things inside a 'Stmt' Node
        '''

        decorators = node.decorators
        name = node.name
        args = node.argnames
        defaults = node.defaults
        flags = node.flags
        doc = node.doc
        body = self.visit(node.code)

        return Function(decorators, name, args, defaults, flags, doc, body)

    # Handle Lambda

    def visitLambda(self, node):
        '''
        Lambda AST consists of the following items in 
        the following order:
        argnames: [], defaults: [], flags: Number, code: Some AST Nodes(s)
        '''
        args = node.argnames
        defaults = node.defaults
        flags = node.flags
        body = Return(self.visit(node.code))

        return Lambda(args, defaults, flags, body)

    # Handle Return

    def visitReturn(self, node):
        return Return(self.visit(node.value))
    
    def visitCreateClosure(self, node):
        freevars = map(lambda x: self.visit(Name(x)), node.free_vars)
        return InjectFrom(BIG, CreateClosure(node.func, List(freevars)))

    def visitGetFunPtr(self, node):
        return GetFunPtr(self.visit(node.func))

    def visitGetFreeVars(self, node):
        return GetFreeVars(self.visit(node.func))


# Helper function to explicate the AST
def get_explicated_ast(node):
    return compiler.visitor.walk(node,
                                 ExplicateVisitor()).explicit_ast

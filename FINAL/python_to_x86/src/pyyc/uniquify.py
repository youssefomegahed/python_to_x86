# uniquify.py
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

class FunctionCollector(compiler.visitor.ASTVisitor):
    '''
    Collect all the function names in the AST and its scope.
    We need this to know which functions should get which unique names
    during function calls
    '''

    def __init__(self):
        self.top = -1
        self.func_tbl = []

    def visitModule(self, node):

        # Happens only once
        self.top += 1
        self.func_tbl.append(set([]))

        self.visit(node.node)

        self.top -= 1


    def visitStmt(self, node):
        for child in node.nodes:
            self.visit(child)

    def visitAssign(self, node):
        lhs = self.visit(node.nodes[0])
        rhs = node.expr
        if isinstance(rhs, Lambda):
          self.visit(rhs, lhs)

    def visitAssName(self, node):
      return node.name

    def visitName(self, node):
      return node.name

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
        return self.visit(node.expr)

    def visitFunction(self, node):
        self.func_tbl[self.top].update(set([node.name]))

        # Create new scope
        self.top += 1
        # We don't want to create a new set again
        # if it already exists. Note here
        # all the functions are global scope now
        if len(self.func_tbl) <= self.top:
            self.func_tbl.append(set([]))

        self.visit(node.code)

        # Destroy scope
        self.top -= 1

    def visitLambda(self, node, parent=None):
        if parent is not None:
            self.func_tbl[self.top].update(set([parent]))
          
        # Create new scope
        self.top += 1
        # We don't want to create a new set again
        # if it already exists. Note here
        # all the functions are global scope now
        if len(self.func_tbl) <= self.top:
            self.func_tbl.append(set([]))

        self.visit(node.code)

        # Destroy scope
        self.top -= 1

    def visitReturn(self, node):
        self.visit(node.value)

    def visitCallFunc(self, node):
        self.visit(node.node)
        for arg in node.args:
            self.visit(arg)


class UniquifyVisitor(compiler.visitor.ASTVisitor):
  def __init__(self, func_tbl):
    self.uniquified_ast = None
    self.stack = utils.Stack()
    self.func_tbl = func_tbl
    self.lambda_assign_list = []

  def visitModule(self, node):
    self.stack.push(set([]))
    self.lambda_assign_list.append([])

    self.uniquified_ast = Module(None, self.visit(node.node))

    self.uniquified_ast.node = Stmt(self.lambda_assign_list[0]
                                    + self.uniquified_ast.node.nodes)

    self.lambda_assign_list.pop()
    self.stack.pop()

  # Handle Function

  def visitFunction(self, node):
    current_scope = self.stack.size() - 1
    function_name = node.name + '_' + str(current_scope)
    self.stack.peek().update(set([node.name]))

    self.stack.push(set([]))
    self.lambda_assign_list.append([])


    args = node.argnames
    uniquified_args = []
    current_scope = self.stack.size() - 1
    for arg in args:
      self.stack.peek().update(set([arg]))
      var = arg  + '_' + str(current_scope)
      uniquified_args.append(var)

    
    code = self.visit(node.code)
    code = Stmt(self.lambda_assign_list[current_scope] + code.nodes)

    # Destroy scope
    self.lambda_assign_list.pop()
    self.stack.pop()

    ret = Function(node.decorators, function_name, uniquified_args,
                    node.defaults, node.flags, node.doc, code)
    
    return ret

  # Handle Lambda

  def visitLambda(self, node, parent=None):
    # Create new scope
    self.stack.push(set([]))
    self.lambda_assign_list.append([])

    args = node.argnames
    uniquified_args = []
    current_scope = self.stack.size() - 1
    for arg in args:
      self.stack.peek().update(set([arg]))
      var = arg  + '_' + str(current_scope)
      uniquified_args.append(var)

    code = Stmt([Return(self.visit(node.code))])
    if len(self.lambda_assign_list[current_scope]) > 0:
      code = Stmt(self.lambda_assign_list[current_scope] + code.nodes)
 
    ret = Lambda(uniquified_args, node.defaults, node.flags, code)
    if not isinstance(parent, Assign):
      name = utils.tmpvar('uflattened_lambda')
      self.lambda_assign_list[current_scope - 1].append(
        Assign([AssName(name, 'OP_ASSIGN')], ret)
      )
      ret = Name(name)

    # Destroy scope
    self.lambda_assign_list.pop()
    self.stack.pop()

    return ret

  # Remap the name based on the scope in Name and AssName nodes
  # Handle nodes to be remapped
  # Handle Name

  def visitName(self, node):
    '''
    Name Node has two special cases. "True" and "False"
    If the node name is not one of these, only then 
    proceed with the remapping.
    '''
    var = node.name
    if var not in ["True", "False", "input"]:
      current_scope = self.stack.size() - 1
      # Check if the variable is in current or parent scope
      is_var_found = False
      for i in range(current_scope, -1, -1):
        if var in self.stack.get(i):
          var = var + '_' + str(i)
          is_var_found = True
          break
      
      if not is_var_found:
        for i in range(current_scope, -1, -1):
          if var in self.func_tbl[i]:
            var = var + '_' + str(i)
            is_var_found = True
            break
      
      if not is_var_found:
        self.stack.peek().update(set([var]))       # Add to current scope
        var = var + '_' + str(current_scope) # Add to current scope

    return Name(var)

  # Handle AssName

  def visitAssName(self, node):
    current_scope = self.stack.size() - 1
    self.stack.peek().update(set([node.name]))
    var = node.name + '_' + str(current_scope)
    return AssName(var, node.flags)

  # All other nodes
  # Handle all other nodes

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
    lhs = self.visit(node.nodes[0])
    rhs = node.expr
    if isinstance(rhs, Lambda):
      rhs = self.visit(node.expr, Assign)
    else:
      rhs = self.visit(node.expr)
    return Assign([lhs], rhs)

  # Handle Add

  def visitAdd(self, node):
    return Add((self.visit(node.left), self.visit(node.right)))

  # Handle Const

  def visitConst(self, node):
    return node

  # Handle Discard

  def visitDiscard(self, node):
    return Discard(self.visit(node.expr))

  # Handle UnarySub

  def visitUnarySub(self, node):
    return UnarySub(self.visit(node.expr))

  # Handle CallFunc

  def visitCallFunc(self, node):
    return CallFunc(self.visit(node.node), [self.visit(arg) for arg in node.args])

  # Handle Return
  def visitReturn(self, node):
    return Return(self.visit(node.value))

  # Handle List

  def visitList(self, node):
    children = []
    for child in node.nodes:
      children.append(self.visit(child))
    return List(children)

  # Handle Dict

  def visitDict(self, node):
    children = []
    for key, val in node.items:
      children.append((self.visit(key), self.visit(val)))
    return Dict(children)

  # Handle Subscript

  def visitSubscript(self, node):
    '''
    node.subs might also have to be handled?
    '''
    subs = [self.visit(sub) for sub in node.subs]
    return Subscript(self.visit(node.expr), node.flags, subs)

  # Handle IfExp

  def visitIfExp(self, node):
    return IfExp(self.visit(node.test), self.visit(node.then), self.visit(node.else_))

  # Handle If
  def visitIf(self, node):
    test = self.visit(node.tests[0][0])
    body = self.visit(node.tests[0][1])
    else_ = self.visit(node.else_)
    return If([(test, body)], else_)

  # Handle While
  def visitWhile(self, node):
    test = self.visit(node.test)
    body = self.visit(node.body)
    return While(test, body, None)

  # Handle Logical Operators

  def visitAnd(self, node):
    children = []
    for child in node.nodes:
      children.append(self.visit(child))
    return And(children)

  def visitOr(self, node):
    children = []
    for child in node.nodes:
      children.append(self.visit(child))
    return Or(children)

  def visitNot(self, node):
    return Not(self.visit(node.expr))

  # Handle Compare

  def visitCompare(self, node):
    children = []
    for op, child in node.ops:
      children.append((op, self.visit(child)))
    return Compare(self.visit(node.expr), children)

# Helper function to get uniquified AST
def get_uniquified_ast(node):
  func_tbl = compiler.visitor.walk(
      node, FunctionCollector()).func_tbl
  uniquifier = compiler.visitor.walk(
      node, UniquifyVisitor(func_tbl))
  return uniquifier.uniquified_ast

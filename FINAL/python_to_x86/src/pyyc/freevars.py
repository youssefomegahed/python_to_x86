# freevars.py
# Prologue
import compiler

class FreeVarVisitor(compiler.visitor.ASTVisitor):
  '''
  This program should take an AST and return a set of 
  free variables for the given top-level AST node.

  The visitor should be called at the appropriate level.
  For a doubly nested function, the visitor should be called
  once on the outer function, and once on the inner function
  to get the free variables for the outer function and the
  inner function respectively.
  '''
  def __init__(self):
    self.freevars = set([])
    self.boundvars = set([])

  def visitStmt(self, node):
    for child in node.nodes:
      self.visit(child)

  def visitName(self, node):
    if node.name not in ["True", "False", "input"]:
      self.freevars.add(node.name)
  
  def visitAssign(self, node):
    self.visit(node.expr)
    for child in node.nodes:
      self.visit(child)

  def visitAssName(self, node):
    self.boundvars.add(node.name)
  
  def visitLambda(self, node):
    for arg in node.argnames:
      self.boundvars.add(arg)
    self.visit(node.code)
    self.freevars.difference_update(self.boundvars)

  def visitFunction(self, node):
    self.boundvars.add(node.name)
    for arg in node.argnames:
      self.boundvars.add(arg)
    self.visit(node.code)
    self.freevars.difference_update(self.boundvars)

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
    
  def visitCallFunc(self, node):
    self.visit(node.node)
    for arg in node.args:
      self.visit(arg)
  
  def visitPrintnl(self, node):
    self.visit(node.nodes[0])
  
  def visitAdd(self, node):
    self.visit(node.left)
    self.visit(node.right)

  def visitUnarySub(self, node):
    self.visit(node.expr)

  def visitCompare(self, node):
    self.visit(node.expr)
    for op in node.ops:
      self.visit(op[1])

  def visitSubscript(self, node):
    self.visit(node.expr)
    self.visit(node.subs[0])

  def visitList(self, node):
    [self.visit(arg) for arg in node.nodes]
  
  def visitAnd(self, node):
    [self.visit(arg) for arg in node.nodes]

  def visitOr(self, node):
    [self.visit(arg) for arg in node.nodes]

  def visitNot(self, node):
    self.visit(node.expr)

  def visitDict(self, node):
    for key, value in node.items:
      self.visit(key)
      self.visit(value)

  def visitReturn(self, node):
    if node.value:
      self.visit(node.value)

  def visitDiscard(self, node):
    self.visit(node.expr)


def get_free_vars(node):
  return compiler.visitor.walk(node, FreeVarVisitor()).freevars

def get_bound_vars(node):
  return compiler.visitor.walk(node, FreeVarVisitor()).boundvars
###########################################################
# File: src/pyyc/utils.py                                 #
# Description: Utility functions, constants, and classes  #
###########################################################

from cProfile import label
import re
from datetime import datetime
from os import path
import sys

#############################################################
# Utility Classes for Semantic Analysis and Code Generation #
#############################################################


class Graph(object):
    class Vertex():
        def __init__(self, name):
            self.name = name
            self.possible_colors = set()
            self.neighbors = set()
            self.color = None
            self.type = REGISTER if name in [
                EAX, EBX, ECX, EDX, ESP, EBP, ESI, EDI] else STACK if FRAMEBASE in name else CONST if re.match(r'^\d+$', name) else VARIABLE
            self.unspillable = False

        def __str__(self):
            return "\nVertex(Name(%s), \n\t Neighbors(%s), \n\t PossibleColors(%s), \n\t Color(%s), \n\t Type(%s), \n\t Unspillable(%s))\n" % (
                str(self.name), str(self.neighbors), str(self.possible_colors), str(self.color), str(self.type), str(self.unspillable))

        def __repr__(self):
            return self.__str__()

        def __eq__(self, other):
            return self.name == other.name

        def __ne__(self, other):
            return not self.__eq__(other)

        def __hash__(self):
            return hash(self.name)

    def __init__(self, directed=False):
        self.__vertices = {}
        self.__directed = directed

    def add_vertex(self, name):
        if self.__vertices.get(name) is None:
            self.__vertices[name] = self.Vertex(name)

    def add_edge(self, v1, v2):
        self.__vertices[v1].neighbors.add(v2)
        if not self.__directed:
            self.__vertices[v2].neighbors.add(v1)

    # Gives a vertex given a name.
    def get_vertex(self, name):
        return self.__vertices.get(name)

    def get_most_constrained_vertex(self):
        '''
        Most constrained vertex is the one that is not yet colored and has the fewest possible colors.
        If there are more than one, the one with the most neighbors is chosen.
        '''
        least_possible_colors = sys.maxint
        most_constrained_vertex = []
        for v in filter(lambda v: v.color == None, self.__vertices.values()):
            if len(v.possible_colors) < least_possible_colors:
                least_possible_colors = len(v.possible_colors)
                most_constrained_vertex = [v.name]
            elif len(v.possible_colors) == least_possible_colors or v.unspillable:
                most_constrained_vertex.append(v.name)
        if len(most_constrained_vertex) == 0:
            return None

        # If there are more than one, the one with the most neighbors is chosen.
        most_constrained_vertex = sorted(most_constrained_vertex, key=lambda v: len(
            self.__vertices[v].neighbors), reverse=True)
        # If there are unspillable vertices, bring them to the front of the list.
        most_constrained_vertex = sorted(
            most_constrained_vertex, key=lambda v: self.__vertices[v].unspillable, reverse=True)
        return most_constrained_vertex[0]

    def get_vertices(self):
        return self.__vertices.keys()

    def get_edges(self):
        edges = []
        for v in self.__vertices:
            for neighbor in self.__vertices[v].neighbors:
                edges.append((v, neighbor))
        return edges

    def get_neighbors(self, v):
        return self.__vertices[v].neighbors

    def get_possible_colors(self, v):
        return self.__vertices[v].possible_colors

    def get_color(self, v):
        return self.__vertices[v].color

    def get_type(self, v):
        return self.__vertices[v].type

    def is_unspillable(self, v):
        return self.__vertices[v].unspillable

    def set_possible_colors(self, v, possible_colors):
        self.__vertices[v].possible_colors = set(possible_colors)

    def set_color(self, v, color):
        self.__vertices[v].color = color

    def set_type(self, v, type):
        self.__vertices[v].type = type

    def set_unspillable(self, v, unspillable):
        self.__vertices[v].unspillable = unspillable

    def __str__(self):
        out = "Undirected Graph(" if not self.__directed else "Directed Graph("
        out += str(self.__vertices) + ")"
        return out

    def __len__(self):
        return len(self.__vertices)

    def __repr__(self):
        return self.__str__()

    def __contains__(self, v):
        return v in self.__vertices


class Stack:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def get(self, i):
        return self.items[i]

    def peek(self):
        return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)


class InstGen():
    '''
    Class for generating instructions during IR and x86 gen
    Add checks for src and dst types. Dst cannot be immediate
    '''

    def __init__(self):
        self.instructions = []

    def movl(self, src, dst):
        if is_int(src):
            src = "$%s" % src
        self.instructions.append("movl %s, %s" % (str(src), str(dst)))
        return self

    def addl(self, src, dst):
        if is_int(src):
            src = "$%s" % src
        self.instructions.append("addl %s, %s" % (str(src), str(dst)))
        return self

    def negl(self, dst):
        self.instructions.append("negl %s" % str(dst))
        return self

    def subl(self, src, dst):
        if is_int(src):
            src = "$%s" % src
        self.instructions.append("subl %s, %s" % (str(src), str(dst)))
        return self

    def pushl(self, dst):
        if is_int(dst):
            dst = "$%s" % dst
        self.instructions.append("pushl %s" % str(dst))
        return self

    def popl(self, dst):
        if is_int(dst):
            dst = "$%s" % dst
        self.instructions.append("popl %s" % str(dst))
        return self

    def cmpl(self, lhs, rhs):
        if is_int(lhs):
            src = "$%s" % lhs
        self.instructions.append("cmpl %s, %s" % (str(lhs), str(rhs)))
        return self

    def jmp(self, label):
        self.instructions.append("jmp %s" % str(label))
        return self

    def jne(self, label):
        self.instructions.append("jne %s" % str(label))
        return self

    def ifeq(self, lhs, rhs, label=None):
        if is_int(lhs):
            lhs = "$%s" % lhs
        self.cmpl(lhs, rhs)
        self.jne("else_" + str(label))
        self.then_(label)
        return self

    def whileeq(self, lhs, rhs, label=None):
        if is_int(lhs):
            lhs = "$%s" % lhs
        self.cmpl(lhs, rhs)
        self.jne("endwhile_" + str(label))
        self.do_(label)

    def else_(self, label=None, jmp=True):
        if jmp:
            self.jmp("endif_" + str(label))
        self.instructions.append("else_%s:" % str(label))
        return self

    def then_(self, label=None):
        self.instructions.append("then_%s:" % str(label))
        return self

    def do_(self, label=None):
        self.instructions.append("do_%s:" % str(label))
        return self

    def endif_(self, label=None):
        self.jmp("endif_%s" % str(label))
        self.instructions.append("endif_%s:" % str(label))
        return self

    def while_(self, label=None):
        self.instructions.append("while_%s:" % str(label))
        return self
    
    def endwhile_(self, label=None):
        self.instructions.append("endwhile_%s:" % str(label))
        return self

    def call(self, label):
        self.instructions.append("call %s" % str(label))
        return self

    def orl(self, src, dst):
        if is_int(src):
            src = "$%s" % src
        self.instructions.append("orl %s, %s" % (str(src), str(dst)))
        return self

    def andl(self, src, dst):
        if (is_int(src)):
            src = "$" + str(src)
        self.instructions.append("andl %s, %s" % (str(src), str(dst)))
        return self

    def notl(self, dst):
        self.instructions.append("notl %s" % str(dst))
        return self

    def shl(self, src, dst):
        if is_int(src):
            src = "$%s" % src
        self.instructions.append("shl %s, %s" % (str(src), str(dst)))
        return self

    def shr(self, src, dst):
        if is_int(src):
            src = "$%s" % src
        self.instructions.append("shr %s, %s" % (str(src), str(dst)))
        return self

    def label(self, label):
        self.instructions.append("%s:" % str(label))
        return self

    def globl(self, symbol):
        self.instructions.append(".globl %s" % str(symbol))
        return self

    def ret(self):
        self.instructions.append("ret")
        return self

    def leave(self):
        self.instructions.append("leave")
        return self

    def raw_append(self, stmt):
        self.instructions.append(str(stmt))
        return self

    def clear(self):
        self.instructions = []


#####################
# Helper Functions
#####################
def tmpvar(prefix="tmp"):
    '''
    Generate unique temporary variable name.
    '''
    if not hasattr(tmpvar, "counter"):
        tmpvar.counter = 0
    tmpvar.counter += 1
    return prefix + "_" + datetime.now().strftime("%d") + "_" + str(tmpvar.counter)


def is_int(s):
    if (isinstance(s, int)):
        return True
    else:
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
    return s.isdigit()


def flatten_list(seq):
    '''
    Flatten 2D list into 2D list
    '''
    l = []
    for elem in seq:
        t = type(elem)
        if t is list:
            for elem2 in flatten_list(elem):
                l.append(elem2)
        else:
            l.append(elem)
    return l


def write_to_file(file, data, suffix=None):
    '''
    Write to a file with or without separate suffix
    Usage: 1. write_to_file("file_name", data, ".py")
           2. write_to_file("file_name.py", data) 
    '''
    if isinstance(suffix, str):
        head, filename = path.split(file)
        filename = path.splitext(filename)[0] + suffix
        file = path.join(head, filename)
    with open(file, "w") as f:
        for expr in data:
            f.write(str(expr) + "\n")


def read_file(filename):
    '''
    Read each line and put it in a list
    '''
    with open(filename) as f:
        return f.read().splitlines()


# CONSTANTS

#######################################
# To reduce string replication errors #
#######################################

INT = "int"
BOOL = "bool"
BIG = "big"
EAX = "%eax"
EBX = "%ebx"
ECX = "%ecx"
EDX = "%edx"
ESI = "%esi"
EDI = "%edi"
ESP = "%esp"
EBP = "%ebp"
SHIFT = 2 # Projection/Injection SHIFT for tag management
MASK = 3
FRAMEBASE = "(%ebp)"
REGISTER = "register"
STACK = "stack"
CONST = "const"
VARIABLE = "variable"
SPILLFILE = "spill.ir"
LAMBDA = "lambda"
CONDITIONAL = "conditional"
UNCONDITIONAL = "unconditional"

registers = [EAX, EBX, ECX, EDX, ESI, EDI]
num_registers = len(registers)
caller_saved_registers = [EAX, ECX, EDX]


def from_ebp(offset):
    return str(offset) + FRAMEBASE

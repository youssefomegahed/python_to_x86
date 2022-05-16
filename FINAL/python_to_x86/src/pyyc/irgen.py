import compiler
from compiler.ast import Add
from compiler.ast import UnarySub
from compiler.ast import Subscript
from compiler.ast import While
from compiler.ast import Break
import utils
from utils import InstGen
from utils import EAX, SHIFT, MASK, from_ebp, ESP

# Very Important:
# Make sure that every jump  is followed by a label
# We need it to be able to create a CFG


class IRGenVisitor(compiler.visitor.ASTVisitor):
    '''
    Convert the flattened AST into a list of IR instructions.
    The IR instructions are represented as tuples of the form:
    (opcode, arg1, arg2, ...) where the tuples resemble x86 instructions 
    with a slight modification, namely that the all arguments are represented
    as variables or constants instead of using registers or stack slots.
    '''

    def __init__(self):
        self.ir_list = []
        self.ir = InstGen()
        self.loop_label = None

    def visitModule(self, node):
        '''
        Visit the module and append the result to the IR List
        '''
        self.visit(node.node)

    def visitStmt(self, node):
        '''
        Visit each statement in the list and append the result to the IR List
        '''
        for child in node.nodes:
            self.visit(child)
        return None

    def visitPrintnl(self, node):
        '''
        Assuming only one arguments is passed to print.
        '''
        name = self.visit(node.nodes[0])
        self.ir.movl(name, EAX) \
            .pushl(EAX) \
            .call('print_any') \
            .addl(4, ESP)
        return None

    def visitAssign(self, node):
        '''
        Assign a value to a variable.
        Caveat: if the variable is a subscript, use set_subscript
        to assign the value to the subscript. This is because the 
        visitSubscript function is used to get the value of the subscript (i.e,
        when the subscript is on the right hand side of the assign).
        '''
        if isinstance(node.nodes[0], Subscript):
            # This is a subscript assignment.
            # use set_subscript(list, key, value)
            subscript = node.nodes[0]
            listname = self.visit(subscript.expr)
            key = self.visit(subscript.subs[0])
            value = self.visit(node.expr)
            key_var = utils.tmpvar()
            self.ir.pushl(value) \
                .movl(key, key_var) \
                .pushl(key_var) \
                .pushl(listname) \
                .call('set_subscript') \
                .addl(12, ESP)
            return None

        dst = self.visit(node.nodes[0])
        src = self.visit(node.expr)
        src_var_1 = utils.tmpvar()
        src_var_2 = utils.tmpvar()

        if isinstance(node.expr, Add):
            self.ir.movl(src[0], src_var_1) \
                .movl(src_var_1, dst) \
                .shr(SHIFT, dst) \
                .movl(src[1], src_var_2) \
                .shr(SHIFT, src_var_2) \
                .addl(src_var_2, dst)
        elif isinstance(node.expr, UnarySub):
            self.ir.movl(src, src_var_1) \
                .movl(src_var_1, dst) \
                .shr(SHIFT, dst) \
                .negl(dst)
        else:
            self.ir.movl(src, src_var_1) \
                .movl(src_var_1, dst)
        return None

    def visitCompare(self, node):
        '''
        Compare the values of two operands.
        '''
        op1 = self.visit(node.expr)
        op2 = self.visit(node.ops[0][1])
        op = node.ops[0][0]
        lvar = utils.tmpvar()
        rvar = utils.tmpvar()
        cmpvar = utils.tmpvar()

        control_flow_labels = [utils.tmpvar() for i in range(3)]

        self.ir.movl(op1, lvar) \
            .andl(MASK, lvar) \
            .ifeq(MASK, lvar, control_flow_labels[0]) \
            .movl(op2, rvar) \
            .movl(op1, lvar)
        if op in ['==', '!=']:
            self.ir.movl(MASK, cmpvar) \
                .notl(cmpvar) \
                .andl(cmpvar, lvar) \
                .andl(cmpvar, rvar)  \
                .pushl(lvar) \
                .pushl(rvar) \
                .call('equal' if op == '==' else 'not_equal') \
                .addl(8, ESP)
        else:
            self.ir.ifeq(rvar, lvar, control_flow_labels[1])
            if (op == 'is'):
                self.ir.movl(1, EAX)
            else:
                self.ir.movl(0, EAX)
            self.ir.else_(control_flow_labels[1])
            if (op == 'is'):
                self.ir.movl(0, EAX)
            else:
                self.ir.movl(1, EAX)
            self.ir.endif_(control_flow_labels[1])
        self.ir.else_(control_flow_labels[0]) \
            .movl(op1, lvar) \
            .movl(op2, rvar)
        if (op in ["==", "!="]):
            self.ir.shr(SHIFT, lvar) \
                .shr(SHIFT, rvar)
        self.ir.ifeq(rvar, lvar, control_flow_labels[2])
        if op in ['==', 'is']:
            self.ir.movl(1, EAX)
        else:
            self.ir.movl(0, EAX)
        self.ir.else_(control_flow_labels[2])
        if op in ['==', 'is']:
            self.ir.movl(0, EAX)
        else:
            self.ir.movl(1, EAX)
        self.ir.endif_(control_flow_labels[2]) \
            .endif_(control_flow_labels[0]) \
            .shl(SHIFT, EAX) \
            .orl(1, EAX)

        return EAX  # this is where the result is stored

    def visitIf(self, node):
        '''
        Convert test to ifeq and remove the colon from the test.
        We don't convert if-else to jumps and labels because 
        we will need to know the scope of variables in if-else during 
        liveness analysis.
        '''
        test = node.tests[0][0]
        control_flow_label = utils.tmpvar()
        self.ir.ifeq(1, self.visit(test), control_flow_label)
        self.visit(node.tests[0][1])
        if hasattr(node.else_, "nodes") and isinstance(node.else_.nodes[0], Break):
            # FIXME: This is a very hacky and dangerous way to handle loops.
            # We should have a better way to handle loops.
            # We are assuming that break statement will only be used by us in loops.
            # Although it is true, this is not a safe assumption if we want to
            # handle loops in a general way or extend the compiler in future.
            self.ir.jmp("while_" + str(self.loop_label))
            self.loop_label = None
            self.ir.else_(control_flow_label, False)
        else:
            self.ir.else_(control_flow_label)
        self.visit(node.else_)
        self.ir.endif_(control_flow_label)
        return None

    def visitBreak(self, node):
        '''
        Convert break to jmp.
        '''
        return None

    def visitWhile(self, node):
        '''
        Convert while to ifeq and remove the colon from the test.
        We don't convert while-else to jumps and labels because 
        we will need to know the scope of variables in while-else during 
        liveness analysis.
        '''
        control_flow_label = utils.tmpvar()
        self.ir.while_(control_flow_label)
        # Don't worry about test, it is an infinite loop
        self.loop_label = control_flow_label
        self.visit(node.body)
        return None

    def visitAdd(self, node):
        '''
        Mov the left hand side of plus to the dest.
        Add the right hand side of plus to the dest.
        This ensures that we are not dealing with a const as dest.
        (Assumption: the left hand side of assign is never a const)
        BigAdds go directly to CallFunc.
        '''
        op1 = self.visit(node.left)
        op2 = self.visit(node.right)
        return (op1, op2)

    def visitUnarySub(self, node):
        '''
        Negate the value of the operand.
        '''
        op = self.visit(node.expr)
        return str(op)

    def visitSubscript(self, node, dest=None):
        '''
        - get the value of the list using get_subscript(list, key)
        - put the value in the destination
        '''
        self.ir.movl(self.visit(node.subs[0]), EAX) \
            .pushl(EAX) \
            .pushl(self.visit(node.expr)) \
            .call('get_subscript') \
            .addl(8, ESP)
        return EAX

    def visitList(self, node):
        '''
        - use create_list(length) function from the runtime to create list of length
          equal to the length of the list.
        - Get the value of each element in the list and put in the right
          index using set_subscript(list, index, value)
        '''
        length = len(node.nodes)
        var = utils.tmpvar()
        self.ir.movl(length, EAX) \
            .shl(SHIFT, EAX) \
            .pushl(EAX) \
            .call('create_list') \
            .addl(4, ESP) \
            .orl(MASK, EAX) \
            .movl(EAX, var)
        for idx, v in enumerate(node.nodes):
            self.ir.pushl(self.visit(v)) \
                .movl(idx, EAX) \
                .shl(SHIFT, EAX) \
                .pushl(EAX) \
                .pushl(var) \
                .call('set_subscript') \
                .addl(12, ESP)
        # return the pointer to the list
        self.ir.movl(var, EAX)
        return EAX

    def visitDict(self, node):
        '''
        - use create_dict from runtime to create an empty dictionary
        - Put the key-value pairs in the dictionary using set_subscript
        - If dest is not None, move the dictionary to dest
        '''
        var = utils.tmpvar()
        self.ir.call('create_dict') \
            .orl(MASK, EAX) \
            .movl(EAX, var)
        for k, v in node.items:
            self.ir.pushl(self.visit(v)) \
                .pushl(self.visit(k)) \
                .pushl(var) \
                .call('set_subscript') \
                .addl(12, ESP)
        # return the pointer to the dict
        self.ir.movl(var, EAX)
        return EAX

    def visitCallFunc(self, node):
        '''
        This takes care of inject, project, bigadd, pyobjerror, istrue,
        compare, and, or, not, isint, isbool, isbig.
        '''
        #TODO(raghu): Check if the label is a function 
        args = []
        for idx, arg in enumerate(node.args):
            arg  = self.visit(arg)
            if node.node.name in ["create_closure"] and idx == 0:
                arg = "$" + arg
            args.append(arg)
        [self.ir.pushl(arg) for arg in reversed(args)]
        self.ir.call(node.node.name)
        self.ir.addl(len(node.args)*4, ESP)
        return EAX

    def visitConst(self, node):
        val = str(node.value)
        return str(val)

    def visitName(self, node):
        val = node.name
        return str(val)

    def visitAssName(self, node):
        val = node.name
        return str(val)

    def visitDiscard(self, node):
        return self.visit(node.expr)

    def visitFunction(self, node):
        '''
        This is the function definition.
        1. Change def to a label
        2. self.visit(node.code)
        3. Return the label
        '''
        self.ir.label(node.name)
        args = node.argnames
        for idx, arg in enumerate(args):
            self.ir.movl(from_ebp((idx+2) * 4), arg)
        self.visit(node.code)
        if node.name == "main":
            self.ir.movl(0, EAX)
        self.ir_list.append(self.ir.instructions)
        self.ir.clear()
        return node.name
    
    def visitReturn(self, node):
        self.ir.movl(self.visit(node.value), EAX)
        return EAX


# Helper function to get IR from the flattened AST
def get_ir_list(node):
    return compiler.visitor.walk(node,
                          IRGenVisitor()).ir_list



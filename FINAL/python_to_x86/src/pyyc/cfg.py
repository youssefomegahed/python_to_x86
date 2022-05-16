from utils import flatten_list
from utils import CONDITIONAL, UNCONDITIONAL
from utils import EBP, EAX
import liveness as lv
# import graphviz


class BasicBlock:
    def __init__(self):
        self.src_id = None
        self.tgt_id = None
        self.branch_type = None
        self.instructions = []
        self.successors = []
        self.lvsets = []
        self.eob = False

    def add_instruction(self, instruction):
        if len(self.instructions) == 0:  # first instruction in the block (leader)
            # if the first instruction is a label, then it is the leader
            if is_label(instruction):
                self.set_src_id(get_label(instruction))

        self.instructions.append(instruction)

    def set_target_id(self, target_id):
        self.tgt_id = target_id

    def set_src_id(self, src_id):
        self.src_id = src_id

    def get_target_id(self):
        return self.tgt_id

    def get_src_id(self):
        return self.src_id

    def get_instructions(self):
        return self.instructions

    def set_eob(self, eob):
        self.eob = eob

    def is_eob(self):
        return self.eob == True

    def set_branch_type(self, branch_type):
        self.branch_type = branch_type

    def get_branch_type(self):
        return self.branch_type

    def add_successor(self, successor):
        self.successors.append(successor)

    def get_successors(self):
        return self.successors

    def set_lvsets(self, lvsets):
        self.lvsets = lvsets

    def get_lvsets(self):
        return self.lvsets

    def __str__(self):
        return "BasicBlock(<BasicBlock instance at 0x%x" % (id(self)) + ">, \n" + \
            "  SrcID(" + str(self.src_id) + "), \n" + \
            "  TargetID(" + str(self.tgt_id) + "), \n" + \
            "  BranchType(" + str(self.branch_type) + "), \n" + \
            "  Successors(" + str(self.successors) + "), \n" + \
            "  Instructions(" + str(self.instructions) + "), \n" + \
            "  LiveSet(" + str(self.lvsets) + ")), \n"


class CFG:
    def __init__(self, ir):
        self.basic_blocks = []
        self.ir = ir

    def build_basic_blocks(self):
        # create a basic block for each instruction
        for idx, inst in enumerate(self.ir):
            # A leader can be label or the first instruction after
            # a jump(jmp, jne, jle, jge, jg, jl, je, jmp)
            if is_label(inst) or self.basic_blocks[-1].is_eob():
                # while is a special case
                if len(self.basic_blocks) > 0 and not self.basic_blocks[-1].is_eob():
                    self.basic_blocks[-1].set_eob(True)
                    self.basic_blocks[-1].set_target_id(get_label(inst))
                    self.basic_blocks[-1].set_branch_type(UNCONDITIONAL)
                self.basic_blocks.append(BasicBlock())
            if is_jmp(inst):
                # if the last instruction is a jump, then this is the end of the block
                # Also set the target id so that we can connect the blocks later
                self.basic_blocks[-1].set_eob(True)
                self.basic_blocks[-1].set_target_id(get_label(inst))
                self.basic_blocks[-1].set_branch_type(get_jmp_type(inst))
            self.basic_blocks[-1].add_instruction(inst)
        # mark the end of last block
        self.basic_blocks[-1].set_eob(True)

    def connect_basic_blocks(self):
        for idx, block in enumerate(self.basic_blocks):
            # check if the last instruction is an conditional jump or an unconditional jump
            if block.branch_type == UNCONDITIONAL:
                # if the last instruction is an unconditional jump, there should be only one successor
                target_block = self.get_block_by_id(block.get_target_id())
                # Stupidity Check
                if target_block is None:
                    raise RuntimeError(
                        "Unconditional jump to non-existent block: %s" % str(block.get_target_id()))
                # put it back in the list of basic blocks
                self.basic_blocks[idx].add_successor(target_block)
            elif block.branch_type == CONDITIONAL:
                # if the last instruction is a conditional jump, there should be two successors
                target_block = self.get_block_by_id(block.get_target_id())
                # Stupidity Check
                if target_block is None:
                    raise RuntimeError(
                        "Conditional jump to non-existent block: %s" % str(block.get_target_id()))
                self.basic_blocks[idx].add_successor(target_block)
                # fall through block is the last block in the list
                self.basic_blocks[idx].add_successor(self.basic_blocks[idx+1])

    def initialize_lvsets(self):
        for idx, block in enumerate(self.basic_blocks):
            [self.basic_blocks[idx].lvsets.append(set()) for i in range(
                len(block.get_instructions()) + 1)]

    # def export_cfg(self):
    #   '''
    #   Use graphviz to show the connections in graph
    #   '''
    #   g = graphviz.Digraph(format='png')
    #   g.attr('node', shape='box')
    #   for block in self.basic_blocks:
    #     if len(block.get_successors()) == 0:
    #       g.node(str(block.get_instructions()))
    #     for successor in block.get_successors():
    #       g.edge(str(block.get_instructions()),
    #       str(successor.get_instructions()))
    #   g.render('cfg')

    def build_cfg(self):
        self.build_basic_blocks()
        self.connect_basic_blocks()
        # self.export_cfg()

    def lvn(self):
        '''
        Perform LVN on the CFG
        1. Instructions that we need to handle include:
          movl, addl, negl, pushl, popl, orl, andl, notl, shr, shl
        2. Make sure to not mess with registers that are used in the IR
        3. Make sure to not do anything to stack pointer or base pointer
        4. Make sure to not handle calls and labels
        '''
        var_to_vn_map = {}
        vn_to_var_map = {}
        expr_to_vn_map = {}
        current_value_number = 0
        for idx, block in enumerate(self.basic_blocks):
            for i, inst in enumerate(block.get_instructions()):
                opcode = get_opcode(inst)
                operands = get_operands(inst)
                if opcode == 'movl':
                    src = operands[0]
                    dst = operands[1]
                    if is_register(src) or is_memory(src):
                        if is_var(dst):
                            # if is_boxed_return(block, i, src):
                            #     var_to_vn_map[dst] = current_value_number
                            #     vn_to_var_map[current_value_number] = dst
                            #     current_value_number += 1
                            # else:
                            var_to_vn_map[dst] = current_value_number
                            vn_to_var_map[current_value_number] = dst
                            current_value_number += 1
                    if is_var(src):
                        if src not in var_to_vn_map:
                            var_to_vn_map[src] = current_value_number
                            vn_to_var_map[current_value_number] = src
                            current_value_number += 1
                        src_vn = var_to_vn_map[src]
                        var_to_vn_map[dst] = src_vn
                        vn_to_var_map[src_vn] = dst
                    if is_int(src):
                        var_to_vn_map[dst] = current_value_number
                        vn_to_var_map[current_value_number] = dst
                        expr_to_vn_map[src] = ("const", current_value_number)
                        current_value_number += 1
                elif opcode == 'addl':
                    left = operands[0]
                    right = operands[1]
                    dst = operands[1]
                    # Unfortunately, because we are dealing with the IR, we will never have
                    # a situation where left and right are both constants?
                    if is_var(left) and is_var(right):
                        if left not in var_to_vn_map:
                            raise RuntimeError(
                                "Variable not in var_to_vn_map: %s" % left)
                        if right not in var_to_vn_map:
                            raise RuntimeError(
                                "Variable not in var_to_vn_map: %s" % right)
                        left_vn = var_to_vn_map[left]
                        right_vn = var_to_vn_map[right]
                        expr = '%s + %s' % (left_vn, right_vn)
                        if expr not in expr_to_vn_map:
                            expr_to_vn_map[expr] = (
                                "expr", current_value_number)
                            vn_to_var_map[current_value_number] = dst
                            var_to_vn_map[dst] = current_value_number
                            current_value_number += 1
                        else:
                            vn = expr_to_vn_map[expr][1]
                            if vn in vn_to_var_map:
                                print vn_to_var_map[vn]
                                # DO COPY FOLDING HERE
                                self.basic_blocks[idx].instructions[i] = 'movl %s, %s' % (
                                    vn_to_var_map[vn], dst)
                                print self.basic_blocks[idx].instructions[i]
                            var_to_vn_map[dst] = expr_to_vn_map[expr][1]
                            vn_to_var_map[expr_to_vn_map[expr][1]] = dst
                        print expr_to_vn_map, inst
                    elif is_int(left) and is_var(right):
                        if right not in var_to_vn_map:
                            raise RuntimeError(
                                "Variable not in var_to_vn_map: %s" % right)
                        expr = '%s + %s' % (left, right)
                        if expr not in expr_to_vn_map:
                            expr_to_vn_map[expr] = (
                                "expr", current_value_number)
                            vn_to_var_map[current_value_number] = dst
                            var_to_vn_map[dst] = current_value_number
                            current_value_number += 1
                        else:
                            vn = expr_to_vn_map[expr][1]
                            if vn in vn_to_var_map:
                                # DO COPY FOLDING HERE
                                self.basic_blocks[idx].instructions[i] = 'movl %s, %s' % (
                                    vn_to_var_map[vn], dst)
                            var_to_vn_map[dst] = expr_to_vn_map[expr][1]
                            vn_to_var_map[expr_to_vn_map[expr][1]] = dst
        return self.get_ir()

    def run_dead_store_elimination(self):
        '''
        Perform dead store elimination on the CFG
        '''
        # run fixed point analysis once so that the lvsets are populated
        no_dead_store = False
        while not no_dead_store:
            old_inst_count = self.get_total_inst_count()
            new_inst_count = self.dead_store_elimination()
            no_dead_store = old_inst_count == new_inst_count
        return self.get_ir()

    def dead_store_elimination(self):
        self.run_fixed_point_liveness_analyis()
        for idx, block in enumerate(self.basic_blocks):
            lvsets = block.get_lvsets()

            # Mark and Sweep (Mark with None)
            for i, inst in enumerate(block.get_instructions()):
                opcode = get_opcode(inst)
                operands = get_operands(inst)
                if opcode in ['movl', 'addl', 'andl', 'orl', 'shl', 'shr']:
                    dst = operands[1]
                    if is_var(dst) and dst not in lvsets[i + 1]:
                        self.basic_blocks[idx].instructions[i] = None
                elif opcode in ['negl', 'notl']:
                    dst = operands[0]
                    if is_var(dst) and dst not in lvsets[i + 1]:
                        self.basic_blocks[idx].instructions[i] = None

            # Remove None instructions
            for i, inst in enumerate(block.get_instructions()):
                if inst is None:
                    self.basic_blocks[idx].instructions.pop(i)
            self.basic_blocks[idx].set_lvsets([])
        return self.get_total_inst_count()

    def get_total_inst_count(self):
        total_inst_count = 0
        for block in self.basic_blocks:
            total_inst_count += len(block.get_instructions())
        return total_inst_count

    def get_ir(self):
        ir = []
        for block in self.basic_blocks:
            ir.append(block.get_instructions())
        return flatten_list(ir)

    def run_fixed_point_liveness_analyis(self):
        # get the old global liveness sets, run liveness analysis, and get the new global liveness sets
        # if the new global liveness sets are the same as the old global liveness sets, then we have a fixed point
        # otherwise, we have not yet reached a fixed point
        self.initialize_lvsets()
        is_fixed_point = False
        fixed_point_lvsets = []
        while not is_fixed_point:
            old_lvsets = self.get_global_lvsets()
            new_lvsets = self.liveness_analysis()
            is_fixed_point = old_lvsets == new_lvsets
            fixed_point_lvsets = new_lvsets if is_fixed_point else fixed_point_lvsets
        return fixed_point_lvsets

    def liveness_analysis(self):
        # reverse enumerate the basic blocks
        for idx, block in reversed(list(enumerate(self.basic_blocks))):
            # if the block has successors, then the lvset[-1] of the block is the union of the lvset[0] of the successors
            if len(block.get_successors()) > 0:
                for succ in block.get_successors():
                    block.lvsets[-1] = block.lvsets[-1].union(
                        succ.get_lvsets()[0])
            lvsets = lv.analyze_liveness_with_cfg(
                block.get_instructions(), block.get_lvsets())
            self.basic_blocks[idx].set_lvsets(lvsets)
        return self.get_global_lvsets()

    def get_global_lvsets(self):
        global_lvsets = []
        for idx, block in enumerate(self.basic_blocks):
            if idx == 0:
                global_lvsets.append(block.get_lvsets())
            else:
                global_lvsets.append(block.get_lvsets()[1:])
        global_lvsets = flatten_list(global_lvsets)
        # we need to flatten it is because the lvsets are a list of lists
        return global_lvsets

    def get_block_by_id(self, id):
        for block in self.basic_blocks:
            if block.get_src_id() == id:
                return block
        return None

    def get_blocks(self):
        return self.basic_blocks

    def __str__(self):
        out = "CFG("
        for block in self.basic_blocks:
            out += str(block)
            out += "\n"
        out += ")"
        return out


def is_label(instruction):
    return True if instruction.endswith(":") else False


def is_jmp(instruction):
    return True if instruction.startswith("jmp") or \
        instruction.startswith("jle") or  \
        instruction.startswith("jge") or  \
        instruction.startswith("jne") or  \
        instruction.startswith("je") or  \
        instruction.startswith("jg") or  \
        instruction.startswith("jl") else False


def get_jmp_type(instruction):
    opcode = instruction.split(" ")[0]
    if opcode == "jmp":
        return UNCONDITIONAL
    elif opcode == "jle" or opcode == "jge" or opcode == "jne" or opcode == "je" or opcode == "jg" or opcode == "jl":
        return CONDITIONAL


def get_label(instruction):
    # if the instruction is a jump then, just returnt the label
    # which is the last word in the instruction.
    # We can get the id from this using get_id_from_label
    if is_jmp(instruction):
        return instruction.split()[1]
    return instruction.split(":")[0]


def get_opcode(instruction):
    return instruction.split()[0]


def get_operands(instruction):
    return instruction.replace(',', ' ').split()[1:]


def is_var(operand):
    var_flag = True
    if '%' in operand:
        var_flag = False
    elif '$' in operand:
        var_flag = False
    return var_flag


def is_int(operand):
    if operand.startswith("$"):
        return True
    if (isinstance(operand, int)):
        return True
    else:
        if operand[0] in ('-', '+'):
            return operand[1:].isdigit()
    return operand.isdigit()


def is_register(operand):
    return True if operand.startswith('%') else False


def is_memory(operand):
    return True if EBP in operand else False

def is_boxed_return(block, idx, operand):
    if idx < 2:
        return False
    if operand == EAX and \
        block.get_instructions()[idx - 2].replace(',', 
            ' ').split()[1] == "inject_int":
        return True
    return False
        

from ctypes import util
import utils
from utils import Graph
from utils import caller_saved_registers, EBP, ESP
import cfg


def add_all_vertices(graph, ir):
    '''
    Add all the vertices in the IR to the graph, 
    it could be a register or a variable
    param graph: the graph to add the vertices to
    param ir: the IR to get the vertices from
    '''
    for idx, inst in enumerate(ir):
        op = inst.split()
        if len(op) == 2:
            if op[0] in ["notl", "negl", "pushl"]:
                op1 = op[1].strip(",")
                if "$" not in op1:
                    graph.add_vertex(op1)
        elif len(op) == 3:
            op1 = op[1].strip(",")
            op2 = op[2].strip(",")
            if "$" not in op1 and EBP not in op1 and ESP not in op1:
                graph.add_vertex(op1)
            if "$" not in op2 and EBP not in op2 and ESP not in op2:
                graph.add_vertex(op2)
    return graph


def create_interference_graph(ir):
    '''
    Create the interference graph from the IR
    param: ir: the IR
    return: the interference graph
    '''
    # addedge(t, v) \forall v \in lvset_{after}(inst), where v != t or v != s and inst == "movl s, t"

    # addedge(t, v) \forall v \in lvset_{after}(inst), where v != t and inst == "addl s, t"

    # addedge(r, v) \forall r \in caller_saved_registers and v \in lvset_{after}(inst), where inst == "call label"

    graph = Graph()
    cfg1 = cfg.CFG(ir)
    cfg1.build_cfg()
    lvsets = cfg1.run_fixed_point_liveness_analyis()
    # lvsets = lv.analyze_liveness(ir)
    

    # Add all vertices to the graph
    graph = add_all_vertices(graph, ir)

    

    for idx, inst in enumerate(ir):
        op = inst.split()
        if not op:
            continue
        op = op[0]
        sset = save_set(inst, op)
        for v in lvsets[idx + 1] - sset:
            iset = interference_set(inst, op)
            map(lambda x: graph.add_vertex(x), iset)
            map(lambda x: graph.add_edge(x, v), iset)
    return graph

def save_set(inst, opcode):
    '''
    Get the save set for the given instruction
    param inst: the instruction
    param ir_ig_inst_save_map: the lookup table
    return: the save set
    '''
    # lookup table for ensuring that we are not creating a self-edge or a redundant edge
    ir_ig_inst_save_map = {"movl": [1, 2], "addl": [2], "negl": [],
                           "pushl": [], "popl": [], "call": [],
                           "cmpl": [1, 2], "else": [], "endif": [],
                           "orl": [2], "andl": [2], "notl": [],
                           "shr": [2], "shl": [2]}

    sset = set([])
    for operand in ir_ig_inst_save_map.get(opcode, []):
        sset.add(inst.split()[operand].strip(","))

    return sset

def interference_set(inst, opcode):
    '''
    Get the interference set for the given instruction
    param inst: the instruction
    param ir_ig_inst_int_map: the lookup table
    return: the interference set
    '''
    # lookup table containing all the variables/registers that interfere with the given variable
    ir_ig_inst_int_map = {"movl": [2], "addl": [2], "negl": [1],
                          "pushl": [], "popl": [], "call": caller_saved_registers,
                          "cmpl": [2], "else": [], "endif": [],
                          "orl": [2], "andl": [2], "notl": [1],
                          "shr": [2], "shl": [2]}

    iset = set([])
    for operand in ir_ig_inst_int_map.get(opcode, []):
        if isinstance(operand, int):
            iset.add(inst.split()[operand].strip(","))
        else:
            iset.add(operand)
        
        # remove EBP and ESP from the set as they might be used for function calls in IR
        iset = iset - set([EBP, ESP])
    return iset

import interferencegraph as ig
import color_and_spill as cs
from x86gen import x86CodeGen
import utils
import cfg

def reg_alloc(ir_list):
    x86asm_list = []
    # Run register allocation for each function
    # ir_list contains ir for every function in the program 
    # as a list
    for ir in ir_list:
        func_name = ir[0][:-1]
        
        # Run dead store elimination
        cfg_dse = cfg.CFG(ir)
        cfg_dse.build_cfg()
        ir = cfg_dse.run_dead_store_elimination()
        utils.write_to_file("dse" + func_name + ".ir", ir)

        cfg_lvn = cfg.CFG(ir)
        cfg_lvn.build_cfg()
        ir = cfg_lvn.lvn()
        utils.write_to_file("lvn_" + func_name + ".ir", ir)

        # Generate Interference Graph
        interference_graph = ig.create_interference_graph(ir)

        # # Allocate Registers for the nodes in the interference graph
        graph, ir = cs.color_and_spill(interference_graph, ir)

        # # Generate x86 Assembly
        x86asm = x86CodeGen().x86gen(graph, ir[1:], func_name=func_name)
        x86asm_list.append(x86asm)
    return x86asm_list

import compiler
import utils
import argparse
import uniquify as uniq
import heapify as hpfy
import closure as clsr
import explicate
import flatten
import irgen
import os
import reg_alloc as ra

argparser = argparse.ArgumentParser(
    description='Compile python P_0 to x86 assembly')
argparser.add_argument('filename', metavar='filename', type=str,
                       help='the python file to compile')
args = argparser.parse_args()
filename = args.filename


raw_ast = compiler.parseFile(filename)

uniquified_ast = uniq.get_uniquified_ast(raw_ast)

heap_vars = hpfy.get_heap_vars(uniquified_ast)
heapified_ast = hpfy.get_heapified_ast(uniquified_ast)

closurified_ast = clsr.get_converted_ast(heapified_ast, heap_vars)

# Explicate the Raw AST
explicit_ast = explicate.get_explicated_ast(closurified_ast)

fname = os.path.splitext(filename)[0] # filename without the extension
utils.write_to_file(fname+ "_flat", flatten.get_flattened_statements(explicit_ast), ".py")


# Flatten the Explicit AST
flattened_ast = flatten.get_flattened_ast(explicit_ast)


# # Generate IR
ir_list = irgen.get_ir_list(flattened_ast)

# print IR to the .ir file for debugging
utils.write_to_file(fname + "_flat", utils.flatten_list(ir_list), ".ir")

# Register Allocation and Assigning Home
x86asm_list = ra.reg_alloc(ir_list)


utils.write_to_file(filename, utils.flatten_list(x86asm_list), suffix=".s")

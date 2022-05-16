# THIS IS THE OLD VERSION OF THE LIVENESS ANALYSIS. IT IS NOT USED ANYMORE.
# # Bottom Up: lvset(before) = (lvset(after) - Write(CurrentInstruction)) U Read(CurrentInstruction)
# # lvset means live variable set
# def analyze_liveness(ir):
#     # Initialize the live variables
#     lvsets = []
#     # Allocate ir length + 1 for the last lvsets (end of program)
#     [lvsets.append(set()) for i in range(len(ir) + 1)]
#     for idx, inst in reversed(list(enumerate(ir))):
#         lvsets[idx] = (lvsets[idx + 1] - write(inst)) | read(inst)
#     return lvsets


def analyze_liveness_with_cfg(ir, lvsets):
    # lvsets[LAST_INSTRUCTION] is never evaluated because it is the end of the block.
    # But technically, it is the result of the first instructions of the successor blocks.
    for idx, inst in reversed(list(enumerate(ir))):
        lvsets[idx] = (lvsets[idx + 1] - write(inst)) | read(inst)
    return lvsets

# inst is of the form (op, args)
# FIXME: print needs to be handled
ir_read_inst_map = {"movl": [1], "addl": [1, 2], "negl": [1],
                    "pushl": [1], "call": [], "cmpl": [1, 2],
                    "orl": [1, 2], "andl": [1, 2], "notl": [1],
                    "shr": [1, 2], "shl": [1, 2]}
ir_write_inst_map = {"movl": [2], "addl": [2], "negl": [1],
                     "pushl": [], "call": [], "cmpl": [],
                     "orl": [2], "andl": [2], "notl": [1],
                     "shr": [2], "shl": [2]}


def rw_decorator(func):
    def wrapper(inst):
        op = inst.split()
        rwset = set()
        if op == []:
            return rwset
        op = op[0]
        vars = func(inst, op)
        for v in vars:
            arg = inst.split()[v].strip(",")
            if "$" not in arg and not "%" in arg:
                rwset.add(arg)
        return rwset
    return wrapper


@rw_decorator
def read(inst, op):


    # call is an exception
    # During dead store eliminination we 
    # need to know if the call is direct or indirect.
    # We need to add the indirect calls to the read set
    # because they might be of the form:
    # call get_fun_ptr
    # addl $4, % esp
    # movl % eax, tmp_13_501
    # movl tmp_13_501, tmp_13_216
    # pushl n_1
    # pushl tmp_13_199
    # pushl l_1
    # pushl f_1
    # pushl tmp_13_183
    # call tmp_13_216
    # And we should not remove the tmp_13_216 from the instruction list
    # from the dead store elimination phase as it is used in the next
    # instruction.
    if op == "call":
        return [1] if is_indirect_call(inst) else []
    return ir_read_inst_map.get(op, [])


@rw_decorator
def write(inst, op):
    return ir_write_inst_map.get(op, [])


def is_indirect_call(inst):
    operand = inst.split()[1]
    if operand in [
        "get_fun_ptr",
        "get_free_vars",
        "print_any",
        "input",
        "create_closure",
        "is_int",
        "is_true",
        "add",
        "error_pyobj",
        "is_bool",
        "is_big",
        "project_int",
        "project_bool",
        "project_big",
        "inject_int",
        "inject_bool",
        "inject_big",
        "set_subscript",
        "equal",
        "not_equal",
        "get_subscript",
        "create_list",
        "create_dict",
        "*%eax",
    ]:
        return False
    if operand.startswith("lambda_"):
        return False
    return True

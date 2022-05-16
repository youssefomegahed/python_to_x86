import utils
from utils import registers, num_registers, CONST
from utils import EAX, EBX, ECX, EDX, ESP, EBP, ESI, EDI, from_ebp, REGISTER
from utils import InstGen


class x86CodeGen():
    def __init__(self, ):
        self.x86asm = InstGen()

    def x86gen(self, graph, ir, func_name="main"):
        stack = utils.Stack()
        colored_vertices = set(
            filter(lambda x: graph.get_color(x) != None, graph.get_vertices()))
        colored_vertices_color = set(
            map(lambda x: graph.get_color(x), colored_vertices))
        offset = max(colored_vertices_color.union(([0])))
        offset = max(4*(offset - num_registers + 1), 0)
        global_offset = offset
        # Setup Assembly Prologue
        self.x86asm.globl(func_name) \
                .label(func_name) \
                .pushl(EBP) \
                .movl(ESP, EBP) \
                .subl(global_offset, ESP) \
                .pushl(EDI) \
                .pushl(ESI) \
                .pushl(EBX) \
                .raw_append("")

        for line in ir:
                stmt = line.split()
                if not stmt:
                    self.x86asm.raw_append(line)
                    continue
                opcode = stmt[0]
                for i, x in enumerate(stmt[1:]):
                    name = x.strip(',')
                    loc = name
                    if name in graph.get_vertices():
                        color = graph.get_color(name)
                        if color >= num_registers:
                            offset = -4*(color-num_registers + 1)
                            loc = from_ebp(offset=offset)
                        else:
                            loc = registers[color]
                    stmt[i+1] = x.replace(name, loc)

                if opcode == "movl" and stmt[1] == stmt[2] + ',':
                    continue


                if opcode == "call":
                    op1 = stmt[1]
                    if op1 in registers:
                        self.x86asm.call("*" + op1)
                    else:
                        self.x86asm.call(op1)

                else:
                    self.x86asm.raw_append(' '.join(stmt))

        # Setup Assembly Epilogue/Teardown
        self.x86asm.raw_append("") \
                .popl(EBX) \
                .popl(ESI) \
                .popl(EDI) \
                .addl(global_offset, ESP) \
                .leave() \
                .ret() \
                .raw_append("")
        return self.x86asm.instructions

import utils
from utils import num_registers, registers, REGISTER, caller_saved_registers, EBP
from utils import SPILLFILE
import interferencegraph as ig


def color(graph):
    # Mapping: [0: %eax, 1: %ebx, 2: %ecx, 3: %edx, 4: %esi, 5: %edi]
    colored_vertices = filter(lambda x: graph.get_color(
        x) is not None, graph.get_vertices())
    num_colors = num_registers + len(colored_vertices)

    # Initialize possible colors to num colors
    map(lambda vertex: graph.set_possible_colors(
        vertex, range(num_colors)), graph.get_vertices())  

    # Assign colors to (caller saved registers) in the graph
    map(lambda vertex: graph.set_color(vertex, registers.index(vertex))
        if graph.get_type(vertex) == REGISTER and vertex in caller_saved_registers else None, graph.get_vertices())

    

    uncolored_vertices = True
    # While there are uncolored nodes
    while uncolored_vertices:
        # Remove colors that are already used in a given vertex from the possible colors of the neighboring vertices
        for vertex in filter(lambda x: graph.get_color(x) is not None, graph.get_vertices()):
            vertex_color = graph.get_color(vertex)
            graph.set_possible_colors(vertex, set([vertex_color]))
            for neighbor in graph.get_neighbors(vertex):
                graph.set_possible_colors(
                    neighbor, graph.get_possible_colors(neighbor) - set([vertex_color]))

        # Get the vertex with the least possible colors
        most_constrained_vertex = graph.get_most_constrained_vertex()
        if most_constrained_vertex is None:
            uncolored_vertices = False
            break

        color = num_colors
        if len(graph.get_possible_colors(most_constrained_vertex)) == 0:
            num_colors += 1
            for vertex in filter(lambda x: graph.get_color(x) is None, graph.get_vertices()):
                graph.set_possible_colors(
                    vertex, graph.get_possible_colors(vertex) | set([color]))
        else:
            color = min(graph.get_possible_colors(most_constrained_vertex))
        graph.set_color(most_constrained_vertex, color)

    return graph


def generate_spillcode(ir, graph):
    output = utils.InstGen()
    spilled = False

    for line in ir:
        stmt = list(map(lambda x: x.strip(','), line.split()))
        if not stmt:
            continue

        opcode = stmt[0]
        if opcode == 'movl':
            src = stmt[1]
            dst = stmt[2]
            if graph.get_vertex(src) is not None or graph.get_vertex(dst) is not None or EBP in src:
                    if EBP in src and graph.get_color(dst) >= num_registers:
                        tmpvar = utils.tmpvar()
                        output.movl(src, tmpvar) \
                            .movl(tmpvar, dst)
                        graph.add_vertex(tmpvar)
                        graph.set_unspillable(tmpvar, True)
                        spilled = True
                    else:
                        output.raw_append(line)
            elif (graph.get_color(src) >= num_registers and
                  graph.get_color(dst) >= num_registers and
                  graph.get_color(src) != graph.get_color(dst)):
                tmpvar = utils.tmpvar()
                output.movl(src, tmpvar) \
                    .movl(tmpvar, dst)
                graph.add_vertex(tmpvar)
                graph.set_unspillable(tmpvar, True)
                spilled = True
            else:
                output.raw_append(line)
        elif opcode == 'addl':
            src = stmt[1]
            dst = stmt[2]
            if graph.get_vertex(dst) and graph.get_color(dst) >= num_registers:
                tmpvar = utils.tmpvar()
                output.movl(dst, tmpvar) \
                    .addl(src, tmpvar) \
                    .movl(tmpvar, dst)
                graph.add_vertex(tmpvar)
                graph.set_unspillable(tmpvar, True)
                spilled = True
            else:
                output.raw_append(line)
        elif opcode in ['shr', 'shl']:
            src = stmt[1]
            dst = stmt[2]
            if graph.get_vertex(dst) and graph.get_color(dst) >= num_registers:
                tmpvar = utils.tmpvar()
                output.movl(dst, tmpvar)
                if opcode == 'shr':
                    output.shr(src, tmpvar)
                else:
                    output.shl(src, tmpvar)
                output.movl(tmpvar, dst)
                graph.add_vertex(tmpvar)
                graph.set_unspillable(tmpvar, True)
                spilled = True
            else:
                output.raw_append(line)
        else:
            output.raw_append(line)
    return (output.instructions, spilled)


def color_and_spill(graph, IR):
    graph = color(graph)
    spilled = True
    newIR, spilled = generate_spillcode(IR, graph)
    oldIR = newIR
    roundNo = 1
    while spilled:
        utils.write_to_file(SPILLFILE, newIR)
        spilled_graph = ig.create_interference_graph(
            utils.read_file(SPILLFILE))
        #add stack colors and unspill to new graph
        for vertex in graph.get_vertices():
            col = graph.get_color(vertex)
            if col >= num_registers:
                spilled_graph.set_color(vertex, col)
            if graph.is_unspillable(vertex):
                spilled_graph.set_unspillable(vertex, True)

        spilled_graph = color(spilled_graph)
        oldIR = newIR
        newIR, spilled = generate_spillcode(
            utils.read_file(SPILLFILE), spilled_graph)
        graph = spilled_graph
        utils.write_to_file(SPILLFILE, oldIR)
        roundNo += 1
    return (graph, oldIR)

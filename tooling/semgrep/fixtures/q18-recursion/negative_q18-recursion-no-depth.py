def walk(node, depth):
    if depth > 64:
        raise ValueError
    return walk(node.next, depth + 1)

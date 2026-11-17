def walk(node, depth):
    if depth > 64:
        raise ValueError
    return walk(node.next, depth + 1)

def visit(root):
    stack = [root]
    while stack:
        node = stack.pop()
        stack.extend(node.children)

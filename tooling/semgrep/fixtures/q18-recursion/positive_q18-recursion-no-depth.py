def walk_a(node):
    return walk_a(node.next)

def walk_b(node):
    walk_b(node.next)
    return None


"""
Ukkonen linear time suffix tree building algorithm
and various applications
"""

import collections


"""
To get really O(N) performance we must not copy chunks of `s`, but instead
refer to it substrings using this lightweight wrapper
"""
class StringView(object):
    def __init__(self, s, start, end):
        self.s = s
        self.start = start
        self.end = end
        assert self.start <= self.end

    def get(self, ind):
        pos = self.start + ind
        if self.start <= pos < self.end:
            return self.s[pos]
        raise IndexError(self, ind)

    def cutprefix(self, amount):
        assert amount <= self.length()
        return StringView(self.s, self.start + amount, self.end)

    def length(self):
        return self.end - self.start

    def __repr__(self):
        return 'S(%s)' % repr(str(self))

    def __str__(self):
        return self.s[self.start: self.end]

class Edge(object):
    def __init__(self, label, node):
        self.label = label
        self.node = node

class Node(object):
    def __init__(self):
        # {character: Edge}
        self.edges = {}
        # If current node represents string `s`, successor points to a node 
        # representing s[1:] (or None if this is root)
        self.successor = None
        # Parent of this node, this is set up in the end of build
        self.parent = None
        # If we follow this label in parent, we will get into self
        self.edge_label = None

class Position(object):
    def __init__(self, node, edge=None, offset=0):
        # Node 
        self.node = node
        # Edge coming from node
        self.edge = edge
        # How many characters away from node
        self.offset = offset

    def __repr__(self):
        if self.edge is None:
            return 'Position(%r)' % self.node
        else:
            return 'Position(%r, %r, %d)' % (self.node, self.edge, self.offset)
 
def follow(position, path):
    """Follow `path` from current position. Path must exist"""
    runner = Position(position.node, position.edge, position.offset)
    while path.length():
        if runner.edge is None:
            runner.edge = runner.node.edges[path.get(0)]
            runner.offset = 0
        edge_left = runner.edge.label.length() - runner.offset
        if path.length() >= edge_left:
            # path exceeds current edge, follow to node
            runner.node = runner.edge.node
            runner.edge = None
            path = path.cutprefix(edge_left)
        else:
            # path ends on this node
            runner.offset += path.length()
            break
    return runner

def get_path(node):
    result = []
    while node.parent is not None:
        result.append(node.edge_label)
        node = node.parent
    return list(reversed(result))

def set_parent_pointers(root):
    stack = collections.deque([root])
    while stack:
        node = stack.pop()
        for c, edge in node.edges.iteritems():
            edge.node.parent = node
            edge.node.edge_label = edge.label
            stack.append(edge.node)

def build(s):
    root = Node()
    position = Position(root)
    ask_for_successor = None
    for i, c in enumerate(s):
        while True:
            if position.edge is None:
                if c in position.node.edges:
                    position = follow(position, StringView(s, i, i + 1))
                    break
                else:
                    position.node.edges[c] = Edge(StringView(s, i, len(s)), Node())
                    successor = position.node.successor
                    if successor is None:
                        break
                    position = Position(successor)
            else:
                if position.edge.label.get(position.offset) == c:
                    position = follow(position, StringView(s, i, i + 1))
                    break

                middle_node = Node()

                # (1) Previously we asked that a new node will be created
                # and we want it to be that guy successor
                if ask_for_successor is not None:
                    ask_for_successor.successor = middle_node
                    ask_for_successor = None

                edge = position.edge

                start_half_edge = Edge(
                    StringView(
                        s,
                        edge.label.start,
                        edge.label.start + position.offset
                    ),
                    middle_node
                )
                end_half_edge = Edge(
                    StringView(
                        s,
                        edge.label.start + position.offset,
                        edge.label.end
                    ),
                    position.edge.node
                )

                position.node.edges[start_half_edge.label.get(0)] = start_half_edge
                middle_node.edges[end_half_edge.label.get(0)] = end_half_edge
                middle_node.edges[c] = Edge(StringView(s, i, len(s)), Node())

                successor = position.node.successor
                if successor is not None:
                    new_position = follow(Position(successor), start_half_edge.label)
                else:
                    assert position.node is root
                    new_position = follow(Position(root), start_half_edge.label.cutprefix(1))

                if new_position.edge is None:
                    middle_node.successor = new_position.node
                else:
                    # The node will be created at (1) and we ask to fill our successor field when it's done
                    ask_for_successor = middle_node

                position = new_position

    set_parent_pointers(root)

    return root

def find(node, s):
    """Find if string `s` is contained in suffix tree `node`"""
    position = Position(node)
    for c in s:
        if position.edge is None:
            if c not in position.node.edges:
                return None
            position.edge = position.node.edges[c]
            position.offset = 0
        if c != position.edge.label.get(position.offset):
            return None
        position.offset += 1
        if position.offset == position.edge.label.length():
            position.node = position.edge.node
            position.edge = None
    return position

def find_longest_repeating_substring(s):
    forbidden_symbol = '\x00'
    assert forbidden_symbol not in s
    suffix_tree = build(s + forbidden_symbol)

    def dfs(node, total_len):
        assert len(node.edges) != 1
        if not len(node.edges):
            return None

        # This node has multiple children - thus string is met multiple times
        best = (total_len, node)

        for c, edge in node.edges.iteritems():
            total_len += edge.label.length()
            res = dfs(edge.node, total_len)
            if res is not None:
                best = max(best, res)
            total_len -= edge.label.length()

        return best

    max_len, node = dfs(suffix_tree, 0)
    result = get_path(node)
    return ''.join(str(v) for v in result)

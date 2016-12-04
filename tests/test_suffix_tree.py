
import pytest
from algolib.suffix_tree import *
import algolib.suffix_array

def test_find():
    s = "A quick brown fox jumps over a lazy dog$"
    tree = build(s)
    assert traverse(Position(tree), 'a l') is not None
    assert traverse(Position(tree), 'f n') is None

def test_lrs():
    assert find_longest_repeating_substring("""
    In computer science, a suffix tree (also called PAT tree or, in an earlier form, position tree) is a compressed trie containing all the suffixes of the given text as their keys and positions in the text as their values. Suffix trees allow particularly fast implementations of many important string operations.
    The construction of such a tree for the string S {\displaystyle S} S takes time and space linear in the length of S {\displaystyle S} S. Once constructed, several operations can be performed quickly, for instance locating a substring in S {\displaystyle S} S, locating a substring if a certain number of mistakes are allowed, locating matches for a regular expression pattern etc. Suffix trees also provide one of the first linear-time solutions for the longest common substring problem. These speedups come at a cost: storing a string's suffix tree typically requires significantly more space than storing the string itself.
    """) == ' locating a substring i'

def compare_trees(tree1, tree2):
    stack = collections.deque([(tree1, tree2)])
    while stack:
        node1, node2 = stack.pop()
        if str(node1.edge_label) != str(node2.edge_label):
            return False
        if node1.edges.keys() != node2.edges.keys():
            return False
        for c, edge1 in node1.edges.iteritems():
            edge2 = node2.edges[c]
            print c, edge1.label, edge2.label
            if str(edge1.label) != str(edge2.label):
                # print get_path(node1), get_path(node2)
                # print node1, node2
                # print node1.edges, node2.edges
                # print edge1.label, edge2.label
                return False
            stack.append((edge1.node, edge2.node))
    return True

@pytest.mark.parametrize('insert_dollar', [False, True], ids=['', 'with_dollar'])
def test_b2b_naive_implementation(sample_str, insert_dollar):
    if insert_dollar:
        sample_str += '$'
    correct = build_naive(sample_str)
    got = build(sample_str)
    assert compare_trees(correct, got)

def test_b2b_suffix_array(sample_str):
    dollar_sign = '\xff'
    sample_str += dollar_sign
    correct = algolib.suffix_array.suffix_array_ks(sample_str)
    got = convert_to_suffix_array(build(sample_str), dollar_sign)
    assert correct == got
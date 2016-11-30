
import pytest
from suffix_tree import *

def test_find():
    s = "A quick brown fox jumps over a lazy dog$"
    tree = build(s)
    assert find(tree, 'a l') is not None
    assert find(tree, 'f n') is None

def test_lrs():
    assert find_longest_repeating_substring("""
    In computer science, a suffix tree (also called PAT tree or, in an earlier form, position tree) is a compressed trie containing all the suffixes of the given text as their keys and positions in the text as their values. Suffix trees allow particularly fast implementations of many important string operations.
    The construction of such a tree for the string S {\displaystyle S} S takes time and space linear in the length of S {\displaystyle S} S. Once constructed, several operations can be performed quickly, for instance locating a substring in S {\displaystyle S} S, locating a substring if a certain number of mistakes are allowed, locating matches for a regular expression pattern etc. Suffix trees also provide one of the first linear-time solutions for the longest common substring problem. These speedups come at a cost: storing a string's suffix tree typically requires significantly more space than storing the string itself.
    """) == ' locating a substring i'
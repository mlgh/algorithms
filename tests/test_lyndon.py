
from algolib.lyndon import *

def test_factorize_lyndon_b2b(sample_str):
    correct = list(factorize_lyndon_naive(sample_str))
    got = list(factorize_lyndon(sample_str))
    assert correct == got

def test_lex_min_rotation(sample_str):
	assert lex_min_rotation_naive(sample_str) == lex_min_rotation(sample_str)

def test_lex_min_rotation_suffix_array(sample_str):
	assert lex_min_rotation_naive(sample_str) == lex_min_rotation_suf_arr(sample_str)

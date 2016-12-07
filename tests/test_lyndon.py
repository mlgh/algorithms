
from algolib.lyndon import *

def test_factorize_lyndon_b2b(sample_str):
    correct = list(factorize_lyndon_naive(sample_str))
    got = list(factorize_lyndon(sample_str))
    assert correct == got


import pytest

from suffix_array import *

def test_naive():
	assert suffix_array_naive('abacaba') == [0, 4, 2, 6, 1, 5, 3]

test_cases = """
abacaba
abaaaaaaaaaa
aaaaaaaaaaaaaaaa
aacbacbcabccbcbabacbabacbabaaabaaaaabbbbbbbbbbccccccccccaa
a quick brown fox jumps over a lazy dog
aaaaaaaaaaabbbbbbbbbbbbbcccccccccccccaaaaaaaaabbbbbbcccccccaaaabbbccccaabbccabc
""".strip().split()

@pytest.mark.parametrize('s', test_cases)
def test_b2b_kmr(s):
	correct = suffix_array_naive(s)
	kmr_version = suffix_array_kmr(s)
	assert correct == kmr_version

@pytest.mark.parametrize('s', test_cases)
def test_b2b_ks(s):
	correct = suffix_array_naive(s)
	ks_version = suffix_array_ks(s)
	assert correct == ks_version

def common_prefix(s1, s2):
	ans = 0
	while ans < len(s1) and ans < len(s2) and s1[ans] == s2[ans]:
		ans += 1
	return ans

@pytest.mark.parametrize('s', test_cases)
def test_lcp_kasai(s):
	suf_arr = suffix_array_ks(s)
	lcp = lcp_kasai(s, suf_arr)
	for rank in xrange(len(suf_arr) - 1):
		pos1 = suf_arr[rank]
		pos2 = suf_arr[rank + 1]
		assert common_prefix(s[pos1:], s[pos2:]) == lcp[rank]


import pytest

from suffix_array import *

def test_naive():
	assert suffix_array_naive('abacaba') == [0, 4, 2, 6, 1, 5, 3]

def test_b2b_kmr(sample_str):
	correct = suffix_array_naive(sample_str)
	kmr_version = suffix_array_kmr(sample_str)
	assert correct == kmr_version

def test_b2b_ks(sample_str):
	correct = suffix_array_naive(sample_str)
	ks_version = suffix_array_ks(sample_str)
	assert correct == ks_version

def test_b2b_ks_ext(sample_str):
	correct = suffix_array_naive(sample_str)
	ks_version = suffix_array_ks_ext(sample_str)
	assert correct == ks_version


def common_prefix(s1, s2):
	ans = 0
	while ans < len(s1) and ans < len(s2) and s1[ans] == s2[ans]:
		ans += 1
	return ans

def test_lcp_kasai(sample_str):
	suf_arr = suffix_array_ks(sample_str)
	lcp = lcp_kasai(sample_str, suf_arr)
	for rank in xrange(len(suf_arr) - 1):
		pos1 = suf_arr[rank]
		pos2 = suf_arr[rank + 1]
		assert common_prefix(sample_str[pos1:], sample_str[pos2:]) == lcp[rank]

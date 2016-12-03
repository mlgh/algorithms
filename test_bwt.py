
from bwt import *

def test_bwt_simple():
	assert bwt('abacaba\xff') == list('\xffcbbaaaa')

def test_bwt(sample_str):
	assert bwt(sample_str + '\xff') == bwt_naive(sample_str + '\xff')

def test_ibwt(sample_str):
	dollar_sign = '\xff'
	bwt_of_str = bwt(sample_str + dollar_sign)
	assert ibwt_string(bwt_of_str, dollar_sign) == sample_str + dollar_sign


import pytest
from algolib.manacher import *

def test_manacher(sample_str):
	assert list(find_all_palyndromes_slow(sample_str)) == list(find_all_palyndromes_manacher(sample_str))


import pytest
from manacher import *

@pytest.mark.parametrize('s', [
	'abacaba',
	'',
	'xxabacabacyy',
])
def test_manacher(s):
	assert list(find_all_palyndromes_slow(s)) == list(find_all_palyndromes_manacher(s))

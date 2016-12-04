
import pytest

def gen_fixture_params():
	def gen():
		yield '', 'empty_string'
		yield 'a', 'single_char'
		yield 'abacaba'
		yield 'abaaaaa'
		yield 'abababa'
		yield 'aaabbbcccaabbccabc', 'cyclic_shortening'
		yield 'abcdef'
		yield 'a' * 10, 'ten_chars'
	params = []
	ids = []
	for res in gen():
		if isinstance(res, tuple):
			res, res_id = res
		else:
			res_id = res
		params.append(res)
		ids.append(res_id)
	return dict(params=params, ids=ids)

@pytest.fixture(**gen_fixture_params())
def sample_str(request):
	return request.param
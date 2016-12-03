
import sys
from suffix_array import suffix_array_ks_ext

def bwt_naive(arr):
	arrays = sorted([arr[i:] + arr[:i] for i in xrange(len(arr))])
	return [array[-1] for array in arrays]

def bwt(arr):
	suf_arr = suffix_array_ks_ext(arr)
	result = [None] * len(arr)
	for i, pos in enumerate(suf_arr):
		result[i] = arr[(pos + len(arr) - 1) % len(arr)]
	return result

def ibwt_string(s, dollar_sign='\xff'):
	result = ibwt(map(ord, s), ord(dollar_sign))
	return ''.join(map(chr, result))

def ibwt(arr, dollar_marker):
	if not arr:
		return []

	# occ[elem] - number of occurences of elem in arr thus far.
	occ = [0]

	# rank[i] = arr[:i].count(arr[i])
	rank = [None] * len(arr)

	dollar_marker_pos = None

	for i, elem in enumerate(arr):
		while len(occ) <= elem:
			occ.extend([0] * len(occ))
		rank[i] = occ[elem]
		occ[elem] += 1

		if elem == dollar_marker:
			dollar_marker_pos = i

	first_pos = [0] * len(occ)
	for i in xrange(1, len(occ)):
		first_pos[i] = first_pos[i - 1] + occ[i - 1]

	if dollar_marker_pos is None:
		raise ValueError("No dollar marker found")

	result = [None] * len(arr)

	current_pos = dollar_marker_pos

	for writer_pos in xrange(len(arr) - 1, -1, -1):
		result[writer_pos] = arr[current_pos]
		current_pos = first_pos[arr[current_pos]] + rank[current_pos]

	return result

if __name__ == '__main__':
	data = sys.stdin.read()
	bwt_data = bwt(data)
	sys.stdout.write(''.join(bwt_data))

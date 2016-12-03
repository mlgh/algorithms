# -*- coding: utf-8 -*-

import suffix_array_ext

def suffix_array_naive(s):
	"""Naive n^2 log(n)"""
	if not s:
		return []
	dollar_char = chr(ord(max(s)) + 1)
	suffixes = [(s[i:] + dollar_char, i) for i in xrange(len(s))]
	return [i for (suf, i) in sorted(suffixes)]

def counting_sort(arr, key_func, max_key):
	"""Stable counting sort, works in O(max(len(arr), max_key))"""
	max_key += 1
	occ = [0] * max_key
	for elem in arr:
		occ[key_func(elem)] += 1
	for i in xrange(1, max_key):
		occ[i] += occ[i - 1]
	pos = [0] * max_key
	for i in xrange(1, max_key):
		pos[i] = occ[i - 1]
	result = [None] * len(arr)
	for elem in arr:
		k = key_func(elem)
		result[pos[k]] = elem
		pos[k] += 1
	return result

def suffix_array_kmr(s):
	"""Karp Miller Rosenberg prefix doubling O(N*log(N))"""

	if not s:
		return []

	# Since most probably we won't be using all ASCII symbols, it makes sense to remap characters
	alphabet = {c: i for (i, c) in enumerate(sorted(set(s)))}

	position_to_rank = []
	for i, c in enumerate(s):
		position_to_rank.append(alphabet[c])

	def get_pos_rank(pos_to_rank, pos, max_rank):
		if pos >= len(pos_to_rank):
			return max_rank + 1
		return pos_to_rank[pos]

	prefix_size = 1
	while True:
		strings = [s[i:i + prefix_size] for i in xrange(len(s))]
		table = []
		max_rank = max(position_to_rank)
		for i in xrange(len(s)):
			rank1 = get_pos_rank(position_to_rank, i, max_rank)
			rank2 = get_pos_rank(position_to_rank, i + prefix_size, max_rank)
			table.append(((rank1, rank2), i))

		table = counting_sort(table, lambda x: x[0][1], max_rank + 1)
		table = counting_sort(table, lambda x: x[0][0], max_rank + 1)

		assert sorted(table) == table

		new_position_to_rank = [0] * len(s)
		prev_rank_pair = None
		rank = 0
		for rank_pair, pos in table:
			if prev_rank_pair is not None and prev_rank_pair != rank_pair:
				rank += 1
			prev_rank_pair = rank_pair
			new_position_to_rank[pos] = rank

		position_to_rank[:] = new_position_to_rank

		if rank + 1 == len(s):
			break
		prefix_size *= 2

	result = [None] * len(s)
	for pos, rank in enumerate(position_to_rank):
		result[rank] = pos

	assert None not in result

	return result

def suffix_array_ks_helper(arr, max_elem):
	def get_elem(ind):
		if ind < len(arr):
			return arr[ind]
		return max_elem + 1

	# Suppose s is abacaba then it will be split into
	# bac aba - remainder 1
	# aca ba$ - remainder 2

	# sort only by first 3 symbols
	rem12 = range(1, len(arr), 3) + range(2, len(arr), 3)
	rem12 = counting_sort(rem12, key_func=lambda pos: get_elem(pos + 2), max_key=max_elem + 1)
	rem12 = counting_sort(rem12, key_func=lambda pos: get_elem(pos + 1), max_key=max_elem + 1)
	rem12 = counting_sort(rem12, key_func=lambda pos: get_elem(pos + 0), max_key=max_elem + 1)

	# Assign rank to each position from rem12. If multiple positions
	# have same rank, this means that we need to make a recursive call to solve those collisions.
	position_to_rank = [None] * len(arr)
	prev_t = None
	rank = 0
	for pos in rem12:
		t = (get_elem(pos), get_elem(pos + 1), get_elem(pos + 2))
		if prev_t is not None and prev_t != t:
			rank += 1
		prev_t = t
		position_to_rank[pos] = rank
	# Rank of $$$ symbol
	dollar_rank = rank + 1

	# So there were collisions
	if dollar_rank < len(rem12):
		new_arr = []
		idx = []
		# If string was abacaba, construct 
		# bac + aba + $$$ + aca + ba$
		# Note that this will give us ordering for positions with remained 1 and 2
		for i in xrange(1, len(arr), 3):
			new_arr.append(position_to_rank[i])
			idx.append(i)
		new_arr.append(dollar_rank)
		idx.append(None)
		for i in xrange(2, len(arr), 3):
			new_arr.append(position_to_rank[i])
			idx.append(i)
		result = suffix_array_ks_helper(new_arr, dollar_rank)

		# Now deduce rank for original positions from computed ordering
		rem12 = []
		for rank, pos in enumerate(result):
			if idx[pos] is not None:
				position_to_rank[idx[pos]] = rank
				rem12.append(idx[pos])

		# $$$ rank may have changed
		dollar_rank = len(result)

	def get_rank(pos):
		if pos < len(position_to_rank):
			return position_to_rank[pos]
		return dollar_rank

	# rem0 can be sorted by (first_char, corresponding rem1 rank) 
	rem0 = range(0, len(arr), 3)
	rem0 = counting_sort(rem0, key_func=lambda pos: get_rank(pos + 1), max_key=dollar_rank)
	rem0 = counting_sort(rem0, key_func=lambda pos: arr[pos], max_key=max_elem)

	# Merge phase
	result = []
	i = j = 0
	while i < len(rem0) and j < len(rem12):
		pos0 = rem0[i]
		pos12 = rem12[j]
		if rem12[j] % 3 == 1:
			# Case 1: compare rem0 with rem1
			# key is (first_char, corresponding rem1) and (first_char, corresponding rem2)
			key0 = get_elem(pos0), get_rank(pos0 + 1)
			key12 = get_elem(pos12), get_rank(pos12 + 1)
		elif rem12[j] % 3 == 2:
			# Case 2: compare rem0 with rem2
			# key is (first_char, second_char, corresponding_rem2)
			# and (first_char, second_char, corresponding_rem1)
			key0 = get_elem(pos0), get_elem(pos0 + 1), get_rank(pos0 + 2)
			key12 = get_elem(pos12), get_elem(pos12 + 1), get_rank(pos12 + 2)
		else:
			assert False
		if key0 <= key12:
			result.append(pos0)
			i += 1
		else:
			result.append(pos12)
			j += 1
	result.extend(rem0[i:])
	result.extend(rem12[j:])

	return result
	

def suffix_array_ks(s):
	"""Kärkkäinen, Sanders suffix array construction, O(N) runtime"""
	if not s:
		return []
	alphabet = {c: i for (i, c) in enumerate(sorted(set(s)))}
	arr = [alphabet[c] for c in s]
	max_elem = max(arr)
	result = suffix_array_ks_helper(arr, max_elem)
	return result

def suffix_array_ks_ext(s):
	"""C++ implementation of the above"""
	if not s:
		return []
	alphabet = {c: i for (i, c) in enumerate(sorted(set(s)))}
	arr = [alphabet[c] for c in s]
	result = suffix_array_ext.suffix_array_ks_helper(arr)
	return result


def lcp_kasai(arr, suf_arr):
	"""Kasai algorithm to compute lcp"""
	if len(arr) < 1:
		return []
	rank_to_pos = suf_arr
	result = [None] * (len(arr) - 1)

	pos_to_rank = [None] * len(rank_to_pos)
	for rank, pos in enumerate(rank_to_pos):
		pos_to_rank[pos] = rank

	lcp = 0

	for pos in xrange(len(suf_arr)):
		rank = pos_to_rank[pos]
		next_rank = rank + 1

		if next_rank == len(arr):
			lcp = 0
		else:
			pos1 = rank_to_pos[rank]
			pos2 = rank_to_pos[next_rank]

			# lcp can only decrease by 1
			if lcp:
				if not (pos1 + lcp - 1 < len(arr) and pos2 + lcp - 1 < len(arr) and arr[pos1 + lcp - 1] == arr[pos2 + lcp - 1]):
					lcp -= 1
			pos1 = pos1 + lcp
			pos2 = pos2 + lcp

			while pos1 < len(arr) and pos2 < len(arr) and arr[pos1] == arr[pos2]:
				pos1 += 1
				pos2 += 1
				lcp += 1

			result[rank] = lcp
	return result

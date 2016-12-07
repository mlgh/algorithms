# -*- coding: utf-8 -*-

"""
Convention: suppose a and b are strings (indexing from 0) of length len(a) <= len(b)
a < b => exists i < len(a): a[i] < b[i]
a > b => exists i < len(a): a[i] > b[i]

Some properties:
a < b => a + x < b + y (same for >)
a < b => x + a < x + b (same for >)

a <= b is only meaningful when len(a) == len(b) and means a == b OR a < b

A proper prefix of string s is a string t such that t is a prefix of s and t != s
"""

def is_lyndon(arr):
	"""
	A word is called Lyndon if it's unique minimum of its rotations
	"""
	return all(arr[i:] + arr[:i] > arr for i in xrange(1, len(arr)))

"""
s is unique minimum among all of its suffixes if    (1)
	for all i > 0 s[:i] < s[-i:]

s is unique minimum among all of its rotations if    (2)
	for all i > 0 s < s[i:] + s[:i] 

(2) is a definition of Lyndon word. Let's show (1) <=> (2)

Proof:
1) (1) => (2)

Suppose exists i > 0 s.t.
	s >= s[i:] + s[:i] = pref + suf    !(2)
Then
	s[:pref] >= s[i:]    !(1)

2) (2) => (1)

Suppose exists i > 0 s.t.
	s[:i] >= s[-i:]    !(1)
Then compare
	s[:i] + s[i:] and s[-i:] + s[:-i]
a) s[:i] > s[-i:] => s[:i] + s[i:] > s[-i:] + s[:-i]
b) s[:i] = s[-i:] =>
	either s[i:] < s[:-i] => s[i:] + s[:i] < s[:-i] + s[-i:] = s     !(2)
	or s[i:] >= s[:-i] => s[:i] + s[i:] >= s[-i:] + s[:-i] = s     !(2)
So in both cases !(2) holds.

▫

Some properties of Lyndon words:
A Lyndon word is called trivial if it len(s) = 1.

If s is a non-trivial Lyndon word then
s[0] < s[-1]
Proof: use (1) with i = 0

If s is a Lyndon word, there may be prefixes that are not Lyndon words.
Proof: aab is a Lyndon word, but aa is not a Lyndon word
Same for suffixes:
Proof: abb is a Lyndon word, but bb is not.
If s and s + t are Lyndon words, then t may be not a Lyndon word.
Proof: aaaabbb is a Lyndon word, aaaab is a Lyndon word, but bb is not a Lyndon word
If t and s + t are Lyndon words, then s may be not a Lyndon word.
Proof: aaab is a Lyndon word, ab is a Lyndon word, but aa is not a Lyndon word

Merge rules:

If s and t are Lyndon words and s < t then s + t is a Lyndon word
Proof:
a) s + t < suf(s): s < suf(s)
b) s + t < t: s < t => s + t < t
c) s + t < suf(t): s < t < suf(t) => s + t < suf(t)

If s and t are Lyndon words and t is prefix of s, then s + t is not a Lyndon word.
Proof:
Let s = t + e
s + t = t + e + t => t

If s and t are Lyndon words and s is proper prefix of t, then s + t is a Lyndon word.
Proof:
Let t = s + e
a) s + t < suf(s) + t: s < suf(s)
b) s + t < t: t < e => s + t < s + e
c) s + t < suf(s) + e: s < suf(s)
d) s + t < e: s + t < t < e
e) s + t < suf(e): s + t < t < suf(e) since suf(suf(t)) is still suf(t)

Let a >> b mean that !(a < b) && !(a is a proper prefix of b)
a << b is the same as "a$ is lexicographically smaller than b$"
where '$' is a special symbol that is greater than everything.

* Chen-Lyndon-Fox theorem:
For arbitrary string t there exists a unique decomposition of t into Lyndon words s.t.
t = s1 + s2 + s3 + ... + sn s.t. s1 >> s2 >> s3 >> ... >> sn

Proof:
1) Existance: decompose t into trivial Lyndon words. Then for every adjacent Lyndon words
merge them into a single Lyndon word using previous property until there are no such adjacent pairs.
Suppose after this operation we got a sequence s1 s2 ... sn, and !(s_i >> s_i+1) for some i
Contradiction: all such adjacent pairs were eliminated on previous step.

2) Uniqueness
Suppose there are two different decompositions of t:
a1 a2 ... an
b1 b2 ... bm

Throw away a_i b_i while a_i == b_i
If we threw away everything, then contradiction, decompositions are same.

Thus a_i != b_i. This means that len(a_i) != len(b_i) (since they are decompositions from the same string)
Let len(a_i) < len(b_i) (otherwise swap labels)

b_i is some prefix of a_i + a_{i+1} + ... + an
	b_i = a_i + a_{i+1} + ... + a_{k}[:prefix]
Since a_i >> a_{k} >> a_{k}[:prefix], so
!(a_i < a_{k}[:prefix]) thus b_i is not a Lyndon word.
Contradiction.

▫
"""

def factorize_lyndon_naive(arr):
	"""
	By Chen-Lyndon-Fox theorem proved above this will yield us unique decomposition
	of arr into longest Lyndon words
	"""
	l = 0
	while l < len(arr):
		max_r = l + 1
		for r in xrange(l + 2, len(arr) + 1):
			if is_lyndon(arr[l:r]):
				max_r = r
		yield l
		l = max_r


"""
The above algorithm works in O(N^4) which makes it useless.

We can speed it up to linear time, constant space.

TODO: Normal explanation
"""

def factorize_lyndon(arr):
	current_lyndon_l = 0
	current_lyndon_r = 1
	next_candidate_idx = 1
	while current_lyndon_l < len(arr):
		lyndon_word_size = current_lyndon_r - current_lyndon_l
		compare_with = (next_candidate_idx - current_lyndon_r) % lyndon_word_size
		if next_candidate_idx == len(arr) or arr[next_candidate_idx] < arr[compare_with]:
			while current_lyndon_l + lyndon_word_size <= next_candidate_idx:
				yield current_lyndon_l
				current_lyndon_l += lyndon_word_size
				current_lyndon_r += lyndon_word_size
			current_lyndon_r = current_lyndon_l + 1
			next_candidate_idx = current_lyndon_r
		elif arr[next_candidate_idx] == arr[compare_with]:
			next_candidate_idx += 1
		elif arr[next_candidate_idx] > arr[compare_with]:
			next_candidate_idx += 1
			current_lyndon_r = next_candidate_idx

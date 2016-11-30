
"""
3 (and a half) steps to understand Manacher algorithm.

Problem: given a string, list all its substrings that are maximal palyndrome.
(also formulated like: find maximum length palyndrome, find longest palyndromic suffix, etc)

A substring is called a maximal palyndrome if it can't be extended anymore.
E.g. word "fallacy", here "ll" is a palyndrome, but it's not maximal.
However, "alla" is maximal.

Also if the substring length is even, we call it even palyndrome, otherwise we call it odd.

We will focus only on odd palyndromes and then extend the algorithm to all
kinds of palyndromes using a simple hack.
"""

def find_odd_palyndromes_simple(s):
    """
    Brute-force - expand palyndrome bounds at each location till it's possible
    """
    for center in xrange(len(s)):
        max_radius = 0
        radius = 0
        while True:
            radius += 1
            palyndrome_l = center - radius
            palyndrome_r = center + radius

            if palyndrome_l < 0 or palyndrome_r >= len(s):
                break

            if s[palyndrome_l] != s[palyndrome_r]:
                break
            max_radius = radius
        yield (center, max_radius)

"""
Although this could work in linear time on some strings,
the worst case running time is `O(N^2)` e.g. on string "aaaa....aaa"

We are doing lots of redundant work. It can be avoided if we
use palyndrome property:
(convention: index arrays start from 0)

Palindrome property:    (1)
If string `p` is a palyndrome and it contains a palyndromic
substring with center in position `c` of radius `r`,
then it will also contain a  palyndromic substring with center in position
`c_mirrored = |p| - c - 1` of radius `r`
Example: `p = "abacaba"`, and there is a palyndrome `p[0:3] = "aba"` with center 
in position  1, so there will also be a palyndrome `p[4:7]` with center in position 5

Clamped palyndrome property:    (2)
If string `s` has substring `p` and `p` is a palyndrome, let's apply palyndrome property (1)
to `p`, thus we get that radius of palyndrome with center in position 'c'
in original substring will be >= `r`.

Draw a bunch of palyndromes with sub-palyndromes to get the idea and verify those properties: if you know that 
something is a palyndrome, and you know something about its left half, you can deduce some knowledge
about its right half.

During the algorithm, if at some iteration we know that the current center `c` is inside some palyndrome `p`,
we apply clamped palyndrome property (2) and start expanding current palyndrome from radius `r` + 1, not 0

Example:
string:         xxabacabacxx
prev_radius[]   0001030?
                       ^-- current center
Since "abacaba" is a palyndrome, and it contains sub-palyndrome "aba" which is known to have radius 1,
for the current center we know that the radius is at least 1.

How do we find the `p` palyndrome at each position? Well, for now let's
just try all previous palyndromes.
"""

def find_odd_palyndromes_caching(s):
    prev_radius = [0] * len(s)
    for center in xrange(len(s)):
        max_radius = 0
        # Iterate through all previous palyndromes
        for previous_center in xrange(center):
            # Compute bounds of string `p` which is palyndrome
            p_l = previous_center - prev_radius[previous_center]
            p_r = previous_center + prev_radius[previous_center]
            # `center` is not contained inside that palyndrome - no info can be extracted
            if not p_l <= center <= p_r:
                continue
            # Apply palyndromic property
            p_len = p_r - p_l + 1
            center_offset = center - p_l
            mirrored_center = p_l + (p_len - center_offset - 1)
            radius_cand = prev_radius[mirrored_center]
            # But we need to clamp it since some parts of it may lie outside `s`
            # How many symbols of palyndrome with center at `mirrored_center` are outside `s`
            left_outside = max(0, p_l - (mirrored_center - radius_cand))
            # same for right
            right_outside = max(0, (mirrored_center + radius_cand) - p_r)
            # make sub-palyndrome fit into `s`
            clamped_radius = radius_cand - max(left_outside, right_outside)
            # There may be multiple contaning palyndromes, take maximum
            max_radius = max(max_radius, clamped_radius)
        # The rest of the algorithm is the same as previous
        radius = max_radius
        while True:
            radius += 1
            palyndrome_l = center - radius
            palyndrome_r = center + radius

            if palyndrome_l < 0 or palyndrome_r >= len(s):
                break

            if s[palyndrome_l] != s[palyndrome_r]:
                break
            max_radius = radius
        prev_radius[center] = max_radius

        yield (center, max_radius)

"""
Seems like we've turned the worst-case O(N^2) performance into best-case
O(N^2) performance.

But do we really need to look at all previous palyndromes?

Here is a trick: 
Let's always choose the palyndrome with the right-most right bound as `p`.

We didn't lose any correctness! If we choose a bad heuristic for choosing `p`
all we get will be just worse asymptotics.

"""

def find_odd_palyndromes_manacher(s):
    prev_radius = [0] * len(s)
    rightmost_palyndrome_l = rightmost_palyndrome_r = 0
    for center in xrange(len(s)):
        max_radius = 0
        if rightmost_palyndrome_l <= center <= rightmost_palyndrome_r:
            p_l = rightmost_palyndrome_l
            p_r = rightmost_palyndrome_r
            # Apply palyndromic property
            p_len = p_r - p_l + 1
            center_offset = center - p_l
            mirrored_center = p_l + (p_len - center_offset - 1)
            radius_cand = prev_radius[mirrored_center]
            # But we need to clamp it since some parts of it may lie outside `s`
            # How many symbols of palyndrome with center at `mirrored_center` are outside `s`
            left_outside = max(0, p_l - (mirrored_center - radius_cand))
            # same for right
            right_outside = max(0, (mirrored_center + radius_cand) - p_r)
            # make sub-palyndrome fit into `s`
            clamped_radius = radius_cand - max(left_outside, right_outside)
            # There may be multiple contaning palyndromes, take maximum
            max_radius = clamped_radius
        radius = max_radius
        while True:
            radius += 1
            palyndrome_l = center - radius
            palyndrome_r = center + radius

            if palyndrome_l < 0 or palyndrome_r >= len(s):
                break

            if s[palyndrome_l] != s[palyndrome_r]:
                break

            assert palyndrome_r > rightmost_palyndrome_r
            rightmost_palyndrome_l = palyndrome_l
            rightmost_palyndrome_r = palyndrome_r

            max_radius = radius
        prev_radius[center] = max_radius
        yield center, max_radius

"""
This algorithm works in O(N). Why? Every iteration of `while` loop
will increase `rightmost_palyndrome_r` by 1, so in total
the loop can't be executed more than |s| times.

To extend our algo to work with odd palyndromes just insert some fake symbol
between every character.
E.g. looot -> l$o$o$o$t, now find palyndromes in that string 
and take care of a special case : $o$ must be reported as 'o', not as '$'
"""

def generic_find_all_palyndromes(s, odd_palyndrome_finder):
    mangled_s = '$'.join(s)
    for center, radius in find_odd_palyndromes_manacher(mangled_s):
        l = center - radius
        r = center + radius
        if mangled_s[l] == '$' and mangled_s[r] == '$':
            if l == r:
                continue
            l += 1
            r -= 1
        l /= 2
        r /= 2
        yield l, r

def find_all_palyndromes_slow(s):
    return generic_find_all_palyndromes(s, odd_palyndrome_finder=find_odd_palyndromes_simple)

def find_all_palyndromes_manacher(s):
    return generic_find_all_palyndromes(s, odd_palyndrome_finder=find_odd_palyndromes_manacher)

import sys
from suffix_array import suffix_array_ks

def bwt(arr):
	suf_arr = suffix_array_ks(arr)
	result = [None] * len(arr)
	for i, pos in enumerate(suf_arr):
		result[i] = arr[(pos + len(arr) - 1) % len(arr)]
	return result

# Taken from wikipedia, TODO: implement mine
def ibwt(r, *args):
    firstCol = "".join(sorted(r))
    count = [0]*256
    byteStart = [-1]*256
    output = [""] * len(r)
    shortcut = [None]*len(r)
    #Generates shortcut lists
    for i in range(len(r)):
        shortcutIndex = ord(r[i])
        shortcut[i] = count[shortcutIndex]
        count[shortcutIndex] += 1
        shortcutIndex = ord(firstCol[i])
        if byteStart[shortcutIndex] == -1:
            byteStart[shortcutIndex] = i

    localIndex = (r.index("\xff") if not args else args[0])
    for i in range(len(r)):
        #takes the next index indicated by the transformation vector
        nextByte = r[localIndex]
        output [len(r)-i-1] = nextByte
        shortcutIndex = ord(nextByte)
        #assigns localIndex to the next index in the transformation vector
        localIndex = byteStart[shortcutIndex] + shortcut[localIndex]
    return "".join(output)

if __name__ == '__main__':
	data = sys.stdin.read()
	bwt_data = bwt(data)
	sys.stdout.write(''.join(bwt_data))

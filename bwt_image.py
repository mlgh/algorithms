
import argparse
import threading
from PIL import Image

from bwt import ibwt
from suffix_array_ext import bwt_pixels

def set_end_marker(arr):
	for i in xrange(len(arr)):
		if arr[i] == 255:
			arr[i] = 254
	arr[-1] = 255

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input_image')
	parser.add_argument('output_image')
	parser.add_argument('-i', '--inverse', action='store_true', help='Inverse BWT transform')
	args = parser.parse_args()

	im = Image.open(args.input_image)

	if im.mode == 'B':
		im = im.convert('L')

	data = im.getdata()
	if len(im.mode) == 1:
		channels = list(data)
	else:
		channels = map(list, zip(*data))

	# Replace 255 with 254 so that we could apply inverse bwt later
	if not args.inverse:
		threads = []

		def thread_func(chan_num):
			channels[chan_num] = bwt_pixels(channels[chan_num])

		for i in xrange(len(channels)):
			threads.append(threading.Thread(target=thread_func, args=(i,)))
			threads[-1].start()
		[t.join() for t in threads]
	else:
		channels = [ibwt(channel, 255) for channel in channels]
	if len(im.mode) == 1:
		data = channels
	else:
		data = zip(*channels)

	im.putdata(data)
	im.save(args.output_image)



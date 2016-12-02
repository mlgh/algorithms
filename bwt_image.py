
import argparse
from PIL import Image

from bwt import bwt, ibwt

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
		for channel in channels:
			set_end_marker(channel)
		channels = map(bwt, channels)
	else:
		# XXX: Rewrite using my ibwt
		channels = map(lambda ch: map(chr, ch), channels)
		channels = map(ibwt, channels)
		channels = map(lambda ch: map(ord, ch), channels)

	if len(im.mode) == 1:
		data = channels
	else:
		data = zip(*channels)

	im.putdata(data)
	im.save(args.output_image)



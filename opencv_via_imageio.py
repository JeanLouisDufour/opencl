#
# conda install -c conda-forge imageio-ffmpeg
import imageio as iio
import matplotlib.pyplot as plt

plt.ion()

camera = iio.get_reader("<video0>")
meta = camera.get_meta_data()
im = camera.get_data(0) # (480,640,3) uint8

fig1, ax1 = plt.subplots()
visu = ax1.imshow(im)

idx = 0
for im in camera:
	visu.set_data(im)
	plt.draw()
	fig1.canvas.flush_events()
	idx += 1
	if idx == 1000:
		break

camera.close()

# plt.imshow(im)

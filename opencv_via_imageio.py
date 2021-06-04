#
# conda install -c conda-forge imageio-ffmpeg
import imageio as iio
import matplotlib as mpl, matplotlib.pyplot as plt
import time

mpl.rcParams['toolbar'] = 'None' 

plt.ion()

camera = iio.get_reader("<video0>")
meta = camera.get_meta_data()
im = camera.get_data(0) # (480,640,3) uint8

fig, axes = plt.subplots(2,2)
for ax in axes.flat:
	ax.axis('off')
visus = [ax.imshow(im) for ax in axes.flat]

N = 100
T0 = time.perf_counter()
sleeps = 0
for idx in range(N):
	t0 = time.perf_counter()
	im = camera.get_next_data()
	imod = idx % 3
	if imod == 0:
		for visu in visus:
			visu.set_data(im)
	elif imod == 1:
		plt.draw()
	else:
		fig.canvas.flush_events()
	t1 = time.perf_counter()
	if t1 - t0 <= 33.333e-3:
		sleeps +=1
		time.sleep(33.333e-3 - (t1-t0))
T1 = time.perf_counter()

camera.close()

print(sleeps)
print((T1-T0)/N)

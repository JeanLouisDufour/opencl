import numpy as np

#a = np.zeros((10,), dtype=np.uint32)

taille = 100000

rng = np.random.default_rng(12345)
a = rng.integers(low=0, high=np.iinfo(np.uint32).max+1, size=(taille,), dtype=np.uint32)

b = np.sort(a)

def is_sorted(a):
	return all(a[i] <= a[i+1] for i in range(len(a)-1))

print(is_sorted(a), is_sorted(b))

c = np.ctypeslib.as_ctypes(a)

def radixsort(a, bsz=4):
	"""
	nombre pair d'appels
	"""
	bmask = np.uint32((1<<bsz)-1)
	# .[0] reste a 0
	countarray = np.zeros(((1<<bsz)+1,), dtype=np.uint32)
	def countsort(x,y, bstart):
		"""
		"""
		# 1 : comptage (le dernier compteur ne sert a rien)
		for e in x:
			tag = (e>>bstart) & bmask
			countarray[tag+1] += 1
		# 2 : cumsum
		for i in range(1,len(countarray)-1):
			countarray[i] += countarray[i-1]
		# 3 : placement
		for e in x:
			tag = (e>>bstart) & bmask
			idx = countarray[tag]
			countarray[tag] += 1
			y[idx] = e
		# 4 : reset
		countarray[:] = 0
	####
	assert 32 % bsz == 0 
	niter = 32//bsz;
	assert niter % 2 == 0
	b = np.empty(a.shape, dtype=a.dtype)
	for i in range(niter//2):
		countsort(a,b,(2*i)*bsz)
		countsort(b,a,(2*i+1)*bsz)
	return a

b1 = radixsort(a)

print(all(b==b1))


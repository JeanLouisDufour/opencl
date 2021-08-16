import cv2 as cv

img = cv.imread('tire.tif')
assert all(img[:,:,0].flat == img[:,:,1].flat) and all(img[:,:,0].flat == img[:,:,2].flat)
img = img[:,:,0]
img1 = cv.equalizeHist(img)
cv.imwrite('tire_APRES.tif',img1)


Kalray :
make
output/bin/host_app

MinGW :
attention a bien utiliser pgm.cpp
g++ -g -c pgm.cpp
g++ -g -c -I c:/opencv-4.5.1/sources/3rdparty/include/opencl/1.2 lib_opencl.cpp
g++ -g -c -I c:/opencv-4.5.1/sources/3rdparty/include/opencl/1.2 histogram.cpp
g++ -g pgm.o lib_opencl.o histogram.o c:/Windows/System32/OpenCL.DLL

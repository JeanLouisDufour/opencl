#
# Copyright (C) 2019 Kalray SA. All rights reserved.
#
CL_BUILD_FLAGS ?= -DENABLE_WG_SIZE
MPPA_BUILD_POCL_CACHE_DIR ?= $(shell echo $$(pwd))/.cache/pocl/kcache
HOST_SYSTEM_BIN ?= host
HOST_SYSTEM ?= linux

ARCH ?= kv3-1
arch := $(ARCH)

cppflags = -g3 -O2

host_app-srcs := histogram.cpp lib_opencl.cpp pgm.cpp
host_app-cflags := -g3 -O2
host_app-cppflags := -g3 -O2 -fopenmp
host_app-lflags := -fopenmp

$(HOST_SYSTEM_BIN)-bin := host_app



include $(KALRAY_TOOLCHAIN_DIR)/share/make/Makefile.opencl.$(HOST_SYSTEM)

all: kernels

kernels:
#	POCL_CACHE_DIR=$(MPPA_BUILD_POCL_CACHE_DIR) POCL_EXTRA_BUILD_FLAGS="-g $(CL_BUILD_FLAGS)" POCL_DEBUG=1 $(KALRAY_TOOLCHAIN_DIR)/bin/kvx-poclcc histogram.cl -DNLIN=720 -DNCOL=1080 -DNWI=16


run_cos_sim: all
	$(KALRAY_TOOLCHAIN_DIR)/bin/kvx-cluster --elf-symbols=1,$(KALRAY_TOOLCHAIN_DIR)/share/pocl/cos_standalone/fw.bin,2,$(KALRAY_TOOLCHAIN_DIR)/share/pocl/cos_standalone/fw.bin,3,$(KALRAY_TOOLCHAIN_DIR)/share/pocl/cos_standalone/fw.bin,4,$(KALRAY_TOOLCHAIN_DIR)/share/pocl/cos_standalone/fw.bin --timeout-sec=3600 -s libstd_scalls.so -- $(O)/bin/host_app

run_cos_hw: all
	$(KALRAY_TOOLCHAIN_DIR)/bin/kvx-jtag-runner --exec-file=Cluster0:$(O)/bin/host_app --timeout=600

run_linux_hw: all
	timeout 120 ./$(O)/bin/host_app

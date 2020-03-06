cimport numpy as np 
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
def black_white(np.ndarray[np.uint8_t, ndim = 3] img):
    cdef int i = 0
    cdef int j = 0
    cdef int k = 0
    cdef int R = img.shape[0]
    cdef int G = img.shape[1]
    cdef int B = img.shape[2]
    for i in range(R):
        for j in range(G):
            for k in range(B):
                img[i, j, k] = img[i, j, 0]
    return img

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True) 
def effect(np.ndarray[np.uint8_t, ndim=3]img):
    cdef int i = 0
    cdef int j = 0
    cdef int k = 0
    cdef int R = img.shape[0]
    cdef int G = img.shape[1]
    cdef int B = img.shape[2]
    for i in range(R):
        for j in range(G):
            for k in range(B):
                img[i, j, k] = (img[i, j, 0] + img[i, j, 1] + img[i, j, 2])/3
    return img


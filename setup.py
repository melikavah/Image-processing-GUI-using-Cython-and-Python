from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
	Extension("Image_processing", ["Image_processing.pyx"],
 		language = "c++", 
 		include_dirs = [np.get_include()])]

setup(ext_modules= cythonize(extensions, annotate=True))	
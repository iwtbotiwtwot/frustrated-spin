from setuptools import setup,Extension
from Cython.Build import cythonize
setup(name='spin-fast-cpu',ext_modules=cythonize([Extension('fast_cpu',['fast_cpu.pyx'],extra_compile_args=['-O3'])],compiler_directives={'language_level':3}))

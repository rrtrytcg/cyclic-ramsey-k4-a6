# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize
import platform

extra_flags = []
if platform.system() == 'Windows':
    extra_flags = ['/std:c++20']

extensions = [
    Extension(
        "subgraph",
        sources=["subgraph.pyx", "c_interface.cpp", "thread_pool.cpp"],
        libraries=[],
        library_dirs=[],
        include_dirs=["../../../include/ord_ram_num/"],
        extra_compile_args=extra_flags
    )
]

setup(name="Subgraph", ext_modules=cythonize(extensions, build_dir="build"))

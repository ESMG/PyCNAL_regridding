import os
from numpy.distutils.core import setup, Extension

fill_msg_grid    = Extension(name = 'brushcutter.fill_msg_grid',
                             sources = ['brushcutter/f90/fill_msg_grid.f90'])
#creeping_sea     = Extension(name = 'brushcutter.creeping_sea',
#                             sources = ['brushcutter/f90/creeping_sea.f90'])
#mod_drown_py     = Extension(name = 'brushcutter.mod_drown_py',
#                             sources = ['brushcutter/f90/mod_drown_py.f90'])

setup(
    name = "brushcutter",
    version = "1.0",
    author = "Raphael Dussin",
    author_email = "raphael.dussin@gmail.com",
    description = ("A package to create boundary conditions for MOM6 " ),
    license = "GPLv3",
    keywords = "ocean boundary conditions",
    url = "",
    packages=['brushcutter'],
    ext_modules = [fill_msg_grid]
#    ext_modules = [fill_msg_grid,creeping_sea,mod_drown_py]
)



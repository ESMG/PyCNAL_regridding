import os
from numpy.distutils.core import setup, Extension

fill_msg_grid    = Extension(name = 'brushcutter.fill_msg_grid',
                             sources = ['brushcutter/f90/fill_msg_grid.f90'])
mod_drown_sosie     = Extension(name = 'brushcutter.mod_drown_sosie',
                             sources = ['brushcutter/f90/mod_drown_sosie.f90'])

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
    ext_modules = [fill_msg_grid,mod_drown_sosie]
)



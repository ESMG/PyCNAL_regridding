import os
from numpy.distutils.core import setup, Extension

fill_msg_grid    = Extension(name = 'PyCNAL_regridding.fill_msg_grid',
                             sources = ['PyCNAL_regridding/f90/fill_msg_grid.f90'])
mod_drown_sosie     = Extension(name = 'PyCNAL_regridding.mod_drown_sosie',
                             sources = ['PyCNAL_regridding/f90/mod_drown_sosie.f90'])

setup(
    name = "PyCNAL_regridding",
    version = "1.0",
    author = "Raphael Dussin",
    author_email = "raphael.dussin@gmail.com",
    description = ("A package to create boundary conditions for MOM6 " ),
    license = "LGPLv3",
    keywords = "ocean boundary conditions",
    url = "https://github.com/ESMG/PyCNAL_regridding",
    packages=['PyCNAL_regridding'],
    ext_modules = [fill_msg_grid,mod_drown_sosie]
)



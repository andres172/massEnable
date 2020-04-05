# pylint: skip-file
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(include_files = ['templates/'], packages = [], excludes = [])

base = 'Console'

executables = [
    Executable('mass_enable.py', base=base)
]

setup(name='Mass Enable',
      version = '1',
      description = 'Mass Enable',
      options = dict(build_exe = buildOptions),
      executables = executables)

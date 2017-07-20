
import sys

try:
  from setuptools import setup
except ImportError:
	sys.exit('ERROR: setuptools is required.\nTry using "pip install setuptools".')

# Use README.rst for the long description
with open('README.rst') as fh:
    long_description = fh.read()

def get_package_version(verfile):
  '''Scan the script for the version string'''
  version = None
  with open(verfile) as fh:
      try:
          version = [line.split('=')[1].strip().strip("'") for line in fh if \
              line.startswith('__version__')][0]
      except IndexError:
          pass
  return version

version = get_package_version('symbolator.py')

if version is None:
    raise RuntimeError('Unable to find version string in file: {0}'.format(version_file))


setup(name='symbolator',
    version=version,
    author='Kevin Thibedeau',
    author_email='kevin.thibedeau@gmail.com',
    url='http://kevinpt.github.io/symbolator',
    download_url='http://kevinpt.github.io/symbolator',
    description='HDL symbol generator',
    long_description=long_description,
    platforms = ['Any'],
    install_requires = ['hdlparse>=1.0.3'],
    packages = ['nucanvas', 'nucanvas/color', 'symbolator_sphinx'],
    py_modules = ['symbolator'],
    entry_points = {
        'console_scripts': ['symbolator = symbolator:main']
    },
    include_package_data = True,

    use_2to3 = True,
    
    keywords='HDL symbol',
    license='MIT',
    classifiers=['Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Documentation',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
        ]
    )


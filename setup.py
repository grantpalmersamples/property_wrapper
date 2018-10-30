from setuptools import setup

setup(name='property_wrapper',
      version='0.1',
      packages=['lib/property_wrapper'],
      url='https://github.com/gpalmz/property_wrapper',
      author='Grant Palmer',
      author_email='grantyorkpalmer@gmail.com',
      description='Easily create wrapper classes that attach Python '
      'properties to complex data',
      long_description=open('README.md').read(),
      python_requires='>=3')

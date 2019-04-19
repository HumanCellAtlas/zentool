import glob
import os
from setuptools import setup, find_packages

install_requires = [line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), "requirements.txt"))]

setup(name='zentool',
      version='1.0.1',
      description='Tool for manipulating ZenHub / GitHub using Google Sheets',
      url='https://github.com/HumanCellAtlas/zentool',
      author='Sam Pierson',
      author_email='spierson@chanzuckerberg.com',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      scripts=glob.glob('scripts/*'),
      zip_safe=False,
      install_requires=install_requires,
      platforms=['MacOS X', 'Posix'],
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.6'
      ]
      )

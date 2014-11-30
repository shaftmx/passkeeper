#!/usr/bin/env python

from distutils.core import setup

setup(name='passkeeper',
      version='0.1',
      description=('This is a very simple password keeper based on ini file '
                   'and symmetric gpg encryption'),
      author='shaftmx',
      author_email='gael@netwiki.fr',
      url='https://github.com/shaftmx/passkeeper',
      packages=['passkeeper'],
      scripts=['passkeeper-cli'],
     )

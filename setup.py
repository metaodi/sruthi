# -*- coding: utf-8 -*-

from codecs import open
from setuptools import setup
import re

with open('sruthie/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

try:
    import pypandoc
    from unidecode import unidecode
    description = open('README.md', encoding='utf-8').read()
    description = unidecode(description)
    description = pypandoc.convert(description, 'rst', format='md')
except (IOError, OSError, ImportError):
    description = 'SRU client for Python'

setup(
    name='sruthi',
    packages=['sruthi'],
    version=version,
    install_requires=['requests'],
    description='SRU client for Python',
    long_description=description,
    author='Stefan Oderbolz',
    author_email='odi@metaodi.ch',
    maintainer='Stefan Oderbolz',
    maintainer_email='odi@metaodi.ch',
    url='https://github.com/metaodi/sruthi',
    download_url='https://github.com/metaodi/sruthi/archive/v%s.zip' % version,
    keywords=['sru', 'search', 'retrieve', 'archive', 'library'],
    license='GPLv3',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

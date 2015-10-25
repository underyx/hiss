import io
from setuptools import setup

with io.open('README.md', encoding='utf-8') as f:
    README = f.read()

setup(
    name='hiss',
    version='0.0.1',
    url='https://github.com/underyx/hiss',
    author='Bence Nagy',
    author_email='bence@underyx.me',
    maintainer='Bence Nagy',
    maintainer_email='bence@underyx.me',
    download_url='https://github.com/underyx/hiss/releases',
    long_description=README,
    packages=['hiss'],
    include_package_data=True,
    install_requires=[
        'protobuf==3.0.0a4',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ]
)

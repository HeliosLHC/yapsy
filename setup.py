from setuptools import setup, find_packages

setup(
    name='yapsy',
    version='1.12.2.post1',
    description='Fat-free DIY Python plugin management toolkit (patched for Python 3.12+)',
    author='Talossec (fork of Olivier Guilyardi)',
    url='https://github.com/talos-security/yapsy',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ],
)

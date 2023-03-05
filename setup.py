# -*- coding: utf-8 -*-

# -------------------------------------------#
# author: sean lee                           #
# email: xmlee97@gmail.com                   #
# -------------------------------------------#


from setuptools import setup, find_packages


__version__ = '0.1.0'


long_description = open('README.md', encoding='utf-8').read()

with open('requirements.txt', encoding='utf-8') as f:
    requirements = [l for l in f.read().splitlines() if l]

with open('dev-requirements.txt', encoding='utf-8') as f:
    test_requirements = [l for l in f.read().splitlines() if l][1:]


setup(
    name='lanno',
    version=__version__,
    description='Let Large Language Models Serve As Data Annotators.',
    long_description_content_type="text/markdown",
    long_description=long_description,
    keywords='LLM,NLP,Annotator,Prompt',
    author='sean lee',
    author_email='xmlee97@gmail.com',
    license='Apache 2.0 License',
    platforms=['all'],
    url='https://github.com/SeanLee97/lanno',
    packages=find_packages(exclude=('test*', )),
    package_data={
        '': ['*.txt', '*.jinja'],
        'lanno': ['templates/texts/*.jinja']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic',
    ],
    install_requires=requirements,
    tests_require=test_requirements,
)

import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='p3bamboo',
    version='1.0.2',
    author='darktohka',
    author_email='daniel@tohka.us',
    description='Panda3D BAM file parser library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/darktohka/p3bamboo',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
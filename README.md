p3bamboo
========

[![PyPI version](https://img.shields.io/pypi/v/p3bamboo.svg)](https://pypi.python.org/pypi/p3bamboo/)

p3bamboo is a Python library that gives you full access to a Panda3D BAM file's inner structure.

# Getting Started

Simply install p3bamboo using `pip`:

```bash
python -m pip install p3bamboo
```

Loading a BAM file is very simple:

```python
from p3bamboo.BamFile import BamFile

bam = BamFile()

with open('myModel.bam', 'rb') as f:
    bam.load(f)
```

Writing out a BAM file is also easy:

```python
with open('newModel.bam', 'wb') as f:
    bam.write(f)
```

To automatically deserialize BAM objects, you must register your own custom BAM object types. For example, to register an object type named `Texture`:

```python
from p3bamboo.BamFactory import BamFactory
from myproject.Texture import Texture

BamFactory.register_type('Texture', Texture)
```

If you register your object types properly and load a BAM file afterwards, you'll be able to access your objects using `bam.object_map`.
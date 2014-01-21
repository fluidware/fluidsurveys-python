# Python FluidSurveys

**A Python wrapper around the Fluidsurveys API.**

## Introduction
This library provides a pure Python interface for the [FluidSurveys API](https://docs.fluidsurveys.com/). It works with Python versions from 2 and 3. 

## Building

From source:
Use `pip` to install dependencies:
 
    $ pip install -r requirements.txt

Clone the latest `fluidsurveys-python` library from Github:
```
 $ git clone https://github.com/fluidware/fluidsurveys-python.git
 $ cd fluidsurveys-python
```

Extract the source distribution and run:

```
$ python setup.py build
$ python setup.py install
```
*Testing*

With setuptools installed:

```
$ python setup.py test
```

## Documentation

View the last release API documentation at: [FluidSurveys API](https://docs.fluidsurveys.com/)

## Using

The library provides a Python wrapper around the Fluidsurveys API and the Fluidsurveys data model.

In development
==============


##### example usage


```python
import fluidsurveys
billy = fluidsurveys.Contact.retrieve(2)
billy.name
u'billy'
billy.name = "Billy Bob"
billy.save()
<Contact at 0x7fbf48c4cdc0> JSON: {
  "contact_uri": "http://fluidsurveys.dev:8000/api/v3/contacts/2/", 
  "email": "face@time.com", 
  "id": 2, 
  "name": "Billy bob", 
  "unsubscribed": false
}

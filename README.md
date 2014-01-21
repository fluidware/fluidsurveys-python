# Python FluidSurveys

<<<<<<< HEAD
**A Python wrapper around the Fluidsurveys API.**

This library provides a pure Python interface for the [FluidSurveys API](https://docs.fluidsurveys.com/). It works with Python versions from 2 and 3. 
=======
FluidSurveys API wrapper for Python

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
```
>>>>>>> fde75a8a46a1f3ecfcf516cd629369819d26c388

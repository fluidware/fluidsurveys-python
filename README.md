fluidsurveys-python
===================

FluidSurveys API wrapper for Python

In development
==============


example usage
-------------

```python
import fluidsurveys
billy = fluidsurveys.Contact.retrieve(2)
billy.name = "Billy bob"
billy.save()
<Contact at 0x7fbf48c4cdc0> JSON: {
  "contact_uri": "http://fluidsurveys.dev:8000/api/v3/contacts/2/", 
  "email": "face@time.com", 
  "id": 2, 
  "name": "Billy bob", 
  "unsubscribed": false
}
```

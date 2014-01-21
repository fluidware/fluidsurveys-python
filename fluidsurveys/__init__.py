
__all__ = [
	'resources',
	'access',
	'exceptions',
	'client',
]

# Fluid Python bindings
# Forked from https://github.com/stripe/stripe-python
# API docs at http://fluidsurveys.com/docs/api
# Authors:
# Patrick Collison <patrick@fluidsurveys.com>
# Greg Brockman <gdb@fluidsurveys.com>
# Andrew Metcalf <andrew@fluidsurveys.com>

# Configuration variables

api_key = None
api_base = 'http://fluidsurveys.dev:8000/api'
api_version = None
verify_ssl_certs = False

import os
if os.environ.get('USER') == 'Steve':
    #TODO remove this, development shortcut
    api_key = 'kT9zp47khwk8QS526t23Grvkm9vQ2N'

#Fluid Resources
from fluidsurveys.resource import Contact, Template

# Error imports.  Note that we may want to move these out of the root
# namespace in the future and you should prefer to access them via
# the fully qualified `fluidsurveys.exceptions` module.

from fluidsurveys.exceptions import (  # noqa
    FluidError, APIError, APIConnectionError, AuthenticationError,
    InvalidRequestError)

# DEPRECATED: These imports will be moved out of the root fluid namespace
# in version 2.0

from fluidsurveys.version import VERSION  # noqa
from fluidsurveys.api_requestor import APIRequestor  # noqa
from fluidsurveys.resource import (  # noqa
    convert_to_fluid_object, FluidObject, FluidObjectEncoder,
    APIResource, ListObject, SingletonAPIResource, ListableAPIResource,
    CreateableAPIResource, UpdateableAPIResource, DeletableAPIResource)
from fluidsurveys.util import json, logger  # noqa


# This is a pretty ugly solution to deprecating modules but a similar
# approach is used in Zope, Twisted and sanctioned in:
# https://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys as _sys
import warnings as _warnings
from inspect import isclass as _isclass, ismodule as _ismodule

_dogetattr = object.__getattribute__
_ALLOWED_ATTRIBUTES = (
    'api_key',
    'api_base',
    'api_version',
    'verify_ssl_certs'
)
_original_module = _sys.modules[__name__]


class _DeprecationWrapper(object):

    def __getattribute__(self, name):
        value = getattr(_original_module, name)

        # Allow specific names and resources
        if not (name[0] == '_' or
                name in _ALLOWED_ATTRIBUTES or
                _ismodule(value) or
                (_isclass(value) and
                 issubclass(value, APIResource) and
                 value is not APIResource)):
            _warnings.warn(
                'Attribute `%s` is being moved out of the `fluid` module '
                'in version 2.0 of the Fluid bindings.  Please access it '
                'in the appropriate submodule instead' % (name,),
                DeprecationWarning, stacklevel=2)

        return value

    def __setattr__(self, name, value):
        setattr(_original_module, name, value)

    def __delattr__(self, name):
        delattr(_original_module, name)

_sys.modules[__name__] = _DeprecationWrapper()

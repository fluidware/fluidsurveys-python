"""
Exceptions definitions.
"""
class WrapperException(Exception):
	""" Base Exception for all exceptions in the wrapper. """
	pass

class MissingArgs(WrapperException):
	"""Supplied arguments are not sufficient for calling a function."""
	def __init__(self, missing):
		self.missing = missing
		msg = "Missing argument(s): %s" % ", ".join(missing)
		super(MissingArgs, self).__init__(msg)

class UnsupportedVersion(WrapperException):
	"""User is trying to use an unsupported version of the API."""
	pass


class AuthorizationFailure(WrapperException):
	"""Cannot authorize API client."""
	pass

class HTTPError(WrapperException):
	""" Base class for all HTTP exceptions. """

	http_status = 0
	message = "HTTP Error"

	def __init__(self, message=None, details=None, responses=None, request_id=None, url=None, method=None, http_status=None):
		self.http_status = http_status or self.http_status
		self.message = message or self.message
		self.request_id = request_id
		self.method = method
		self.url = url
		self.responses = responses

class BadRequest(HTTPError):
	http_status = 400
	message = "Bad Request"
	
# Exceptions
class FluidError(Exception):

	def __init__(self, message=None, http_body=None, http_status=None,
				 json_body=None):
		super(FluidError, self).__init__(message)

		if http_body and hasattr(http_body, 'decode'):
			try:
				http_body = http_body.decode('utf-8')
			except:
				http_body = ('<Could not decode body as utf-8. '
							 'Please report to support@fluidsurveys.com>')

		self.http_body = http_body

		self.http_status = http_status
		self.json_body = json_body


class APIError(FluidError):
	pass


class APIConnectionError(FluidError):
	pass


class InvalidRequestError(FluidError):

	def __init__(self, message, param, http_body=None,
				 http_status=None, json_body=None):
		super(InvalidRequestError, self).__init__(
			message, http_body, http_status, json_body)
		self.param = param


class AuthenticationError(FluidError):
	pass

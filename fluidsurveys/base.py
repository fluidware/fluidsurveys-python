"""
Base utilities to build API operation managers and objects on top of.
"""
import six

from fluidsurveys.compat import urlencode
from fluidsurveys.http_client import Client

class Manager(object):
	"""Basic manager type providing common operations."""

	resource_class = None

	def __init__(self):
		super(Manager, self).__init__()
		self.client = Client()

	def _list(self, url, obj_class=None, body=None):
		""" List the collection """
		if body:
			resp, body = self.client.request(url, 'POST', body=body)
		else:
			respo, body = self.client.request(url, 'GET')

		if obj_class is None:
			obj_class = self.resource_class

		data = body
		try:
			data = data['values']
		except (KeyError, TypeError):
			pass
		return [obj_class(self, res, loaded=True) for res in data if res]

	def _get(self, url):
		""" Get an object from the collection """
		content, status_code = self.client.request('GET', url)
		return self.resource_class(content, loaded=True)

	def _head(self, url):
		""" Retrieve request header for an object """
		resp, body = self.client.request('HEAD', url)
		return resp.status_code == 204

	def _post(self, url, body, return_raw=False):
		resp, body = self.client.request('POST', url, body=body)
		if return_raw:
			return body
		return self.resource_class(self, body)

	def _put(self, url, body=None, responses_key=None):
		""" Update an object with PUT method """
		resp, body = self.client.request('PUT', url, body=body)
		if body is not None:
			if responses_key is not None:
				self.resource_class(self, body)
			else:
				return self.resource_class(self, body)

	def _patch(self, url, body=None, responses_key=None):
		""" Update a method with patch method"""
		resp, body = self.client.request('PATCH', url, body=body)
		if responses_key is not None:
			return self.resource_class(self, body)
		else:
			return self.resource_class(self, body)

	def _delete(self, url):
		""" Delete an object """
		return self.client.request("DELETE", url)



class CrudManager(Manager):
	""" Base Manager for Manipulating the entities. """
	collection_key = None
	key = None
	base_url = None

	def __init__(self, resource_class):
		self.resource_class = resource_class
		super(CrudManager, self).__init__()

	def build_url(self, dict_args_in_out=None):
		""" Build a resource url for a given resource. """

		if dict_args_in_out is None:
			dict_args_in_out = {}

		url = dict_args_in_out.pop('base_url', None) or self.base_url or ''
		url += '/%s' % self.collection_key

		entity_id = dict_args_in_out.pop('id', None)

		if entity_id is not None:
			url += '/%s' % entity_id

		return url

	def create(self, **kwargs):
		url = self.build_url(dict_args_in_out=kwargs)
		return self._create(url, {self.key: kwargs}, self.key)

	def get(self, **kwargs):
		return self._get(self.build_url(dict_args_in_out=kwargs))

	def head(self, **kwargs):
		url = self.build_url(dict_args_in_out=kwargs)

	def list(self, **kwargs):
		url = self.build_url(dict_args_in_out=kwargs)
		if kwargs:
			query = '?%s' % urllib.parse.urlencode(kwargs)
		else:
			query = ''
		return self._list('%(url)s%(query)s' % {'url': url, 'query':query}, self.collection_key)

	def put(self, **kwargs):
		return self._put(self.build_url(dict_args_in_out=kwargs))

	def delete(self, **kwargs):
		return self._delete(self.build_url(dict_args_in_out=kwargs))

	def find(self, **kwargs):
		pass

class Resource(object):
	""" Base class for fluidsurvey resource (user, survey, embed, etc.)"""

	manager_class = None

	def __init__(self, info, loaded=False):
		self._info = {}
		self._add_details(info)
		self._loaded= loaded
		self.manager = self.manager_class(self.__class__)

	@classmethod
	def retreive(cls, obj_id):
		instance = cls(info={'id':obj_id})
		instance.get()
		return instance

	def clone(self, **kwargs):
		instance = self.__class__(info=self._info)
		instance._add_details(**kwargs)
		return instance

	def _add_details(self, info):
		# import ipdb; ipdb.set_trace()
		for (k, v) in six.iteritems(info):
			setattr(self, k, v)
			self._info[k] = v	

	def _getattr__(self, k):
		if not k in self.__dict__:
			if not self.is_loaded():
				self.get()
				return self._getattr__(k)
			raise AttributeError(k)
		else:
			return self.__dict__[k]

	def __repre__(self):
		repkeys = sorted(k for k in self.__dict__ if k[0] != '_' and
			k != 'manager')
		info = ",".join("%s=%s" % (k, getattr(self, k)) for k in repkeys)
		return "<%s %s>" % (self.__class___.__name__, info)

	def get(self):
		self.set_loaded(True)
		if not hasattr(self.manager, 'get'):
			return
		new = self.manager.get(id=self.id)
		if new:
			self._add_details(new._info)

	def save(self):
		return self.manager.put(self)

	def delete(self):
		return self.manager.delete(self)

	def __eq__(self, other):
		if not isinstance(self, other):
			return NotImplemented
		if not isinstance(other, self.__class__):
			return False
		if hasattr(self, 'id') and hasattr(self, 'id'):
			return self.id == other.id
		return self._info == other.__info

	def is_loaded(self):
		return self._loaded

	def set_loaded(self, val):
		self._loaded = val



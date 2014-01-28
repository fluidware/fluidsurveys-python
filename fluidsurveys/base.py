"""
Base utilities to build API operation managers and objects on top of.
"""
import six

from fluidsurveys.compat import urlencode
from fluidsurveys.http_client import Client


class Manager(object):
	"""Basic manager type providing common operations."""

	resource_class = None
	collection_key = None
	key = None
	base_url = ''

	def __init__(self, resource_class, **kwargs):
		super(Manager, self).__init__()
		self.client = Client()
		self.resource_class = resource_class
		self.base_url = self.base_url % kwargs

	def build_url(self, entity_id=None):
		""" Build a resource url for a given resource. """

		url = self.base_url
		url += '/%s' % self.collection_key

		if entity_id is not None:
			url += '/%s' % entity_id

		return url

	def list(self, obj_class=None, body=None):
		""" List the collection """
		url = self.build_url()
		if body:
			body, status_code = self.client.request(url, 'POST', body=body)
		else:
			body, status_code = self.client.request('GET', url)

		if obj_class is None:
			obj_class = self.resource_class
		data = body['results']
		return [obj_class(res, loaded=True) for res in data if res]

	def get(self, entity_id):
		""" Get an object from the collection """
		url = self.build_url(entity_id=entity_id)
		content, status_code = self.client.request('GET', url)
		return self.resource_class(content, loaded=True)

	def head(self, entity_id):
		""" Retrieve request header for an object """
		url = self.build_url(entity_id=entity_id)
		resp, body = self.client.request('HEAD', url)
		return resp.status_code == 204

	def create(self, body):
		url = self.build_url()
		resp, body = self.client.request('POST', url, body=body)
		return self.resource_class(self, body)

	def update(self, obj):
		""" Update an object with PUT method """
		url = self.build_url(entity_id=obj.id)
		body, status_code = self.client.request('PUT', url, body=obj.to_dict())
		print body
		if body is not None:
			return self.resource_class(body)

	def delete(self, entity_id):
		""" Delete an object """
		url = self.build_url(entity_id=entity_id)
		return self.client.request("DELETE", url)

	def request(self, url, method, body=None):
		content, status_code = self.client.request(method, url, body=body)
		return content

	def find(self, **kwargs):
		r1 = self.findall(**kwargs)
		num = len(r1)

		if num == 0:
			msg = "No %s matching %s." % (self.resource_class.__name__, kwargs)
			raise exceptions.NotFound(404, msg)
		elif num>1:
			raise exceptions.NoUniqueMatch
		else:
			return r1[0]

	def finalall(self, **kwargs):
		found = []
		searches = kwargs.items()

		for obj in self.list():
			try:
				if all(getattr(obj, attr) == value for (attr, value) in searches):
					found.append(obj)
			except AttributeError:
				continue

		return found 


class Resource(object):
	""" Base class for fluidsurvey resource (user, survey, embed, etc.)"""

	manager_class = None

	def __init__(self, info={}, loaded=False, **kwargs):
		self._info = []
		self._add_details(info)
		self._loaded= loaded
		self.manager = self.manager_class(resource_class=self.__class__, **kwargs)

	@classmethod
	def retreive(cls, obj_id, **kwargs):
		instance = cls(info={'id':obj_id})
		instance.get()
		return instance

	@classmethod
	def list(cls):
		instance = cls()
		return instance.manager.list()

	def to_dict(self):
		return dict((key, getattr(self, key)) for key in self._info)


	def clone(self, **kwargs):
		instance = self.__class__(info=self._info)
		instance._add_details(**kwargs)
		return instance

	def _add_details(self, info):
		for (k, v) in six.iteritems(info):
			setattr(self, k, v)
			self._info.append(k)	

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
		new = self.manager.get(entity_id=self.id)
		if new:
			self._add_details(new.to_dict())

	def save(self):
		new = self.manager.update(self)
		if new:
			self._add_details(new.to_dict())

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



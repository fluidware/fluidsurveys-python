class AccessInfo(dict):
	
	def __init__(self, *args, **kwargs):
		super(AccessInfo, self).__init__(*args, **kwargs)

	@property
	def auth_token(self):
		raise NotImplementedError()

	@property
	def username(self):
		raise NotImplementedError()

	@property
	def method(self):
		raise NotImplementedError()

	@property
	def format(self):
		raise NotImplementedError()

	def render_header(self):
		raise NotImplementedError()


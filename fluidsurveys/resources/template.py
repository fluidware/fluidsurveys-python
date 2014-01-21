# Template Object

from fluidsurveys import base

class Template(base.Resource):
	""" Represent a template object """
	pass


class TemplateManager(base.CrudManager):
	resource_class = Template
	collection_key = 'templates'
	key = 'template'



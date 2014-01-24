from fluidsurveys import base

class TemplateManager(base.CrudManager):
	collection_key = 'templates'
	key = 'template'


class Template(base.Resource):
	manager_class = TemplateManager
	""" Represent a template object """
	pass




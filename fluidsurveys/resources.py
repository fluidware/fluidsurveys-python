from fluidsurveys import base

class TemplateManager(base.Manager):
	collection_key = 'templates'
	key = 'template'


class Template(base.Resource):
	manager_class = TemplateManager


class ResponseManager(base.Manager):
	collection_key = 'responses'
	key = 'response'
	base_url = "/surveys/%(survey)s"

class Response(base.Resource):
	manager_class = ResponseManager


class GroupManager(base.Manager):
	collection_key = 'groups'
	base_url = "/surveys/%(survey)s"

class Group(base.Resource):
	manager_class = ResponseManager

class SurveyManager(base.Manager):
	collection_key = 'surveys'
	key = 'survey'

	def get_structure(self, survey):
		return self.request("/surveys/%s/structure" % survey.id, 'GET')


class Survey(base.Resource):
	manager_class = SurveyManager
	_structure = None

	@property
	def structure(self):
	    if not self._structure:
	    	self._structure = self.manager.get_structure(self)
	    return self._structure

	 
	


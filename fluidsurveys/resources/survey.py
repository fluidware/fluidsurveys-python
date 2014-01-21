
from fluidsurveys import base


class Survey(base.Resource):
	pass


class SurveyManager(base.CrudManager):
	resource_class = Survey
	collection_key = 'surveys'
	key = 'survey'






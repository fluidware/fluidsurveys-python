
# Access Information
class AccessInfoClass(dict):

    def __call__(self, **kwargs):
        for key, value in kwargs.iteritems():
            self[key] = value

    def render_header(self):
        return {'AUTHORIZATION':'apikey %s@%s' % (self['username'], self['api_key'])}

AccessInfo = AccessInfoClass(api_key='0d23a5e41331cfb129baafefc81e3990a5533a11',api_base='http://10.0.110.86:8080/api/v3/', api_version='v2', username='faraji', verify_ssl_certs=False)
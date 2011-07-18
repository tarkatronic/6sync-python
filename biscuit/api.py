import base64
import urllib2

try:
    import json
except ImportError:
    import simplejson as json


class APIRequest(urllib2.Request):
    """A custom request handler to allow for arbitrary request methods, i.e. PUT and DELETE"""
    def __init__(self, *args, **kwargs):
        self._method = kwargs.get('method')
        if self._method:
            del kwargs['method']
        urllib2.Request.__init__(self, *args, **kwargs)
    
    def get_method(self):
        if self._method:
            return self._method
        return super(APIRequest, self).get_method()


class APIHandler:
    """This object will handle all methods associated with the 6sync RESTful API.
    Before any calls can be made to the API, you must provide both your API key and
    secret. This can be done via positional or keyword arguments, or through direct
    property assignment. i.e.:
    
    >>> api = APIHandler('my_api_key', 'my_api_secret') # Positional arguments
    >>> api = APIHandler(api_key='my_api_key', api_secret='my_api_secret') # Keyword arguments
    >>> api = APIHandler()
    >>> api.api_key = 'my_api_key' # Property assignment
    >>> api.api_secret = 'my_api_secret'
    """
    api_key = None
    api_secret = None
    api_uri = 'https://biscuit.6sync.com/api/'
    api_version = 'trunk'
    
    # Don't instantiate these until we need them
    def _get_auth_handler(self):
        if not hasattr(self, '_auth_handler'):
            if not self.api_key or not self.api_secret:
                raise TypeError, "Both api_key and api_secret must be set before a connection be established"
            self._auth_handler = urllib2.HTTPBasicAuthHandler(urllib2.HTTPPasswordMgrWithDefaultRealm())
            self._auth_handler.add_password(realm=None, uri=self.base_uri, user=self.api_key, passwd=self.api_secret)
        return self._auth_handler
    auth_handler = property(_get_auth_handler)
    
    def _get_opener(self):
        if not hasattr(self, '_url_opener'):
            self._url_opener = urllib2.build_opener(self.auth_handler)
        return self._url_opener
    opener = property(_get_opener)
    
    
    def _api_request(self, uri, method='GET', data=None):
        uri = '%s%s' % (self.base_uri, uri)
        request = APIRequest(uri, data=data, method=method)
        resp = self.opener.open(request)
        return json.loads(resp.read())
    
    base_uri = property(lambda self: '%s%s/' % (self.api_uri, self.api_version))
    
    
    def __init__(self, api_key=None, api_secret=None):
        if not ((api_key is None or isinstance(api_key, basestring)) and
                (api_secret is None or isinstance(api_secret, basestring))):
            raise TypeError, "api_key and api_secret must both be strings"
        self.api_key = api_key
        self.api_secret = api_secret
    
    
    # NOTE: In all cases, existing object not on your account return 401 Unauthorized; nonexistent objects return 404 Not Found
    def domain_list(self):
        """Retrieve a list of all DNS zones you currently have in your account.
        Returns a list of dictionaries containing all of your zone records.
        Example:
        >>> api.domain_list()
        [{"origin":"mydomain.com.", "active":true, "serial":2011070800,
        "description":"My main domain for doing crazy stuff!", "id":1234}, {...}]
        """
        return self._api_request('zones/')
    
    def domain_info(self, zone_id):
        """Retrieve information on an individual DNS zone from your account"""
        pass
    
    def domain_delete(self, zone_id):
        """Delete an individual DNS zone from your account
        WARNING: This method is destructive. That which has been done can not be undone."""
        pass
    
    def domain_create(self, origin, description=None):
        """Create a new DNS zone tied to your account"""
        pass
    
    def domain_resource_list(self, zone_id):
        """Retrieve a list of all records associated with an individual zone
        tied to your account"""
        pass
    
    def domain_resource_info(self, zone_id, record_id):
        """Retrieve information on an individual record tied to one of your DNS zones"""
        pass
    
    def domain_resource_delete(self, zone_id, record_id):
        """Delete an individual record from one of your DNS zones
        WARNING: This method is destructive. That which has been done can not be undone."""
        pass
    
    def domain_resource_create(self, zone_id, name, type, data, aux=None):
        """Create a new record to one of your DNS zones"""
        pass



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
        return  super(APIRequest, self).get_method()


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
    
    # Don't instantiate this until we need it
    def _get_opener(self):
        if not hasattr(self, '_url_opener'):
            self._url_opener = urllib2.build_opener(urllib2.HTTPSHandler(debuglevel=int(bool(self.debug))))
        return self._url_opener
    opener = property(_get_opener)
    
    
    def _api_request(self, uri, method='GET', data=None):
        uri = '%s%s' % (self.base_uri, uri)
        # We're going to let potential JSON encoding errors just pass right through
        if data is not None:
            data = json.dumps(data)
        request = APIRequest(uri, data=data, method=method)
        auth = 'Basic %s' % base64.encodestring('%s:%s' % (self.api_key, self.api_secret)).strip()
        request.add_header('Authorization', auth)
        request.add_header('Content-Type', 'application/json')
        resp = self.opener.open(request)
        if resp.code == 204:
            return True # 204 No Content; return True so the user knows it succeeded
        else:
            return json.loads(resp.read())
    
    base_uri = property(lambda self: '%s%s/' % (self.api_uri, self.api_version))
    
    
    def __init__(self, api_key=None, api_secret=None, debug=False):
        if not ((api_key is None or isinstance(api_key, basestring)) and
                (api_secret is None or isinstance(api_secret, basestring))):
            raise TypeError, "api_key and api_secret must both be strings"
        self.api_key = api_key
        self.api_secret = api_secret
        self.debug = bool(debug)
    
    
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
        try:
            uri = 'zones/%d/' % zone_id
        except TypeError:
            raise TypeError, "zone_id must be an integer"
        return self._api_request(uri)
    
    def domain_delete(self, zone_id):
        """Delete an individual DNS zone from your account
        WARNING: This method is destructive. That which has been done can not be undone."""
        try:
            uri = 'zones/%d/' % zone_id
        except TypeError:
            raise TypeError, "zone_id must be an integer"
        return self._api_request(uri, method='DELETE')
    
    def domain_create(self, origin, description='No description set!'):
        """Create a new DNS zone tied to your account"""
        if not isinstance(origin, basestring) or not isinstance(description, basestring):
            raise TypeError, "origin and description must both be strings"
        return self._api_request('zones/', method='POST', data={'origin':origin, 'description': description})
    
    def domain_resource_list(self, zone_id):
        """Retrieve a list of all records associated with an individual zone
        tied to your account"""
        try:
            uri = 'zones/%d/records/' % zone_id
        except TypeError:
            raise TypeError, "zone_id must be an integer"
        return self._api_request(uri)
    
    def domain_resource_info(self, zone_id, record_id):
        """Retrieve information on an individual record tied to one of your DNS zones"""
        try:
            uri = 'zones/%d/records/%d/' % (zone_id, record_id)
        except TypeError:
            raise TypeError, "zone_id and record_id must both be integers"
        return self._api_request(uri)
    
    def domain_resource_delete(self, zone_id, record_id):
        """Delete an individual record from one of your DNS zones
        WARNING: This method is destructive. That which has been done can not be undone."""
        try:
            uri = 'zones/%d/records/%d/' % (zone_id, record_id)
        except TypeError:
            raise TypeError, "zone_id and record_id must both be integers"
        return self._api_request(uri, method='DELETE')
    
    def domain_resource_create(self, zone_id, name, rrtype, data, aux=0):
        """Create a new resource record tied to one of your DNS zones. All fields
        are required, but where appropriate (or necessary) can be empty strings.
        Allowed record types: A, AAAA, ALIAS, CNAME, HINFO, MX, NS, PTR, RP, SRV, TXT"""
        try:
            uri = 'zones/%d/records/' % zone_id
        except TypeError:
            raise TypeError, "zone_id must be an integer"
        if not isinstance(name, basestring) or not isinstance(rrtype, basestring) or not isinstance(data, basestring):
            raise TypeError, "name, rrtype, data and aux must all be strings"
        try:
            aux = int(aux)
        except ValueError:
            raise TypeError, "aux must be an integer"
        allowed_types = ('A','AAAA','ALIAS','CNAME','HINFO','MX','NS','PTR','RP','SRV','TXT')
        if rrtype.upper() not in allowed_types:
            raise ValueError, "rrtype must be one of: %s" % ', '.join(allowed_types)
        return self._api_request(uri, method='POST',
            data={'name': name, 'type': rrtype.upper(), 'data': data, 'aux': aux})



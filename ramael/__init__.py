
import urllib
import base64
import threading
import gzip
from . import utils
import os
from . import poster
register_openers = poster.streaminghttp.register_openers
from io import StringIO
import io


try:
    import json
except ImportError:
    import simplejson as json

USER_AGENT = "spyral-python/1.1.6"

_defaultheaders = {}
_timeout = 10

_httplib = None
try:
    from google.appengine.api import urlfetch
    _httplib = 'urlfetch'
except ImportError:
    pass

if not _httplib:
    import urllib
    _httplib = "urllib"

# Register the streaming http handlers
register_openers()


def __request(method, url, params={}, headers={}, auth=None, callback=None):

    # Encode URL
    url_parts = url.split("\\?")
    url = url_parts[0].replace(" ", "%20")
    if len(url_parts) == 2:
        url += "?" + url_parts[1]

    # Lowercase header keys
    headers = dict((k.lower(), v) for k, v in headers.items())
    headers["user-agent"] = USER_AGENT

    data, post_headers = utils.urlencode(params)
    if post_headers is not None:
        headers = dict(headers.items() + post_headers.items())

    headers['Accept-encoding'] = 'gzip'

    if auth is not None:
        if len(auth) == 2:
            user = auth[0]
            password = auth[1]
            encoded_string = base64.b64encode(user + ':' + password)
            headers['Authorization'] = "Basic " + encoded_string
    

    for item in _defaultheaders:
      headers[item] = _defaultheaders[item]

    headers = headers

    _spyral_obj = None
    if _httplib == "urlfetch":
        res = urlfetch.fetch(url, payload=data, headers=headers, method=method, deadline=_timeout)
        _spyral_obj = spyral_obj(res.status_code,
                                           res.headers,
                                           res.content,res._method)
    else:
        if type(data) == str:
          data = str.encode(data)
        
        req = urllib.request.Request(method=method,url=url, data=data, headers=headers)

        try:
            response = urllib.request.urlopen(req, timeout=_timeout)
            _spyral_obj = spyral_obj(response.code, response.headers, response.read(),response._method)
        except urllib.error.HTTPError as e:
            response = e
            _spyral_obj = spyral_obj(response.code, response.headers, response.read(),response._method)
        except urllib.error.URLError as e:
            _spyral_obj = spyral_obj(0, {}, str(e.reason))

    if callback is None or callback == {}:
        return _spyral_obj
    else:
        callback(_spyral_obj)

# The following methods in the Mashape class are based on
# Stripe's python bindings which are under the MIT license.
# See https://github.com/stripe/stripe-python



# End of Stripe methods.

HEADERS_KEY = 'headers'
CALLBACK_KEY = 'callback'
PARAMS_KEY = 'params'
AUTH_KEY = 'auth'


def get_parameters(kwargs):
    params = kwargs.get(PARAMS_KEY, {})
    if params is not None and type(params) is dict:
        return dict((k, v) for k, v in params.items() if v is not None)
    return params


def get(url, **kwargs):
    params = get_parameters(kwargs)
    if len(params) > 0:
        if url.find("?") == -1:
            url += "?"
        else:
            url += "&"
        url += utils.dict2query(dict((k, v) for k, v in params.items() if v is not None))  # Removing None values/encode unicode objects

    return __dorequest("GET", url, {}, kwargs.get(HEADERS_KEY, {}), kwargs.get(AUTH_KEY, None), kwargs.get(CALLBACK_KEY, None))


def post(url, **kwargs):
    return __dorequest("POST", url, get_parameters(kwargs), kwargs.get(HEADERS_KEY, {}), kwargs.get(AUTH_KEY, None), kwargs.get(CALLBACK_KEY, None))


def put(url, **kwargs):
    return __dorequest("PUT", url, get_parameters(kwargs), kwargs.get(HEADERS_KEY, {}), kwargs.get(AUTH_KEY, None), kwargs.get(CALLBACK_KEY, None))


def delete(url, **kwargs):
    return __dorequest("DELETE", url, get_parameters(kwargs), kwargs.get(HEADERS_KEY, {}), kwargs.get(AUTH_KEY, None), kwargs.get(CALLBACK_KEY, None))

def ffs_method(url,method, **kwargs):
    return __dorequest(method.upper(), url, get_parameters(kwargs), kwargs.get(HEADERS_KEY, {}), kwargs.get(AUTH_KEY, None), kwargs.get(CALLBACK_KEY, None))


def patch(url, **kwargs):
    return __dorequest("PATCH", url, get_parameters(kwargs), kwargs.get(HEADERS_KEY, {}), kwargs.get(AUTH_KEY, None), kwargs.get(CALLBACK_KEY, None))

def request(method="GET",url=None,headers={},params={},callback=None,auth=None):
  method = method.upper()
  if method == "GET":
    return get(url,method=method,headers=headers,callback=callback,params=params,auth=auth)
  elif method == "POST":
    return post(url,method=method,headers=headers,callback=callback,params=params,auth=auth)
  elif method == "PUT":
    return put(url,method=method,headers=headers,callback=callback,params=params,auth=auth)
  elif method == "DELETE":
    return delete(url,method=method,headers=headers,callback=callback,params=params,auth=auth)
  elif method == "PATCH":
    return patch(url,method=method,headers=headers,callback=callback,params=params,auth=auth)
  else:
      ffs_method(url,method=method,headers=headers,callback=callback,params=params,auth=auth)

def default_header(name, value):
    _defaultheaders[name] = value


def clear_default_headers():
    _defaultheaders.clear()


def timeout(seconds):
    global _timeout
    _timeout = seconds


def __dorequest(method, url, params, headers, auth, callback=None):
    if callback is None:
        return __request(method, url, params, headers, auth)
    else:
        thread = threading.Thread(target=__request,
                                  args=(method,
                                        url,
                                        params,
                                        headers,
                                        auth,
                                        callback))
        thread.start()
        return thread


class spyral_obj(object):
    def __init__(self, code, headers, body,method):
        self._code = code
        self._headers = headers
        self.method=method

        if headers.get("Content-Encoding") == 'gzip':

            buf = io.BytesIO(body)
            f = gzip.GzipFile(fileobj=buf)
            body = f.read()

        self._raw_body = body
        self._body = self._raw_body
        self.jsonified = 0

        try:
            self.jsonified = json.loads(self._raw_body)
        except ValueError:
            # Do nothing
            pass

    @property
    def status(self):
        return self._code

    @property
    def text(self):
        return self._body.decode("utf-8") 

    @property
    def bytes_text(self):
        return self._raw_body

    @property
    def raw_headers(self):
        return self._headers
    @property
    def headers(self):
      tr = {}
      h = str(self._headers).split("\n")
      for item in h:
        item = item.replace(": ",":").replace(" : ",":")
        x = item.split(":")
        try:
          tr[x[0]] = x[1]
        except:
          ok ="why the heck isn't it removing"
      return tr
    def json(self):
      return dict(self.jsonified)
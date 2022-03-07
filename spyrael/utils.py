import os
from . import poster
register_openers = poster.streaminghttp.register_openers
import urllib
from io import IOBase
import io
def is_file(f):
  something = f
  x = isinstance(something, io.TextIOBase)
  y = isinstance(something, io.BufferedIOBase)
  z = isinstance(something, io.RawIOBase)
  a = isinstance(something, io.IOBase)
  list = [a,z,x,y]
  if True in list:
    return True
  else:
    return False
    
def to_utf8(value):
    if isinstance(value, str):
        return urllib.quote_plus(value.encode('utf-8'))

    return value


def _dictionary_encoder(key, dictionary):
    result = []
    for k, v in dictionary.items():
        if is_file(v) == True:
            continue
        key = to_utf8(key)
        k = to_utf8(k)
        v = to_utf8(v)
        result.append('{}[{}]={}'.format(key, k, v))

    return result


def dict2query(dictionary):
    """
    We want post vars of form:
    {'foo': 'bar', 'nested': {'a': 'b', 'c': 'd'}}
    to become:
    foo=bar&nested[a]=b&nested[c]=d
    """
    query = []
    encoders = {dict: _dictionary_encoder}
    for k, v in dictionary.items():
        if v.__class__ in encoders:
            nested_query = encoders[v.__class__](k, v)
            query += nested_query
        else:
            key = to_utf8(k)
            value = to_utf8(v)
            query.append('{}={}'.format(key, value))

    return '&'.join(query)


def urlencode(data):
    if isinstance(data, dict):
        for v in data.values():
            if is_file(v) == True:
                return multipart_encode(data)
        return dict2query(data), None
    else:
        return data, None


if __name__ == '__main__':
    print('...')
    print(dict2query({'foo': 'bar', 'nested': {'a': 'b', 'c': 'd'}}))
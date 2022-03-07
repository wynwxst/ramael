# Ramael
Ramael - An elegant http library focused on simplicity


### About:
An elegant modern http requests library for python

### Installtion:
`pip install ramael`

### Usage:
```python
import ramael
req = ramael.request(method="GET",url="someurl",headers={},callback=None,auth=None)
# or for a oneliner:
r = ramael.request("GET",url="someurl")
# methods for the ramael object
req.headers # headers in json format
req.raw_headers # headers in an object
req.status # Status eg 200
req.text # text in string
req.json() # text jsonified
req.bytes_text # completely raw text dk why you might want this
```


### Development:
Install buildproj:

`pip install buildproj`

`build`

In case of the binary not working:

`python buildbinary.py`

All processes are automated except for the sign in for pip, please be sure to also change the version and name in `setup.py

### Tests:
Install buildproj:

`pip install buildproj`

`build test`

In case of the binary not working:

`python buildbinary.py test`

### Todo:
make a binary for it
`.cli`


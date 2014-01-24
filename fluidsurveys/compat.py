"""
Python2/Python3 compatibility layer for wrapper
"""


import six

if six.PY3:
	# python 3
	import urllib
	import urllib.parse

	urlencode = urllib.parse.urlencode
	urljoin = urllib.parse.urljoin
	urlparse = urllib.parse.urlparse
	urlsplit = urllib.parse.urlsplit
	SplitResult = urllib.parse.SplitResult

else:
	# python 2
	import urllib
	import urllib2
	import urlparse

	urlencode = urllib.urlencode
	
	parse = urlparse
	urljoin = parse.urljoin
	urlparse = parse.urlparse
	urlsplit = parse.urlsplit
	SplitResult = parse.SplitResult

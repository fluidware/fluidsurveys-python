"""
Python2/Python3 compatibility layer for wrapper
"""


import six

if six.PY3:
	# python 3
	import urllib
	import urllib.parse

	urlencode = urllib.parse.urlencode

else:
	# python 2
	import urllib
	import urllib2

	urlencode = urllib.urlencode
	

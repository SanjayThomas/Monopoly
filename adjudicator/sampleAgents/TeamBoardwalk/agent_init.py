import sys
import six
from os import environ
from autobahn.twisted.wamp import ApplicationRunner


if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit("Not enough arguments")
	from riskyAgent import *
	# pass
	url = environ.get("CBURL", u"ws://127.0.0.1:4000/ws")
	if six.PY2 and type(url) == six.binary_type:
		url = url.decode('utf8')
	realm = environ.get('CBREALM', u'realm1')
	runner = ApplicationRunner(url, realm)
	runner.run(RiskyAgent)


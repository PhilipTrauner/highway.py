from traceback import print_exception
from sys import exc_info

def capture_trace():
	exc_type, exc_value, exc_traceback = exc_info()
	print_exception(exc_type, exc_value, exc_traceback)
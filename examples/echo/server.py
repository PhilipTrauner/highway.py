from wsgiref.simple_server import make_server
from ws4py.server.wsgirefserver import WebSocketWSGIRequestHandler

from highway import ServerWSGIApplication, WSGIServer
from highway import Server, Route

from json import JSONEncoder

class Custom:
	def __init__(self):
		self.custom = True


class CustomEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Custom):
			return {
				"custom" : obj.custom,
				}
		return JSONEncoder.default(self, obj)


class Echo(Route):
	def run(self, data, handler):
		print(data, type(data))


class Handler(Server):
	def __init__(self, sock, routes, debug=False):
		super().__init__(sock, routes, debug=debug)

	def ready(self):
		# String
		self.send("text", "echo")
		# Bytes
		self.send(b"text", "echo")
		# Integer
		self.send(1, "echo")
		# Float
		self.send(1.0, "echo")
		# Boolean
		self.send(True, "echo")
		# None Type
		self.send(None, "echo")
		# List
		self.send([1, 2, 3], "echo")
		# Dictionary
		self.send({"key" : "value"}, "echo")
		# Custom object
		self.send({"custom" : Custom()}, "echo", json_encoder=CustomEncoder)
		# Indexed dictionary
		self.send({1 : "test", 2 : "test"}, "echo", indexed_dict=True)


server = make_server("127.0.0.1", 8500,
	server_class=WSGIServer, handler_class=WebSocketWSGIRequestHandler,
	app=ServerWSGIApplication(Handler, routes={"echo" : Echo()}, debug=True))

server.initialize_websockets_manager()

try:
	server.serve_forever()
except KeyboardInterrupt:
	server.server_close()
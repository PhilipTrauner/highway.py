from highway import Client, Route


class Handler(Client):
	def __init__(self, url, routes, debug=False):
		super().__init__(url, routes, debug=debug)


class Echo(Route):
	def run(self, data, handler):
		handler.send(data, "echo")


ws = Handler("ws://127.0.0.1:8500", routes={"echo" : Echo()}, debug=True)
ws.connect()

try:
	ws.run_forever()
except KeyboardInterrupt:
	ws.close()
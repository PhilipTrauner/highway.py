from ujson import dumps as ujson_dumps

from highway import Server
from highway import Handler as Handler_

class Handler(Handler_):
	def __init__(self, websocket, server):
		super().__init__(websocket, server)

	async def on_ready(self):
		# String
		await self.send("text", "echo")
		# Bytes
		await self.send(b"text", "echo")
		# Integer
		await self.send(1, "echo")
		# Float
		await self.send(1.0, "echo")
		# Boolean
		await self.send(True, "echo")
		# None Type
		await self.send(None, "echo")
		# List
		await self.send([1, 2, 3], "echo")
		# Dictionary
		await self.send({"key" : "value"}, "echo")
		# Custom object
		await self.send({"custom" : Custom()}, "echo")

server = Server(Handler, debug=True)

class Custom:
	def __init__(self):
		self.custom = True

	def __json__(self):
		return ujson_dumps({"custom" : self.custom})


@server.route("echo")
async def echo(data, handler):
	print(data, type(data))


server.start("localhost", 1337)
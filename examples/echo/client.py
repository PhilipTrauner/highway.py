from highway import Client
from highway import Handler as Handler_


class Handler(Handler_):
	def __init__(self, websocket, base):
		super().__init__(websocket, base)


client = Client(Handler, debug=True)


@client.route("echo")
async def echo(data, handler):
	await handler.send(data, "echo")


client.start("localhost", 1337)
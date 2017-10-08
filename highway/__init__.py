from asyncio import get_event_loop

from enum import Enum
from abc import ABC, abstractmethod

from websockets import serve, connect
from websockets.framing import OP_BINARY
from websockets.exceptions import ConnectionClosed, InvalidState

# asyncio used logging from the standard library
from . import log as logging
from .utils import capture_trace

from .header import pack_message, parse_metadata
from .header import HeaderLayoutInvalidError
from .header import METADATA_LENGTH

from .routing import assemble_routing, meta_route
from .routing import BASE_PEER_EXCHANGE_ROUTES
from .routing import BASE_PEER_REVERSE_EXCHANGE_ROUTES
from .routing import META_ROUTE

from .close_reasons import *

from .converters import convert


class Shared(ABC):
	def __init__(self, handler_class, debug=False):
		self.handler_class = handler_class
		self.debug = debug

		# {"meta" : meta_route}
		self.routes = {}
		# {meta_route : "meta"}
		self.reverse_routes = {}
		# {0 : "meta"}
		self.exchange_routes = {}
		# {"meta" : 0}
		self.reverse_exchange_routes = {}

		# Add meta route
		self.route(META_ROUTE)(meta_route)


		# Peer routes have not been received yet. As per convention the meta route
		# has to exist and we need it for our first send to succeed (otherwise it
		# would fail during route lookup).
		self.peer_exchange_routes = BASE_PEER_EXCHANGE_ROUTES.copy()
		self.peer_reverse_exchange_routes = \
			BASE_PEER_REVERSE_EXCHANGE_ROUTES.copy()


	@abstractmethod
	def start(self, address, port):
		pass


	def route(self, route):
		def wrapped(func):
			routes = self.routes.copy()
			routes[route] = func
			
			self.routes = routes
			
			self.reverse_routes, \
			self.exchange_routes, \
			self.reverse_exchange_routes = assemble_routing(self.routes)
		return wrapped


	async def consumer(self, websocket):
		handler = self.handler_class(websocket, self)

		await self.on_connect(handler)

		while websocket.open:
			# Receive message
			try:
				message = await websocket.recv()
			except ConnectionClosed as e:
				handler.on_close(e.code, e.reason)
				return
			
			# Extract data type and route id
			try:
				data_type, m_route = parse_metadata(message)
			except HeaderLayoutInvalidError:
				await handler.close(**MALFORMED_HEADER)
				return
			
			# Convert route id back to string
			try:
				route = self.exchange_routes[m_route]
			except KeyError:
				await handler.close(**ROUTE_DOES_NOT_EXIST)
				return
			
			try:
				data = convert(message[METADATA_LENGTH:], data_type)
			except ConvertFailedError:
				await handler.close(**CONVERT_FAILED)
				return

			if self.debug:
				data_repr = str(data).replace("\n", " ")
				if len(data_repr) > 80:
					data_repr = data_repr[:80] + "..."
				logging.info("Received '%s' on route '%s': %s (%s:%d)" % (
					type(data).__name__,
					route, data_repr, websocket.remote_address[0],
					websocket.remote_address[1]))
			
			# Call route
			try:
				await self.routes[route](data, handler)
			except Exception as e:
				await handler.close(**INTERNAL_ERROR)
				capture_trace()
				return


	async def on_connect(self, handler):
		pass


	async def on_exchanged(self, handler):
		pass


class Handler:
	def __init__(self, websocket, base):
		self._websocket = websocket
		self._base = base
	

	@property
	def open(self):
		return self._websocket.open


	@property
	def routes(self):
		return self._base.routes


	@property
	def strict(self):
		return self._base.strict


	@property
	def debug(self):
		return self._base.debug


	@property
	def remote_address(self):
		return self._websocket.remote_address


	async def close(self, code=1000, reason=""):
		self.on_close(code, reason)
		await self._websocket.close(code=code, reason=reason)


	async def send(self, data, route):
		try:
			await self._websocket.write_frame(OP_BINARY, 
				pack_message(
					data,
					self._base.peer_reverse_exchange_routes[route]
				)
			)
		except KeyError:
			await self.close(**ROUTE_DOES_NOT_EXIST)
		except InvalidState:
			await self.close(**INVALID_STATE)
		else:
			if self.debug:
				data_repr = str(data).replace("\n", " ")
				if len(data_repr) > 80:
					data_repr = data_repr[:80] + "..."
				logging.info("Sending '%s' on route '%s': %s (%s:%d)" % (
					type(data).__name__, route, data_repr, 
					self.remote_address[0], self.remote_address[1]))


	async def on_ready(self):
		pass


	def on_close(self, code, reason):
		if code != 1000:
			logging.error("Connection closed (%i): '%s'" % (code, 
				reason))


class Server(Shared):
	def __init__(self, handler_class, debug=False):
		super().__init__(handler_class, debug=debug)


	async def on_connect(self, handler):
		await handler.send(self.exchange_routes, META_ROUTE)


	async def server(self, websocket, path):
		await self.consumer(websocket)


	def start(self, address, port):
		start_server = serve(self.server, address, port)

		get_event_loop().run_until_complete(start_server)
		get_event_loop().run_forever()



class Client(Shared):
	def __init__(self, handler_class, debug=False):
		super().__init__(handler_class, debug=debug)


	async def on_exchange(self, handler):
		await handler.send(handler._base.exchange_routes, META_ROUTE)


	async def client(self, address, port, wss):
		async with connect("ws%s://%s:%i" % ("s" if wss else "", 
			address, port)) as websocket:
			
			await self.consumer(websocket)


	def start(self, address, port, wss=False):
		get_event_loop().run_until_complete(self.client(
			address, port, wss))
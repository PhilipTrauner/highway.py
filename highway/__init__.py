import struct
import json

from . import logging
from .utils import capture_trace

from ws4py.websocket import WebSocket as WebSocketServer_
from ws4py.client.threadedclient import WebSocketClient

from ws4py.server.wsgiutils import WebSocketWSGIApplication
from ws4py.server.wsgirefserver import WSGIServer as _WSGIServer
from ws4py.manager import WebSocketManager as _WebSocketManager
from ws4py import format_addresses

class WebSocketManager(_WebSocketManager):
	def run(self):
		self.running = True
		while self.running:
			with self.lock:
				polled = self.poller.poll()
			if not self.running:
				break

			for fd in polled:
				if not self.running:
					break

				ws = self.websockets.get(fd)
				if ws and not ws.terminated:
					try:
						x = ws.once()
					# Treat the error as if once() had returned None
					except:
						x = None
						logging.error("Terminating websocket %s" %
							format_addresses(ws))
						capture_trace()
					if not x:
						with self.lock:
							self.websockets.pop(fd, None)
							self.poller.unregister(fd)

						if not ws.terminated:
							try:
								ws.terminate()
							except:
								logging.error("Error in termination logic.")
								capture_trace()


class WSGIServer(_WSGIServer):
	def initialize_websockets_manager(self):
		"""
		Call this to start the underlying websockets
		manager. Make sure to call it once your server
		is created.
		"""
		self.manager = WebSocketManager()
		self.manager.start()


class WebSocketServer(WebSocketServer_):
	def _write(self, b):
		"""
		Trying to prevent a write operation
		on an already closed websocket stream.
		This cannot be bullet proof but hopefully
		will catch almost all use cases.
		"""
		if self.terminated or self.sock is None:
			raise RuntimeError("Cannot send on a terminated websocket")


		# If the client disconnects in an unexpected way.
		try:
			self.sock.sendall(b)
		except BrokenPipeError:
			logging.warning("Client disconnected in an unexpected way.")


class ServerWSGIApplication(WebSocketWSGIApplication):
	def __init__(self, handler_cls, routes=None, debug=False):
		super().__init__(self, handler_cls=handler_cls)

		self.routes = routes if type(routes) is dict else {}
		self.debug = debug

	def make_websocket(self, sock, protocols, extensions, environ):
		websocket = self.handler_cls(sock, self.routes, self.debug)
		environ['ws4py.websocket'] = websocket
		return websocket


INDEXED_DICT = 5
NoneType = None.__class__

DATA_TYPES = {str : 0, dict : 1,
	list : 1, bytes : 2,
	int : 3, float : 4, INDEXED_DICT : 5,
	NoneType : 6, bool : 7}


def reverse_dict(dict):
	return {v : k for k, v in dict.items()}


REVERSE_DATA_TYPES = reverse_dict(DATA_TYPES)

META_ROUTE = "meta"
META_ROUTE_INDEX = 0

PACK_FORMAT = "BH"
METADATA_LENGTH = struct.calcsize(PACK_FORMAT)


# Routing related
class Route:
	def run(self, data, handler):
		pass

	def start(self, handler):
		pass


def create_routes(routes):
	routes = routes.copy()
	for prefix in routes:
		if type(routes[prefix]) is tuple or type(routes[prefix]) is list:
			routes[prefix] = routes[prefix][0](**routes[prefix][1])
	return routes


def create_exchange_map(routes):
	exchange_map = {0 : META_ROUTE}
	exchange_id = 1
	for route in routes:
		if route != META_ROUTE:
			exchange_map[exchange_id] = route
			exchange_id += 1
	return exchange_map


def create_metadata(data_type, converted_route, indexed_dict=False):
	return struct.pack(PACK_FORMAT,
		DATA_TYPES[data_type] if not indexed_dict else DATA_TYPES[INDEXED_DICT],
		converted_route)


def convert_exchange_map(routes):
	exchange_map = {}
	for key in routes:
		if key.isnumeric() and type(routes[key]) is str:
			exchange_map[int(key)] = routes[key]
		else:
			return None
	return exchange_map


class ConvertFailedError(ValueError):
	def __init__(self):
		super(ValueError, self).__init__("conversion failed (invalid data type supplied)")


# Built-in routes
class Meta(Route):
	def run(self, data, handler):
		if type(data) is dict:
			if "routes" in data:
				peer_exchange_routes = convert_exchange_map(data["routes"])
				if peer_exchange_routes != None:
					handler.peer_exchange_routes = peer_exchange_routes
					if handler.debug:
						logging.success("Received peer exchange routes: %s" % str(data))
					handler.peer_reverse_exchange_routes = reverse_dict(handler.peer_exchange_routes)
					if issubclass(handler.__class__, Client):
						handler.send({"routes" : handler.exchange_routes}, META_ROUTE)
					if hasattr(handler, "ready"):
						handler.ready()
					if handler.debug:
						logging.info("Launching routes.")
					
					for route in handler.routes:
						if hasattr(handler.routes[route], "start"):
							handler.routes[route].start(handler)

					if handler.debug:
						logging.info("Routes launched.")
				else:
					logging.error("Received invalid exchange routes.")
					handler.close(reason="Invalid exchange routes")


def pack_message(data, exchange_route,
	debug=False, indexed_dict=False, json_encoder=None):
	
	data, original_data_type = prepare_data(data, json_encoder)
	return create_metadata(original_data_type, exchange_route,
		indexed_dict=indexed_dict) + data


def parse_metadata(message):
	metadata = struct.unpack(PACK_FORMAT, message[:METADATA_LENGTH])
	return REVERSE_DATA_TYPES[metadata[0]], metadata[1]


def convert_data(data, data_type, debug=False):
	try:
		if data_type == str:
			try:
				data = data.decode()
			except UnicodeDecodeError:
				logging.warning("Unicode characters are not properly encoded. "
					"Falling back to unicode_escape.")
				data = data.decode("unicode_escape")
		elif data_type == int:
			data = int(data.decode())
		elif data_type == float:
			data = float(data.decode())
		elif data_type == bool:
			data = bool(int(data.decode()))
		elif data_type in (dict, list):
			data = json.loads(data.decode())
		elif data_type == INDEXED_DICT:
			data = json.loads(data.decode())
			indexed_data = {}
			for key in data:
				indexed_data[int(key)] = data[key]
			data = indexed_data
		elif data_type == NoneType:
			data = None
	except Exception:
		logging.error("Data conversion failed.")
		capture_trace()
		return None
	return data


def prepare_data(data, json_encoder):
	original_data_type = type(data)
	if original_data_type is str:
		data = data.encode()
	elif original_data_type in (int, float):
		data = str(data).encode()
	elif original_data_type is bool:
		# Faster than int(data)
		data = str(1 if data else 0).encode()
	elif original_data_type is dict or original_data_type is list:
		data = json.dumps(data, separators=(',',':'), cls=json_encoder).encode()
	elif original_data_type is NoneType:
		data = "".encode()
	# Datatype that couldn't normally be sent but has an json encoder attched
	# Mostly used for sending single objects
	elif json_encoder != None:
		data = json.dumps(data, separators=(',',':'), cls=json_encoder).encode()
		original_data_type = dict
	return data, original_data_type


class Shared:
	def __init__(self, routes, debug=False):
		self.routes = routes
		self.routes[META_ROUTE] = Meta()
		self.routes = create_routes(self.routes)
		self.reverse_routes = reverse_dict(self.routes)
		self.exchange_routes = create_exchange_map(self.routes)
		self.reverse_exchange_routes = reverse_dict(self.exchange_routes)
		# Peer routes have not been received yet. As per convention the meta route
		# has to exist and we need it for our first send to succeed (otherwise it
		# would fail during route lookup).
		self.peer_exchange_routes = {META_ROUTE_INDEX : META_ROUTE}
		self.peer_reverse_exchange_routes = reverse_dict(self.peer_exchange_routes)
		self.debug = debug

		self.received_message = self._received_message
		self.raw_send = self.send
		self.send = self._send


	def _received_message(self, message):
		message = message.data
		try:
			data_type, m_route = parse_metadata(message)
		except struct.error:
			self.close(reason="Malformed header")
			return
		try:
			route = self.exchange_routes[m_route]
		except KeyError:
			capture_trace()
			logging.error("Received message with non-existing route '%d' from '%s:%d'" % (
				m_route, self.peer_address[0], self.peer_address[1]))
			return
		data = convert_data(message[METADATA_LENGTH:], data_type)
		if self.debug:
			data_repr = str(data).replace("\n", " ")
			if len(data_repr) > 80:
				data_repr = data_repr[:80] + "..."
			logging.info("Received '%s' on route '%s': %s (%s:%d)" % (
				type(data).__name__ if not data_type == INDEXED_DICT else "indexed_dict",
				route, data_repr, self.peer_address[0],
				self.peer_address[1]))
		try:
			route = self.routes[route]
		except KeyError as e:
			capture_trace()
			# Did the exception occur during route lookup or in the route itself?
			# Will still print the warning if the missing key is in the route itself
			if e.args[0] == route:
				logging.warning("'%s' does not exist." % route)
		else:
			route.run(data, self)


	def _send(self, data, route, indexed_dict=False, json_encoder=None):
		try:
			self.raw_send(pack_message(data,
				self.peer_reverse_exchange_routes[route],
				debug=self.debug, indexed_dict=indexed_dict,
				json_encoder=json_encoder),
			binary=True)
		except KeyError:
			capture_trace()
			logging.error("'%s' is not a valid peer route." % route)
		else:
			if self.debug:
				data_repr = str(data).replace("\n", " ")
				if len(data_repr) > 80:
					data_repr = data_repr[:80] + "..."
				logging.info("Sent '%s' on route '%s': %s (%s:%d)" % (
					type(data).__name__, route, data_repr, self.peer_address[0],
					self.peer_address[1]))

	def ready(self):
		pass



class Server(WebSocketServer, Shared):
	def __init__(self, sock, routes, debug=False):
		WebSocketServer.__init__(self, sock)
		Shared.__init__(self, routes, debug=debug)


	def opened(self):
		self.send({"routes" : self.exchange_routes}, META_ROUTE)



class Client(WebSocketClient, Shared):
	def __init__(self, url, routes, debug=False):
		WebSocketClient.__init__(self, url)
		Shared.__init__(self, routes, debug=debug)
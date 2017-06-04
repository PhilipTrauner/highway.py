<p align="center">
	<img src="https://cloud.githubusercontent.com/assets/9287847/26756438/93c1ff54-48a2-11e7-981e-37aeb7b2383c.png" height="150"></img>
</p>
<p align="center">
	<strong>highway.py</strong>
</p>

![Python version support: 3](https://img.shields.io/badge/python-3-green.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

> **highway** is a *lightweight*, *route-based* and *data-type preserving* network protocol framework built on top of *WebSockets*.  It facilitates [routes](#route) as a means of data transmission.

## Implementation
**highway.py** is built on top of [ws4py](https://github.com/Lawouach/WebSocket-for-Python) (This **will** change in the future because [ws4py](https://github.com/Lawouach/WebSocket-for-Python) is a buggy mess). This repo contains the **client** and **server** (currently only supports handshakes over [wsgiref](https://github.com/python/cpython/tree/master/Lib/wsgiref)) implementation.

A [JavaScript](https://github.com/PhilipTrauner/highway.js) **client** is also in the works.

## Status
**highway.py** is in a very early stage and should probably not be used in production. The documentation is also severely lacking. Even this README is incomplete!

## Concepts
### Handler
#### Server
```python
from highway import Server

class Handler(Server):
    def __init__(self, sock, routes, debug=False):
        super().__init__(sock, routes, debug=debug)
    
    
```

#### Client
```python
from highway import Client

class Handler(Client):
    def __init__(self, url, routes, debug=False):
        super().__init__(url, routes, debug=debug)
    
    
```
##### Callable Methods
* `send(self, data, route, indexed_dict=False, json_encoder=None)`

##### Override-able Methods
* `opened(self)`  
Called before handshake is completed (don't forget to call `super().opened()`)
* `ready(self)`  
Called after handshake is completed.

### Route
```python
from highway import Route

class Echo(Route):
    def run(self, data, handler):
        handler.send(data, "echo")
        
    def start(self, handler):
        pass
```
A client → server / server → client construct.  
Has to be defined on the receiving end (client or server) to handle incoming messages.

##### Override-able Methods
* `run(self, data, handler)`  
Called on data receive.
* `start(self, handler)`  
Called when the connection becomes ready.

Routes are essentially bandwidth neutral, use as many of them as you like!

### Examples
* [Echo server/client](https://github.com/PhilipTrauner/highway.py/tree/master/examples/echo).

### Installation
* pip
    ```bash
    pip3 install highway.py
    ```
* Manual
    ```bash
    git clone https://github.com/PhilipTrauner/highway.py.git
    cd highway.py
    python3 setup.py install
    ```

### FAQ
* Should I use this over something like [socket.io](https://socket.io)?  
At the moment you really shouldn't.

* Why should I use this?  
I like to think of **highway** as a more lightweight version of [socket.io](https://socket.io) (primarily because the feature-set is much smaller). If that's somewhat appealing to you give it a try!  

* Future plans?  
    - [ ] Built-in client targeting mechanism
    - [ ] 'Piping': client → client connections piped over the server
    - [ ] Better in-line documentation
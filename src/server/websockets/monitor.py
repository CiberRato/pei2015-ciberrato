import time
import socket
import json
from threading import Thread
import cherrypy
from ws4py.manager import WebSocketManager
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import sys


class Root(object):
    # Define the URL's
    @cherrypy.expose
    def index(self):
        return "Ups, what are you doing here? ^^"

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))


# WebSocketManager, this will store the Web Sockets to get access to them
m = WebSocketManager()
data_stream = ""

if len(sys.argv) == 4:
    socket_host = sys.argv[1]
    socket_port = int(sys.argv[2])
    url = sys.argv[3]
else:
    socket_host = '0.0.0.0'
    socket_port = 7777
    url = '/ws'


def monitor():
    global data_stream

    host = "127.0.0.1"
    port = 10000

    sim_viewer_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sim_viewer_connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sim_viewer_connect.bind((host, port))
    sim_viewer_connect.listen(1)
    sim_viewer, addr = sim_viewer_connect.accept()

    while True:
        data = sim_viewer.recv(1024)
        if str(data) == "END":
            break

        data_stream += data
        m.broadcast(data)

    sim_viewer_connect.shutdown(socket.SHUT_RDWR)
    sim_viewer_connect.close()
    sim_viewer.shutdown(socket.SHUT_RDWR)
    sim_viewer.close()

    # see who is connected
    # print m.websockets

    m.close_all()
    s.exit()
    exit()


class WebSocketHandler(WebSocket):
    def received_message(self, message):
        global data_stream
        """
        This is the web socket handler, I will use it if the client doesn't get the packages well
        When the client opens one connection to the Web socket it will send a message "OK"
        This is important to get the Web socket reference since the opened is called recursively by the
        Manager ...
        If is necessary authentication it can be made a /api/ call to see if the user is logged in or retrieve
        a token or something like this ...
        """

        if str(message) != "OK":
            # Handle the missing package number
            # self.send()
            pass
        elif len(data_stream) > 0:
            # send missing packages
            to_send = json.dumps(data_stream)
            self.send(to_send)

        m.add(self)


class Server():
    def __init__(self):
        # 0.0.0.0 => available to all interfaces
        cherrypy.config.update({'server.socket_host': socket_host,
                                'server.socket_port': 7777,
                                'server.thread_pool': 10,
                                'engine.autoreload.on': False})

    @staticmethod
    def run():
        WebSocketPlugin(cherrypy.engine).subscribe()
        cherrypy.tools.websocket = WebSocketTool()
        cherrypy.engine.timeout_monitor.unsubscribe()
        cherrypy.quickstart(Root(), '', config={
            url: {
                'tools.websocket.on': True,
                'tools.websocket.handler_cls': WebSocketHandler
            }
        })

    @staticmethod
    def stop():
        cherrypy.engine.stop()

    @staticmethod
    def exit():
        cherrypy.engine.exit()


if __name__ == '__main__':
    s = Server()

    thread_monitor = Thread(target=monitor)
    thread_monitor.daemon = True
    thread_monitor.start()

    s.run()
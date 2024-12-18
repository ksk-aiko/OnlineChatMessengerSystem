import socket
import threading
import json

# サーバ設定
TCP_PORT = 5000
UDP_PORT = 6000
BUFFER_SIZE = 4096

rooms = {}
tokens = {}



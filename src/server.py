import socket
import threading
import json

# server settings
TCP_PORT = 5000
UDP_PORT = 6000
BUFFER_SIZE = 4096

# room and token management
rooms = {}
tokens = {}

def handle_tcp_connection(client_socket, address):
    # Handles tcp connections. Receives requests from clients and creates or joins chat rooms.
    try:
        # receive data from client
        data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        request = json.loads(data)
        operation = request.get("operation")
        response = {}
        
        if operation == "create_room":
            room_name = request["room_name"]
            username = request["username"]
            token = f"{room_name}-{username}-{address[0]}"

            if room_name not in rooms:
                rooms[room_name] = {"host": token, "members": [token]}
                tokens[token] = {"username": username, "ip": address[0]}
                response = {"status": "success", "token": token}
            else:
                response = {"status":  "error", "message":  "Room already exists."}
        
        elif operation == "join_room":
            room_name = request["room_name"]
            username = request["username"]
            token = f"{room_name}-{username}-{address[0]}"

            if room_name in rooms:
                rooms[room_name]["members"].append(token)
                tokens[token] = {"username": username, "ip": address[0]}
                response = {"status": "success", "token": token}
            else:
                response = {"status": "error", "message": "Room not found."}
        
        # send response to client
        client_socket.send(json.dumps(response).encode('utf-8'))
    except Exception as e:
        print(f"Error handling TCP connection: {e}")
    finally:
        client_socket.close()




"""
This module implements a simple online chat messenger system server using TCP and UDP protocols.
Functions:
    handle_tcp_connection(client_socket, address):
        Handles TCP connections. Receives requests from clients to create or join chat rooms.
    udp_handler(server_socket):
        Handles UDP connections. Receives messages from clients and distributes them to all clients in the room.
    main():
        Configures and starts the TCP and UDP servers, and handles incoming connections.
Global Variables:
    TCP_PORT (int): The port number for TCP connections.
    UDP_PORT (int): The port number for UDP connections.
    BUFFER_SIZE (int): The buffer size for receiving data.
    rooms (dict): A dictionary to manage chat rooms and their members.
    tokens (dict): A dictionary to manage user tokens and their associated information.
"""

import socket
import threading
import json

# server settings
TCP_PORT = 5001
UDP_PORT = 6001
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

def udp_handler(server_socket):
    # Handles UDP connections. Receives messages from clients and distributes them to all clients in the room.
    while True:
        try:
            # receive udp data
            data, address = server_socket.recvfrom(BUFFER_SIZE)
            print(f"Received UDP data from {address}: {data.decode('utf-8')}")
            request = json.loads(data.decode('utf-8'))
            token = request.get("token")
            room_name = request.get("room_name")
            operation = request.get("operation")

            if token is None:
                print("Invalid request: No token provided.")
                continue
            # Check room and token
            if room_name in rooms and token in rooms[room_name]["members"]:
                if operation == "message":
                    username = request.get("username")
                    message_text = request.get("message")
                    for member_token in rooms[room_name]["members"]:
                        target = tokens.get(member_token)
                        if target:
                            target_ip = target["ip"]
                            response = {
                                "status": "success",
                                "sender": username,
                                "message": message_text
                            }
                            server_socket.sendto(json.dumps(response).encode('utf-8'), (target_ip, UDP_PORT))
                elif operation == "leave":
                    username = request.get("username")
                    if token in rooms[room_name]["members"]:
                        rooms[room_name]["members"].remove(token)
                        for member_token in rooms[room_name]["members"]:
                            target = tokens.get(member_token)
                            if target:
                                target_ip = target["ip"]
                                response = {
                                    "status": "success",
                                    "system_message": f"{username} has left the room."
                                }
                                server_socket.sendto(json.dumps(response).encode('utf-8'), (target_ip, UDP_PORT))
        except Exception as e:
            print(f"Error handling UDP handler: {e}")
            # Stop loop if a specific error occurs
            if str(e) == "Stop loop":
                break

def main():
    # Configure TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("0.0.0.0", TCP_PORT))
    tcp_socket.listen(5)

    # Configure UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", UDP_PORT))

    print(f"Server is running on TCP:{TCP_PORT} and UDP:{UDP_PORT}")

    # Start UDP handler in a separate thread
    threading.Thread(target=udp_handler, args=(udp_socket,), daemon=True).start()

    # Wait for TCP connection
    while True:
        client_socket, address = tcp_socket.accept()
        threading.Thread(target=handle_tcp_connection, args=(client_socket, address), daemon=True).start()

if __name__ == "__main__":
    main()
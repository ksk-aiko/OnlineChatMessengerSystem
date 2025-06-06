"""
Client module for Online Chat Messenger System.

This module provides functionality to connect to a chat server, create or join chat rooms,
and exchange messages with other clients. It uses both TCP and UDP connections:
- TCP for connection management (creating/joining rooms)
- UDP for message exchange (defined but not implemented in this snippet)

Constants:
    TCP_HOST (str): The hostname of the server to connect to, default is "localhost"
    TCP_PORT (int): Port number for TCP connection, default is 5000
    UDP_PORT (int): Port number for UDP connection, default is 6000
    BUFFER_SIZE (int): Buffer size for socket communication, default is 4096

Functions:
    connect_to_server(host, room_name, username, operation): Establishes a TCP connection
        to the server for room creation or joining.
    main(): Entry point for the client application, handles user input and initial connection.
"""

import socket
import json
import threading
import sys

# Constants
# TCP and UDP settings
TCP_HOST = "localhost"
TCP_PORT = 5001
UDP_PORT = 6001
BUFFER_SIZE = 4096

# Function to connect to the server
# and create or join a chat room
def connect_to_server(host, room_name, username, operation):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, TCP_PORT))

        request = {
            "operation": operation,
            "room_name": room_name,
            "username": username
        }

        client_socket.send(json.dumps(request).encode('utf-8'))

        response = client_socket.recv(BUFFER_SIZE).decode('utf-8')
        return json.loads(response)

    except Exception as e:
        print(f"Error connecting to server: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        client_socket.close()

# Function to send and receive messages
def message_sender(udp_socket, server_address, token, room_name, username):
    print("Message sender started.")
    print(f"Using token: {token}")
    print(f"Room name: {room_name}")
    print(f"server address: {server_address}")

    while True:
        message_text = input()

        if message_text.lower() == "exit":
            print("Exiting chat room.")
            exit_message = {
                "operation": "leave",
                "token": token,
                "room_name": room_name,
                "username": username
            }
            udp_socket.sendto(json.dumps(exit_message).encode('utf-8'), server_address) 
            break

        message = {
            "operation": "message",
            "token": token,
            "room_name": room_name,
            "username": username,
            "message": message_text
        }

        print(f"Sending message: {message}")

        udp_socket.sendto(json.dumps(message).encode('utf-8'), server_address)

def message_receiver(udp_socket):

    udp_socket.settimeout(0.5)

    while True:
     try:
        data, _ = udp_socket.recvfrom(BUFFER_SIZE)
        response = json.loads(data.decode('utf-8'))

        if response["status"] == "success":
            if "message" in response and "sender" in response:
                print(f"{response['sender']}: {response['message']}")
            elif "system_message" in response:
                print(f"[SYSTEM] {response['system_message']}")
        else:
            print(f"[ERROR] {response.get('message', 'Unknown error')}")
     except socket.timeout:
         continue
     except json.JSONDecodeError:
         print("[ERROR] Failed to decode message.")
     except Exception as e:
         print(f"[ERROR] An error occurred: {e}")
         break
        
def main():
    print("Welcome to the Chat Room!")
    print("1. Create a new room")
    print("2. Join an existing room")
    choice = input("Enter your choice (1/2): ")

    username = input("Enter your username: ")
    room_name = input("Enter the room name: ")

    operation = "create_room" if choice == "1" else "join_room"
    response = connect_to_server(TCP_HOST, room_name, username, operation)
    print(f"Full response object: {response}")

    if response["status"] == "success":
        print(f"Connected to server: token: {response['token']}")
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_address = (TCP_HOST, UDP_PORT)

            receiver_thread = threading.Thread(target=message_receiver, args=(udp_socket, ))
            receiver_thread.daemon = True
            receiver_thread.start()

            message_sender(udp_socket, server_address, response['token'], room_name, username)
        except Exception as e:
            print(f"Error in message handling: {e}")
        finally:
            udp_socket.close()
            sys.exit(0)

    else:
        print(f"Failed to connect: {response.get('message', 'Unknown error')}")

if __name__ == "__main__":
    main()

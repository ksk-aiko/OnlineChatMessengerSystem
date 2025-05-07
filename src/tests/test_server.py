"""
Tests for the chat server implementation.
This module contains test cases for the TCP and UDP handlers of the chat server.
It verifies the functionality of room creation, authentication, and handling
various request scenarios.
The tests use unittest.mock to create mock socket objects and simulate
client connections and requests.
Test cases:
- test_create_room_success: Verifies that a room can be created successfully
- test_create_room_already_exists: Verifies rejection when creating a room that already exists
Note: The tests clear the rooms and tokens dictionaries before and after each test
to ensure a clean testing environment.
"""

import unittest
import sys
import os
import json
import socket
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ..server import handle_tcp_connection, udp_handler, rooms, tokens

class TestChatServer(unittest.TestCase):
    
    # Clear the rooms and tokens dictionaries before each test
    def setUp(self):
        rooms.clear()
        tokens.clear()
    
    def tearDown(self):
        rooms.clear()
        tokens.clear()
    
    # Test case for creating a room successfully
    # This test simulates a client creating a room and verifies that the room is created
    def test_create_room_success(self):
        mock_socket = MagicMock()
        client_address = ('192.168.1.10', 54321)

        # Simulate a request to create a room
        request_data = {
            "operation": "create_room",
            "room_name": "test_room",
            "username": "test_user"
        }

        # Mock the socket's recv method to return the request data
        mock_socket.recv.return_value = json.dumps(request_data).encode('utf-8')

        handle_tcp_connection(mock_socket, client_address)

        expected_token = f"test_room-test_user-{client_address[0]}"

        # Check that the room was created successfully
        self.assertIn("test_room", rooms)

        # Check that the room has the expected host and members
        self.assertEqual(rooms["test_room"]["host"], expected_token)

        # Check that the room has the expected members
        self.assertIn(expected_token, rooms["test_room"]["members"])

        # Check that the tokens dictionary has the expected token
        self.assertIn(expected_token, tokens)
        self.assertEqual(tokens[expected_token]["username"], "test_user")
        self.assertEqual(tokens[expected_token]["ip"], client_address[0])

        expected_response = {
            "status": "success",
            "token": expected_token
        }

        mock_socket.send.assert_called_with(json.dumps(expected_response).encode('utf-8'))

    def test_create_room_already_exists(self):
        test_token = "test_room-existing_user-127.0.0.1"
        rooms["test_room"] = {"host": test_token, "members": [test_token]}
        tokens[test_token] = {"username": "existing_user", "ip": "127.0.0.1"}

        mock_socket = MagicMock()
        client_address = ('192.168.1.10', 54321)

        request_data = {
            "operation": "create_room",
            "room_name": "test_room",
            "username": "another_user"
        }

        mock_socket.recv.return_value = json.dumps(request_data).encode('utf-8')

        handle_tcp_connection(mock_socket, client_address)

        expected_response = {
            "status": "error",
            "message": "Room already exists."
        }

        mock_socket.send.assert_called_with(json.dumps(expected_response).encode('utf-8'))

        self.assertEqual(len(rooms["test_room"]["members"]), 1)
        self.assertIn(test_token, rooms["test_room"]["members"])

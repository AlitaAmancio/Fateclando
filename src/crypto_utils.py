import secrets
import struct

import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HEADER_SIZE = 4
NONCE_SIZE = 12
SESSION_KEY_SIZE = 32

def create_session_key():
    return secrets.token_bytes(SESSION_KEY_SIZE)


def wrap_session_key(public_key, session_key):
    return rsa.encrypt(session_key, public_key)


def unwrap_session_key(private_key, encrypted_session_key):
    return rsa.decrypt(encrypted_session_key, private_key)


def encrypt_text(session_key, message):
    aesgcm = AESGCM(session_key)
    nonce = secrets.token_bytes(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, message.encode("utf-8"), None)
    return nonce + ciphertext


def decrypt_text(session_key, payload):
    nonce = payload[:NONCE_SIZE]
    ciphertext = payload[NONCE_SIZE:]
    aesgcm = AESGCM(session_key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")


def send_packet(connection, payload):
    connection.sendall(struct.pack("!I", len(payload)) + payload)


def recv_exact(connection, size):
    data = b""
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def recv_packet(connection):
    header = recv_exact(connection, HEADER_SIZE)
    if header is None:
        return None
    (size,) = struct.unpack("!I", header)
    return recv_exact(connection, size)
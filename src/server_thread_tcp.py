import argparse
import socket
from pathlib import Path
from threading import Event, Thread

import rsa

from .chat_ui import banner, error, peer_message, prompt_text, status, system, your_message
from .crypto_utils import (
    create_session_key,
    decrypt_text,
    encrypt_text,
    recv_packet,
    send_packet,
    unwrap_session_key,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEYS_DIR = PROJECT_ROOT / "keys"


def parse_args():
    parser = argparse.ArgumentParser(description="Start the encrypted TCP server.")
    parser.add_argument("--name", help="Your name used to load pri_<name>.pem.")
    parser.add_argument("--peer", help="The peer name used to load pub_<peer>.pem.")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0).")
    parser.add_argument("--port", type=int, default=5002, help="TCP port (default: 5002).")
    return parser.parse_args()


def load_key_pair(my_name, peer_name):
    my_private_file = KEYS_DIR / f"pri_{my_name.lower()}.pem"
    peer_public_file = KEYS_DIR / f"pub_{peer_name.lower()}.pem"

    try:
        status(f"Loading private key from {my_private_file}...")
        with my_private_file.open("rb") as f:
            my_private_key = rsa.PrivateKey.load_pkcs1(f.read())

        status(f"Loading peer public key from {peer_public_file}...")
        with peer_public_file.open("rb") as f:
            peer_public_key = rsa.PublicKey.load_pkcs1(f.read())
    except FileNotFoundError:
        error(f"Could not find the keys. Check whether {my_private_file} and {peer_public_file} exist.")
        raise SystemExit(1)

    return my_private_key, peer_public_key


def start_send_loop(connection, session_key, stop_event):
    system("Sending thread started.")
    while not stop_event.is_set():
        try:
            message = input(prompt_text("you > "))
            if not message:
                continue
            payload = encrypt_text(session_key, message)
            send_packet(connection, payload)
            your_message(message)
        except (EOFError, KeyboardInterrupt):
            stop_event.set()
            break
        except Exception as exc:
            error(f"Error while sending: {exc}")
            stop_event.set()
            break


def main():
    args = parse_args()
    my_name = (args.name or input("Enter your name: ")).strip()
    peer_name = (args.peer or input("Enter the peer name that will connect: ")).strip()

    my_private_key, peer_public_key = load_key_pair(my_name, peer_name)

    banner("Fateclando", f"Secure chat session as {my_name}")

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind((args.host, args.port))
    tcp.listen(1)

    status(f"{my_name} (server) waiting on {args.host}:{args.port}...")
    system("When the client connects, a shared AES session key will be negotiated automatically.")

    while True:
        tcp_con, client = tcp.accept()
        status(f"{peer_name} connected from {client}")

        try:
            handshake = recv_packet(tcp_con)
            if handshake is None:
                error("Handshake failed: no session key received.")
                tcp_con.close()
                continue

            session_key = unwrap_session_key(my_private_key, handshake)
            status("Secure session established.")
        except Exception as exc:
            error(f"Handshake error: {exc}")
            tcp_con.close()
            continue

        stop_event = Event()
        t_env = Thread(target=start_send_loop, args=(tcp_con, session_key, stop_event), daemon=True)
        t_env.start()

        system("Type your messages and press Enter. Close the terminal or press Ctrl+C to exit.")

        while not stop_event.is_set():
            try:
                encrypted_payload = recv_packet(tcp_con)
                if encrypted_payload is None:
                    system(f"Connection closed by {peer_name}.")
                    stop_event.set()
                    break

                message = decrypt_text(session_key, encrypted_payload)
                peer_message(peer_name, message)
            except Exception as exc:
                error(f"Error while receiving/decrypting: {exc}")
                stop_event.set()
                break

        system(f"Closing connection with {peer_name} ({client})")
        tcp_con.close()


if __name__ == "__main__":
    main()
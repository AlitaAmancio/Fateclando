# Fateclando
Encrypted TCP chat example in Python.

This code uses a direct command-line flow and a hybrid crypto design:

- RSA is used only for key generation and session-key wrapping.
- AES-GCM is used for the chat messages themselves.
- TCP packets include a length prefix so messages are framed correctly.

## Files

- `main.py`: single entry point for generating keys, starting the server, or starting the client.
- `src/generate_keys.py`: generates RSA public/private key pairs into `keys/`.
- `src/server_thread_tcp.py`: starts the server and receives/sends encrypted messages.
- `src/client_thread_tcp.py`: starts the client and receives/sends encrypted messages.
- `src/crypto_utils.py`: shared helpers for packet framing and encryption.
- `src/chat_ui.py`: terminal UI helpers for the chat-style output.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Generate keys for both sides.
4. Start the server and then the client.

## Commands

Generate keys:

```bash
python main.py keys --name alita
python main.py keys --name gloria
```

Run the server:

```bash
python main.py server --name gloria --peer alita --host 0.0.0.0 --port 5002
```

Run the client:

```bash
python main.py client --name alita --peer gloria --server 127.0.0.1 --port 5002
```

Or run `python main.py` and pick a mode from the menu.

## Notes

- Key files are saved inside `keys/`.
- The default port is `5002`.
- RSA keys are generated with 2048 bits by default.

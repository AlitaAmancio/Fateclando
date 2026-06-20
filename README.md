# Fateclando

Encrypted TCP chat example in Python.

This project uses a hybrid crypto design:

- **RSA 2048-bit** is used only once per session, to wrap the session key during the handshake.
- **AES-256-GCM** encrypts every chat message with a random nonce, providing authenticated encryption.
- **TCP packets** include a 4-byte big-endian length prefix so messages are always read completely, never partially.

## Files

- `main.py` — single entry point for generating keys, starting the server, or starting the client.
- `src/generate_keys.py` — generates RSA public/private key pairs into `keys/`.
- `src/server_thread_tcp.py` — starts the server and receives/sends encrypted messages.
- `src/client_thread_tcp.py` — starts the client and receives/sends encrypted messages.
- `src/crypto_utils.py` — shared helpers for packet framing and encryption.
- `src/chat_ui.py` — terminal UI helpers for the chat-style output.

---

## Running on the same machine (local test)

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Generate keys for both users

```bash
python main.py keys --name user1
python main.py keys --name user2
```

This creates four files inside `keys/`: `pri_user1.pem`, `pub_user1.pem`, `pri_user2.pem`, `pub_user2.pem`.

### 3. Start the server (first terminal)

```bash
python main.py server --name user1 --peer user2 --host 0.0.0.0 --port 5002
```

### 4. Start the client (second terminal)

```bash
python main.py client --name user2 --peer user1 --server 127.0.0.1 --port 5002
```

---

## Running on two different machines on the same network

This requires an extra step: each machine needs its own private key **and the other machine's public key**.

### Step 1 — Generate keys on each machine separately

**Machine A (will be the server — user1):**

```bash
python main.py keys --name user1
```

This creates `keys/pri_user1.pem` and `keys/pub_user1.pem` on Machine A.

**Machine B (will be the client — user2):**

```bash
python main.py keys --name user2
```

This creates `keys/pri_user2.pem` and `keys/pub_user2.pem` on Machine B.

### Step 2 — Exchange public keys between machines

Each machine needs the other's **public** key (never share the private key).

| File to copy | From | To |
|---|---|---|
| `keys/pub_user1.pem` | Machine A | Machine B |
| `keys/pub_user2.pem` | Machine B | Machine A |

Copy via USB drive, `scp`, shared folder, or any other method. After this step:

- Machine A must have: `pri_user1.pem` + `pub_user2.pem`
- Machine B must have: `pri_user2.pem` + `pub_user1.pem`

### Step 3 — Open port 5002 on the server machine (Windows Firewall)

Run the following in PowerShell **as Administrator** on Machine A:

```powershell
New-NetFirewallRule -DisplayName "Fateclando" -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow
```

To remove the rule later:

```powershell
Remove-NetFirewallRule -DisplayName "Fateclando"
```

### Step 4 — Find the server's IP address

On Machine A, run:

```powershell
ipconfig
```

Look for the IPv4 address under your active network adapter (Wi-Fi or Ethernet), e.g. `192.168.1.10`.

### Step 5 — Start the server on Machine A

```bash
python main.py server --name user1 --peer user2 --host 0.0.0.0 --port 5002
```

### Step 6 — Start the client on Machine B

Replace `192.168.1.10` with the actual IP of Machine A:

```bash
python main.py client --name user2 --peer user1 --server 192.168.1.10 --port 5002
```

---

## How the encryption works

```
Client (user2)                             Server (user1)
──────────────────────────────────────────────────────────
1. Generates random 256-bit session key
2. Encrypts it with user1's public key (RSA)
3. Sends encrypted session key ──────────►  4. Decrypts with user1's private key (RSA)
                                             Both sides now share the same session key
──────────────────────────────────────────────────────────
5. Encrypt message with AES-256-GCM ──────► 6. Decrypt with AES-256-GCM
   (random 12-byte nonce per message)
◄─────────────────────────────────────────  Same in reverse
```

Each message is framed as:

```
[4 bytes: length] [12 bytes: nonce] [ciphertext + 16-byte GCM tag]
```

---

## Notes

- Key files are saved inside `keys/`. Never commit private keys (`pri_*.pem`) to a public repository.
- The default port is `5002`. Change it with `--port` on both sides if needed.
- RSA keys are generated with 2048 bits by default. Use `--bits 4096` for stronger keys (slower generation).
- If the connection drops, the send thread stays blocked on `input()` until you press Enter — this is expected behavior.
- Run `python main.py` without arguments to pick a mode from the interactive menu.

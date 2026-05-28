import argparse
from pathlib import Path

import rsa


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEYS_DIR = PROJECT_ROOT / "keys"


def parse_args():
    parser = argparse.ArgumentParser(description="Generate an RSA key pair for this chat project.")
    parser.add_argument("--name", help="Owner name used in the PEM file names.")
    parser.add_argument("--bits", type=int, default=2048, help="RSA key size in bits (default: 2048).")
    return parser.parse_args()


def main():
    args = parse_args()
    my_name = (args.name or input("Enter your name (e.g. mary): ")).strip().lower()

    KEYS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating {args.bits}-bit keys for {my_name}...")
    pub, pri = rsa.newkeys(args.bits)

    pub_path = KEYS_DIR / f"pub_{my_name}.pem"
    pri_path = KEYS_DIR / f"pri_{my_name}.pem"

    with pub_path.open("wb") as f:
        f.write(pub.save_pkcs1())
    with pri_path.open("wb") as f:
        f.write(pri.save_pkcs1())

    print(f"Keys generated successfully in {KEYS_DIR}!")


if __name__ == "__main__":
    main()
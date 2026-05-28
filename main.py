import argparse
import runpy
import sys


MODES = {
    "keys": "src.generate_keys",
    "server": "src.server_thread_tcp",
    "client": "src.client_thread_tcp",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Fateclando launcher.")
    parser.add_argument("mode", nargs="?", choices=MODES.keys(), help="What to run: keys, server, or client.")
    args, extra_args = parser.parse_known_args()
    return args, extra_args


def pick_mode_interactively():
    print("Fateclando launcher")
    print("1) Generate keys")
    print("2) Start server")
    print("3) Start client")

    choice = input("Choose an option: ").strip()
    if choice == "1":
        return "keys"
    if choice == "2":
        return "server"
    if choice == "3":
        return "client"
    raise SystemExit("Invalid option.")


def run_mode(mode, extra_args):
    module_name = MODES[mode]
    sys.argv = [module_name, *extra_args]
    runpy.run_module(module_name, run_name="__main__")


def main():
    args, extra_args = parse_args()
    mode = args.mode or pick_mode_interactively()
    run_mode(mode, extra_args)


if __name__ == "__main__":
    main()
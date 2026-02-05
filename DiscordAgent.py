import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[Agent]\t%(levelname)s:\t%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments"""

    parser = argparse.ArgumentParser(prog="Agent.py", description="Archipelago Discord Agent")
    parser.add_argument("--url", required=True, help="The full URL to the archipelago session.")
    parser.add_argument("--password", required=False, help="The password for the server or slot.")
    parser.add_argument("--multidata", required=True, help="The path to the multidata file.")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Just print the values
    logging.info("Agent started with:")
    logging.info(f"\tURL: {args.url}")
    logging.info(f"\tPassword: {args.password}")
    logging.info(f"\tMultidata: {args.multidata}")

if __name__ == "__main__":
    main()

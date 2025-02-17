import argparse
from aqs.info import VERSION


def parse_args():
    # Command-line argument parsing with argparse.
    parser = argparse.ArgumentParser(description=f"AQS {VERSION}")
    parser.add_argument(
        "--loglevel",
        type=str,
        default="DEBUG",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    parser.add_argument("--logfile", type=str, help="Path to a log file (optional)")
    args = parser.parse_args()
    return args

import logging

from brenda_parser import parse


logging.basicConfig(level="DEBUG")


def main():
    with open("tests/test_parsing/data/long_comments.txt") as fh:
        content = fh.read()
    engine, session = parse(content.split("\n"))


if __name__ == "__main__":
    main()

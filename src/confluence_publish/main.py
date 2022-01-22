import logging

from . import cli


def subparser(subparsers, name, cmd):
    p = subparsers.add_parser(name)

    p.add_argument(cli.ConfigArgument)  # this must come first
    p.add_argument(cli.LoggingArguments)
    p.set_defaults(func=cmd)
    return p


def parse_args(args=None):
    parser = cli.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    subparser(subparsers, "hello", hello)

    args = parser.parse_args(args)
    return args.__dict__


def hello():
    logging.debug("A")
    logging.info("B")
    logging.warning("C")

def main():


if __name__ == "__main__":
    main(**parse_args())
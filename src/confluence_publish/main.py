"""publish doctsring from files into a confluence site

Examples:
    publish a page under the main root document

    confluence-publish "A root page title" file.py {file.py, ..}

"""

import logging
import json

from . import cli

def pp(obj):
    return json.dumps(obj, indent=2, sort_keys=True)


def subparser(subparsers, name, cmd):
    p = subparsers.add_parser(name)

    p.add_argument(cli.ConfigArgument)  # this must come first
    p.add_argument(cli.LoggingArguments)
    p.set_defaults(func=cmd)
    return p


def main():
    args = parse_args()
    func = args.func
    delattr(args, "func")
    func(**args.__dict__)


def parse_args(args=None):
    parser = cli.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    publishp = subparser(subparsers, "publish", publish)
    publishp.add_argument("--commit", action="store_true")

    args = parser.parse_args(args)
    return args


def publish(commit):
    logging.debug("A")
    logging.info("B")
    logging.warning("C")


if __name__ == "__main__":
    main()

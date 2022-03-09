#!/usr/bin/env python3

from argparse import ArgumentParser

from scripts.util import Config
from scripts.build import do_build_netboot
from scripts.run import do_run_netboot


def main():
    parser = ArgumentParser()
    subcommands = parser.add_subparsers(dest='subcommand', required=True)
    cmd_build = subcommands.add_parser('build')
    cmd_build.add_argument('config_dir', help='Path to config directory')
    cmd_run = subcommands.add_parser('run')
    cmd_run.add_argument('config_dir', help='Path to config directory')
    args = parser.parse_args()

    if args.subcommand == 'build':
        config = Config(args.config_dir)
        do_build_netboot(config)
    elif args.subcommand == 'run':
        config = Config(args.config_dir)
        do_run_netboot(config)
    else:
        raise Exception(f'Unimplemented command {args.subcommand}')


if __name__ == '__main__':
    main()

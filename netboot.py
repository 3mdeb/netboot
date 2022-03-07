#!/usr/bin/env python3

from argparse import ArgumentParser
from typing import List
import subprocess
import sys
from os import makedirs
from os.path import realpath, join, isdir, exists


def run(args: List[str]):
    subprocess.run(args, stdout=sys.stdout, stderr=sys.stderr)


def validate_site_conf_dir(dir: str):
    if not isdir(dir):
        print(f'{dir} not a directory')
        sys.exit(1)

    user_overrides = join(dir, 'user-overrides.yml')
    if not exists(user_overrides):
        print(f'{user_overrides} does not exist')
        sys.exit(1)


def main():
    parser = ArgumentParser()
    parser.add_argument('--build', required=False)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--http-port', type=int, required=False)
    parser.add_argument('--app-port', type=int, required=False, default='3000')
    parser.add_argument('--tftp-port', type=int, required=False)
    args = parser.parse_args()

    if args.build:
        build_dir = join('build', 'netboot')
        source_dir = join('external', 'netboot.xyz')
        validate_site_conf_dir(args.build)

        makedirs(build_dir, exist_ok=True)
        user_overrides = join(args.build, 'user-overrides.yml')

        run([
            'docker', 'run', '--rm', '-it',
            '-v', f'{realpath(build_dir)}:/var/www/html:rw',
            '-v', f'{realpath(source_dir)}:/ansible:rw',
            '-w', '/ansible',
            'ghcr.io/netbootxyz/builder:latest',
            'ansible-playbook', '-i', 'inventory', 'site.yml'
        ])

    if args.run:
        docker_args = [
            'docker', 'run', '--rm', '-it',
        ]
        if args.app_port:
            docker_args += ['-p', f'3000:{args.app_port}']

        if args.tftp_port:
            docker_args += ['-p', f'69:{args.tftp_port}/udp']

        docker_args += ['d26c70f9998b']
        run(docker_args)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

from argparse import ArgumentParser
import shutil
from typing import List
import subprocess
import sys
from os import makedirs
from os.path import realpath, join, isdir, exists

NETBOOT_SRC_DIR = 'external/netboot.xyz'
NETBOOT_CONTAINER_VERSION = '0.6.6-nbxyz13'

BUILDENV_INIT = 'scripts/buildenv-init.sh'
USER_OVERRIDES_FILE = 'user_overrides.yml'


def run(args: List[str]):
    subprocess.run(args, stdout=sys.stdout, stderr=sys.stderr)


def validate_site_conf_dir(dir: str):
    if not isdir(dir):
        print(f'{dir} not a directory')
        sys.exit(1)

    user_overrides = join(dir, USER_OVERRIDES_FILE)
    if not exists(user_overrides):
        print(f'{user_overrides} does not exist')
        sys.exit(1)


def get_build_dir(site_conf_dir: str):
    # TODO: use site name in build directory name
    build_dir = join('build', 'build-site-name')
    return build_dir


def do_build_netboot(site_conf_dir: str):
    validate_site_conf_dir(site_conf_dir)
    build_dir = get_build_dir(site_conf_dir)

    menus_dir = join(build_dir, 'menus')
    config_dir = join(build_dir, 'config')

    makedirs(build_dir, exist_ok=True)
    makedirs(menus_dir, exist_ok=True)
    makedirs(config_dir, exist_ok=True)

    run([
        'docker', 'run', '--rm', '-it',
        # FIXME: for some reason tmpfs is not accessible to non-root even when
        # setting tmpfs-mode explicitly
        # '-u', f'{geteuid()}:{getegid()}',
        '-v', f'{realpath(BUILDENV_INIT)}:/buildenv-init.sh',
        '-v', f'{realpath(menus_dir)}:/var/www/html:rw',
        '-v', f'{realpath(NETBOOT_SRC_DIR)}:/netboot_src:ro',
        '-v', f'{realpath(site_conf_dir)}:/custom:ro',
        '--mount', 'type=tmpfs,destination=/ansible,tmpfs-mode=1777',
        '-w', '/ansible',
        'ghcr.io/netbootxyz/builder:latest',
        '/buildenv-init.sh', 'ansible-playbook', '-i', 'inventory', 'site.yml'
    ])

    # netboot.xyz webapp needs config/menuversion.txt file initialize itself
    # properly
    shutil.copyfile(join(NETBOOT_SRC_DIR, 'version.txt'),
                    join(config_dir, 'menuversion.txt'))
    shutil.copyfile(join(NETBOOT_SRC_DIR, 'endpoints.yml'), config_dir)


def main():
    parser = ArgumentParser()
    parser.add_argument('--build', required=False)
    parser.add_argument('--run', required=False)
    parser.add_argument('--http-port', type=int, required=False, default='80')
    parser.add_argument('--app-port', type=int, required=False, default='3000')
    parser.add_argument('--tftp-port', type=int, required=False)
    args = parser.parse_args()

    if args.build:
        do_build_netboot(args.build)

    if args.run:
        validate_site_conf_dir(args.run)
        build_dir = get_build_dir(args.run)
        if not exists(build_dir):
            print(f'{build_dir} does not exist, please use --build')

        menus_dir = join(build_dir, 'menus')
        config_dir = join(build_dir, 'config')

        docker_args = [
            'docker', 'run', '--rm', '-it',
        ]
        if args.app_port:
            docker_args += ['-p', f'{args.app_port}:3000']

        if args.tftp_port:
            docker_args += ['-p', f'{args.tftp_port}:69/udp']

        if args.http_port:
            docker_args += ['-p', f'{args.http_port}:80']

        docker_args += [
            # netboot.xyz container tests for presence of /config/menus/remote/menu.ipxe
            # and if it's not present, then downloads menus from internet.
            '-v', f'{realpath(config_dir)}:/config:rw',
            '-v', f'{realpath(menus_dir)}:/config/menus/remote:rw',
            # /config/menus is used only by TFTP server, to make menus visible
            # over HTTP map the same directory to /assets
            # TODO: should make this configurable
            '-v', f'{realpath(menus_dir)}:/assets:rw',

            # '-v', f'{realpath("build/netboot")}:/config/menus/local:ro',
            # Netboot webapp saves cached assets to /assets/assets-mirror so
            # this mount must be writable
            # '-v', f'{realpath("build/assets")}:/assets:rw'
        ]

        docker_args += [
            f'ghcr.io/netbootxyz/netbootxyz:{NETBOOT_CONTAINER_VERSION}']
        run(docker_args)


if __name__ == '__main__':
    main()

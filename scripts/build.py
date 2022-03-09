from os import makedirs
from os.path import join
from typing import List
from .consts import *
from .util import Config
from .docker import spawn_container, Volume
import sys
import subprocess
import shutil


def run(args: List[str]):
    subprocess.run(args, stdout=sys.stdout, stderr=sys.stderr)


def do_build_netboot(config: Config):
    build_dir = config.get_default_build_dir()

    menus_dir = join(build_dir, 'menus')
    config_dir = join(build_dir, 'config')

    makedirs(build_dir, exist_ok=True)
    makedirs(menus_dir, exist_ok=True)
    makedirs(config_dir, exist_ok=True)

    spawn_container(image=NETBOOT_BUILDER, volumes=[
        Volume(BUILDENV_INIT, '/buildenv-init.sh', False),
        Volume(menus_dir, '/var/www/html', True),
        Volume(NETBOOT_SRC_DIR, '/netboot_src', False),
        Volume(config.config_dir, '/custom', False)
    ], workdir='/ansible', tmpfs=[
        '/ansible'
    ], command=[
        '/buildenv-init.sh'
    ])

    # netboot.xyz webapp needs config/menuversion.txt file to initialize itself
    # properly
    shutil.copyfile(join(NETBOOT_SRC_DIR, 'version.txt'),
                    join(config_dir, 'menuversion.txt'))
    shutil.copyfile(join(NETBOOT_SRC_DIR, 'endpoints.yml'),
                    join(config_dir, 'endpoints.yml'))

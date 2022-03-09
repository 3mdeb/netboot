from os.path import exists, join
from .util import Config
from .docker import spawn_container, Volume, PortMapping
from .consts import NETBOOT_CONTAINER_VERSION, NETBOOT_INIT


def do_run_netboot(config: Config):
    build_dir = config.get_default_build_dir()
    if not exists(build_dir):
        raise RuntimeError(
            f'{build_dir} does not exist, please build netboot.xyz first')

    menus_dir = join(build_dir, 'menus')
    config_dir = join(build_dir, 'config')

    ports = []
    if config.http_port:
        ports.append(PortMapping(80, config.http_port, False))
    if config.app_port:
        ports.append(PortMapping(3000, config.app_port, False))
    if config.tftp_port:
        ports.append(PortMapping(69, config.tftp_port, True))

    spawn_container(
        image=f'ghcr.io/netbootxyz/netbootxyz:{NETBOOT_CONTAINER_VERSION}', volumes=[
            Volume(config_dir, '/config', True),
            Volume(menus_dir, '/config/menus', True),
            # /config/menus is used only by TFTP server, to make menus visible
            # over HTTP map the same directory to /assets
            # TODO: should make this configurable
            Volume(menus_dir, '/assets', True),
            Volume(NETBOOT_INIT, '/netboot-init.sh', False)
        ],
        ports=ports,
        command=['/netboot-init.sh'])

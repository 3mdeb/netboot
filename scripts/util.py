from typing import Any
from os.path import join, exists
from .consts import SERVER_CONFIG_FILE, USER_OVERRIDES_FILE, BUILD_ROOT_DIR
import yaml
import hashlib


class Config:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir

        main_config = None
        server_config = None

        try:
            main_config = yaml_load(join(config_dir, USER_OVERRIDES_FILE))
        except FileNotFoundError:
            raise FileNotFoundError(
                f'{USER_OVERRIDES_FILE} does not exist in {config_dir}')

        try:
            server_config = yaml_load(join(config_dir, SERVER_CONFIG_FILE))
        except FileNotFoundError:
            server_config = {}

        try:
            self.site_name = main_config['site_name']
        except KeyError:
            raise KeyError('Please set `site_name` in user_overrides.yml')

        self.http_port = int_val(server_config.get('http'))
        self.tftp_port = int_val(server_config.get('tftp'))
        self.app_port = int_val(server_config.get('app'))

    def get_default_build_dir(self):
        # Put each site in a separate build directory
        hash = hashlib.md5(self.site_name.encode('utf-8')).hexdigest()
        return join(BUILD_ROOT_DIR, 'build-{}'.format(hash))


def int_val(x):
    if x:
        return int(x)
    else:
        return None


def yaml_load(path: str) -> Any:
    file = open(path, 'rb')
    data = yaml.safe_load(file)
    file.close()

    return data

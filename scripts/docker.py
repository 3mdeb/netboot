from os.path import exists, realpath
import subprocess
import sys


class Volume:
    def __init__(self, source: str, destination: str, writable: bool):
        if not exists(source):
            raise RuntimeError(f'Volume {source} does not exist')

        self.source = source
        self.destination = destination
        self.writable = writable


class PortMapping:
    def __init__(self, internal: int, external: int, is_udp: bool):
        self.internal = internal
        self.external = external
        self.is_udp = is_udp


# def spawn_container(*, image: str, volumes: List[Volume], ports: List[PortMapping], workdir: Optional[str], command: List[str], tmpfs: List[str]):
def spawn_container(**kwargs):
    volumes = kwargs['volumes'] if 'volumes' in kwargs else []
    ports = kwargs['ports'] if 'ports' in kwargs else []
    tmpfs = kwargs['tmpfs'] if 'tmpfs' in kwargs else []

    docker_command = [
        'docker', 'run', '--rm', '-it',
    ]

    for volume in volumes:
        docker_command.extend([
            '-v',
            '{}:{}:{}'.format(
                realpath(volume.source), volume.destination, 'rw' if volume.writable else 'ro')
        ])

    for port in ports:
        docker_command.extend([
            '-p',
            '{}:{}{}'.format(port.external, port.internal,
                             '/udp' if port.is_udp else '')
        ])

    if 'workdir' in kwargs:
        docker_command.extend([
            '-w', kwargs['workdir']
        ])

    for tmp in tmpfs:
        docker_command.extend([
            '--mount', f'type=tmpfs,destination={tmp},tmpfs-mode=1777'
        ])

    docker_command.append(kwargs['image'])
    if kwargs['command']:
        docker_command.extend(kwargs['command'])

    result = subprocess.run(
        docker_command, stdout=sys.stdout, stderr=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(
            f'Docker exited with non-zero code: {result.returncode}')

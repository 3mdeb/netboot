Netboot
-------

This repository provide Debian netinst modification required for booting PC
Engines apuX platforms over PXE.

## Usage

```
git clone https://github.com/3mdeb/netboot.git
```

Get recent netinst package:

```
mkdir tftpboot && cd tftpboot
wget http://ftp.nl.debian.org/debian/dists/stretch/main/installer-amd64/current/images/netboot/netboot.tar.gz
tar xvf netboot.tar.gz
```

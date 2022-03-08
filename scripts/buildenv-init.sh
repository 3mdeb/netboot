#!/usr/bin/env bash

set -euo pipefail

# Copy netboot.xyz and override with selected files from site config
cp -r /netboot_src/* .
cp /custom/user_overrides.yml .

$@

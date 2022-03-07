FROM ghcr.io/netbootxyz/builder:latest as builder

COPY . /ansible
RUN \
    cd /ansible && \
    ansible-playbook -i inventory site.yml

FROM linuxserver/netbootxyz

COPY --from=builder /var/www/html /assets

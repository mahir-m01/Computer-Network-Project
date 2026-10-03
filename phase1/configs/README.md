# Phase 1 configuration deployment

## DNS1

Install dnsmasq and copy `dnsmasq-cn-dns1.conf` into the active dnsmasq configuration on container 201.

Validate and restart:

```bash
dnsmasq --test
systemctl restart dnsmasq
systemctl is-active dnsmasq
```

Test from containers 202, 203 and 204:

```bash
cat /etc/resolv.conf
dig app.cnproject.test
```

The resolver should be `10.200.99.10`, and the A record should return `10.200.99.20`.

## Edge1

Install nginx and place `nginx-cn-edge1.conf` at:

```text
/etc/nginx/sites-available/cn-edge
```

Enable the site using the normal nginx `sites-enabled` link. Place the certificate and private key at the paths referenced by the configuration. Do not copy the private key into this repository.

Validate and reload:

```bash
nginx -t
systemctl reload nginx
systemctl is-active nginx
```

Expected result: the syntax test succeeds and nginx is active.

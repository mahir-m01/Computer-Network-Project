# TLS setup and trust

## Certificate identity

- Common name: `app.cnproject.test`
- Subject alternative names: `app.cnproject.test`, `api.cnproject.test`
- Valid from: 28 September 2026
- Valid until: 27 March 2027
- SHA256 fingerprint: `33:53:15:A5:D6:D7:A8:88:BE:02:F1:18:A5:F7:00:ED:70:AB:2D:E5:1E:A9:53:67:6C:5F:E5:EE:79:8D:01:B1`

The public certificate is stored at `phase1/tls/cnproject-public.crt`. The private key stays on Edge1 at `/etc/nginx/cn-tls/edge.key` and is excluded from Git.

## nginx paths

```nginx
ssl_certificate /etc/nginx/cn-tls/edge.crt;
ssl_certificate_key /etc/nginx/cn-tls/edge.key;
```

## Mac trust

The public certificate was imported into macOS Keychain Access and marked trusted. This lets curl and the browser validate the local certificate without bypassing security.

Verify from the Mac:

```bash
curl -v https://app.cnproject.test
```

Evidence to show:

- The hostname matches the certificate.
- curl prints `SSL certificate verify ok`.
- The response is HTTP 200.
- The command does not use `-k`.

## TLS termination

The Mac creates a TLS connection to nginx on TCP 443. nginx decrypts the request and creates a separate HTTP/1.1 connection to a backend on port 3001 or 3002.

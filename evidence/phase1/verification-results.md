# Phase 1 Verification Results

These results were collected from the running platform on 30 September 2026. Configuration files, packet captures and screenshots are preserved alongside the observed command output.

## Configuration provenance

| Component | Repository source |
| --- | --- |
| DNS1 | [dnsmasq-cn-dns1.conf](../../phase1/configs/dnsmasq-cn-dns1.conf) |
| Backend application | [app.py](../../phase1/backend/app.py) |
| Backend A identity | [backend-a.env.example](../../phase1/backend/backend-a.env.example) |
| Backend B identity | [backend-b.env.example](../../phase1/backend/backend-b.env.example) |
| Edge1 | [nginx-cn-edge1.conf](../../phase1/configs/nginx-cn-edge1.conf) |

## DNS lookup

Command:

```bash
dig @10.200.99.10 app.cnproject.test
```

Observed result:

```text
status: NOERROR
QUESTION: app.cnproject.test. IN A
ANSWER: app.cnproject.test. 30 IN A 10.200.99.20
SERVER: 10.200.99.10#53
```

DNS1 returned Edge1's address with the configured 30-second TTL.

## Trusted HTTPS response

Command:

```bash
curl -i https://app.cnproject.test/api/status
```

Observed result:

```http
HTTP/2 200
server: nginx
content-type: application/json
x-backend: B
cache-control: no-store

{"backend": "B", "status": "ok"}
```

The request completed through nginx over trusted HTTPS. Certificate validation remained enabled.

## HTTP protocol versions

Commands:

```bash
curl --http1.1 -sS -o /dev/null -w 'HTTP version: %{http_version} status: %{http_code}\n' https://app.cnproject.test/api/status
curl --http2 -sS -o /dev/null -w 'HTTP version: %{http_version} status: %{http_code}\n' https://app.cnproject.test/api/status
```

Observed result:

```text
HTTP version: 1.1 status: 200
HTTP version: 2 status: 200
```

## Backend round robin

Repeated requests to the status endpoint produced responses from both upstream servers:

```text
HTTP/2 200
X-Backend: A

HTTP/2 200
X-Backend: B
```

This confirms that both configured backend addresses participated in nginx's upstream rotation.

## Cache validation

Commands:

```bash
curl -I https://app.cnproject.test/api/cache
curl -i -H 'If-None-Match: "cn-cache-v1"' https://app.cnproject.test/api/cache
```

Observed initial response:

```http
HTTP/2 200
server: nginx
x-backend: A
cache-control: public, max-age=60
etag: "cn-cache-v1"
```

Observed conditional response:

```http
HTTP/2 304
server: nginx
x-backend: B
etag: "cn-cache-v1"
```

The client may reuse the response for 60 seconds. A matching ETag then allows the server to return 304 without sending the JSON representation again.

## Packet capture summary

The [focused capture](phase1-dns-tcp-tls.pcapng) contains:

- the DNS query and response for `app.cnproject.test`;
- the TCP SYN, SYN-ACK and ACK on port 443;
- the TLS ClientHello with SNI;
- the TLS ServerHello and certificate;
- encrypted application data.

The [packet evidence guide](README.md) maps these events to individual packet numbers and screenshots.

## Backend failure test

The controlled test stopped the application service on Backend A while leaving DNS1, Edge1 and Backend B operational.

```text
systemctl stop cn-backend   -> Backend A stopped
systemctl is-active cn-backend   -> inactive
Repeated HTTPS requests   -> HTTP 200 with X-Backend: B only
systemctl start cn-backend   -> Backend A started
systemctl is-active cn-backend   -> active
Repeated HTTPS requests   -> X-Backend: A and X-Backend: B returned
```

The failure affected the application service on Backend A. nginx continued serving requests through Backend B, and the restored service returned to the upstream rotation.

## Demonstration recording

The complete Phase 1 demonstration is available in the [Google Drive recording folder](https://drive.google.com/drive/folders/1SVjw0JjsixaM0_xOpkwaDQ1-8z1HvW2b?usp=drive_link).

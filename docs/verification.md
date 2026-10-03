# Verification Guide

These checks reproduce the Phase 1 results. Each command identifies the system on which it should run.

## 1. Private DNS

Run from a client container such as CT 202, CT 203 or CT 204:

```bash
dig app.cnproject.test
```

Expected evidence:

- status `NOERROR`;
- answer `10.200.99.20`;
- resolver `10.200.99.10#53`;
- TTL `30`.

Confirm that public DNS does not contain the private name:

```bash
dig @8.8.8.8 app.cnproject.test
```

Expected result: `NXDOMAIN` or timeout.

## 2. Direct backend responses

Run from CT 202, `cn-edge1`:

```bash
curl -i http://10.200.99.31:3001/api/status
curl -i http://10.200.99.32:3002/api/status
```

Expected result: both requests return HTTP 200. The first response contains `X-Backend: A`; the second contains `X-Backend: B`.

## 3. Trusted HTTPS

Run from the Mac:

```bash
curl -v https://app.cnproject.test
```

Expected evidence:

- the name resolves to `10.200.99.20`;
- the certificate matches `app.cnproject.test`;
- curl reports `SSL certificate verify ok`;
- the response status is HTTP 200;
- the command does not use `-k`.

## 4. HTTP protocol support

Run from the Mac:

```bash
curl --http1.1 -sS -o /dev/null -w 'HTTP version: %{http_version} status: %{http_code}\n' https://app.cnproject.test/api/status
curl --http2 -sS -o /dev/null -w 'HTTP version: %{http_version} status: %{http_code}\n' https://app.cnproject.test/api/status
```

Expected result:

```text
HTTP version: 1.1 status: 200
HTTP version: 2 status: 200
```

## 5. Round-robin distribution

Run from the Mac:

```bash
for i in {1..6}; do echo "Request $i"; curl -sS -i https://app.cnproject.test/api/status; echo; done
```

Expected result: the six successful responses include both `X-Backend: A` and `X-Backend: B`.

## 6. HTTP caching

Run from the Mac:

```bash
curl -I https://app.cnproject.test/api/cache
curl -i -H 'If-None-Match: "cn-cache-v1"' https://app.cnproject.test/api/cache
```

Expected result:

- the first response is HTTP 200 with `Cache-Control: public, max-age=60` and ETag `"cn-cache-v1"`;
- the conditional request is HTTP 304 with no response body.

## 7. Backend failure test

Establish the normal state by making repeated requests from the Mac and confirming that both backends appear.

Stop Backend A on CT 203:

```bash
systemctl stop cn-backend
systemctl is-active cn-backend
```

The service status should be `inactive`. Repeat the HTTPS status request from the Mac:

```bash
for i in {1..6}; do curl -sS -i https://app.cnproject.test/api/status; echo; done
```

All successful responses should show `X-Backend: B`.

Restore Backend A on CT 203:

```bash
systemctl start cn-backend
systemctl is-active cn-backend
```

The service status should return to `active`. After the nginx failure timeout, repeated requests should include both A and B again.

## 8. Wireshark analysis

Use the focused capture in `evidence/phase1/phase1-dns-tcp-tls.pcapng`.

### DNS

```text
dns && ip.addr == 10.200.99.10
```

This filter shows the query for `app.cnproject.test` and the answer `10.200.99.20` with TTL 30.

### TCP handshake

```text
tcp.stream == 0
```

Packets 7, 8 and 9 show SYN, SYN-ACK and ACK between client port 55130 and Edge1 port 443.

### TLS handshake and encrypted data

```text
tcp.stream == 0 && tls
```

This filter shows ClientHello, ServerHello, Certificate, key exchange messages and encrypted Application Data. The HTTP headers and body are not readable because TLS encrypts them.

## Recorded results

The corresponding observed outputs are preserved in [verification-results.md](../evidence/phase1/verification-results.md). Packet-level evidence is indexed in the [Phase 1 evidence guide](../evidence/phase1/README.md).

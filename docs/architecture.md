# Architecture and Protocol Flow

## Network design

The platform runs on a Proxmox VE host. OPNsense runs as VM 9000 and provides the VLAN 99 gateway at `10.200.99.1`, routing and firewall separation from other networks. Each service has its own LXC container and IPv4 address on VLAN 99 (`10.200.99.0/24`).

Proxmox uses a VLAN-aware Linux bridge for container connectivity. Traffic between containers in the same VLAN is switched locally by Proxmox. Traffic entering or leaving VLAN 99 is routed by OPNsense.

## Service inventory

### Phase 1

| Container | Address | Role | Exposed service |
| --- | --- | --- | --- |
| 201 `cn-dns1` | `10.200.99.10` | Primary private DNS | UDP/TCP 53 |
| 202 `cn-edge1` | `10.200.99.20` | HTTPS edge and load balancer | TCP 443 |
| 203 `cn-app-a` | `10.200.99.31` | Python Backend A | TCP 3001 |
| 204 `cn-app-b` | `10.200.99.32` | Python Backend B | TCP 3002 |

### Phase 2 extension

| Container | Address | Role |
| --- | --- | --- |
| 205 `cn-dns2` | `10.200.99.11` | Backup private DNS |
| 206 `cn-edge2` | `10.200.99.21` | Standby nginx edge |

The Phase 2 services are shown to document the intended extension. The evidence in this repository evaluates the Phase 1 path through DNS1 and Edge1.

## Request flow

1. The client queries DNS1 for `app.cnproject.test` over UDP port 53.
2. DNS1 returns Edge1 at `10.200.99.20` with a 30-second TTL.
3. The client opens a TCP connection to Edge1 port 443 using SYN, SYN-ACK and ACK.
4. The client and Edge1 negotiate TLS. Edge1 presents the certificate for `app.cnproject.test`.
5. The client sends an HTTP/1.1 or HTTP/2 request through the encrypted connection.
6. nginx selects Backend A or Backend B from the `cn_backends` upstream group.
7. nginx creates a separate HTTP/1.1 connection to backend port 3001 or 3002.
8. The backend returns JSON to nginx, which sends the HTTPS response to the client.

## Protocol map

| Protocol | Function in the project |
| --- | --- |
| DNS over UDP 53 | Resolves the private application name |
| IPv4 | Routes traffic between the client and VLAN 99 |
| TCP | Establishes a reliable, ordered connection |
| TLS | Authenticates Edge1 and encrypts application data |
| HTTP/1.1 and HTTP/2 | Carries client API requests to nginx |
| HTTP/1.1 | Carries nginx proxy requests to the Python backends |

## Failure behavior

If Backend A stops, nginx marks the failed upstream unavailable and retries Backend B. The public endpoint remains available because DNS1, the TCP connection, TLS termination and nginx are still operating. Restarting Backend A returns it to the upstream rotation after the configured failure timeout.

## Trust boundary

The Mac trusts the local certificate through macOS Keychain Access. nginx terminates TLS at Edge1. Connections from nginx to the Python backends remain inside VLAN 99 and use HTTP/1.1.

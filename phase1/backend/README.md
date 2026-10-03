# Backend deployment

The same Python program and systemd unit run on containers 203 and 204. Only the environment file changes.

## Files on each container

```text
/opt/cn-backend/app.py
/etc/cn-backend.env
/etc/systemd/system/cn-backend.service
```

## Install Backend A on container 203

Copy `app.py` to `/opt/cn-backend/app.py`, copy the service unit, and create `/etc/cn-backend.env` with:

```ini
BACKEND_ID=A
PORT=3001
```

## Install Backend B on container 204

Use the same program and service unit. Create `/etc/cn-backend.env` with:

```ini
BACKEND_ID=B
PORT=3002
```

## Start the service

Run on each backend container:

```bash
systemctl daemon-reload
systemctl enable --now cn-backend
systemctl is-active cn-backend
```

Expected result: `active`.

## Verify from Edge1

Run on container 202:

```bash
curl -i http://10.200.99.31:3001/api/status
curl -i http://10.200.99.32:3002/api/status
```

Expected result: HTTP 200 with `X-Backend: A` and `X-Backend: B` respectively.

# Pi-hole Blocking Status Proxy

A lightweight Flask app that securely checks whether Pi-hole's DNS blocking is enabled, and returns a clean JSON response. Designed to be monitored by tools like [Uptime Kuma](https://github.com/louislam/uptime-kuma).

## 🔧 Features

- Logs into Pi-hole via its `/api/auth` endpoint using your password
- Checks the blocking status (`/api/dns/blocking`)
- Cleanly logs out after the check
- Returns a simple JSON response like:
  ```json
  { "enabled": true }
  ```

## 📦 Usage (Docker Compose)

```yaml
version: '3.8'

services:
  pihole-status-proxy:
    build: .
    container_name: pihole-status-proxy
    environment:
      - PIHOLE_URL=https://your-pihole-url
      - PIHOLE_PASSWORD=your-pihole-password
    ports:
      - "5000:5000"
    restart: unless-stopped
```

You can also use an `.env` file instead of hardcoding environment variables.

## 🧪 Example Curl Test

```bash
curl http://localhost:5000/
```

Expected output:

```json
{ "enabled": true }
```

## 🛡 Security Notes

- Don't expose this app to the public internet.
- No Pi-hole credentials are stored or cached.
- The app authenticates, fetches status, and logs out on every request.

## ✅ Uptime Kuma Setup

- Monitor Type: `HTTP(s) - Keyword`
- URL: `http://<docker-host>:5000/`
- Keyword: `enabled`

---

## License

MIT

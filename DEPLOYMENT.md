# Cloud VPS deployment

1. Provision an Ubuntu LTS VPS. Use a non-root deployment user and SSH keys.
2. Install Docker Engine and the Docker Compose plugin from official Docker documentation.
3. Clone the private GitHub repository.
4. Create `.env` on the VPS; do not copy secrets into GitHub.
5. Configure a domain and HTTPS reverse proxy (Caddy or another maintained proxy).
6. Expose only HTTPS publicly. Keep PostgreSQL private; keep Node-RED editor behind authentication/VPN.
7. Run `docker compose up -d --build`.
8. Configure provider webhooks to your HTTPS endpoints.
9. Configure automated encrypted PostgreSQL backups and test restore.
10. Add monitoring, log rotation, firewall rules, OS updates and alerting.

The Compose file binds service ports to localhost. Put a reverse proxy in front and route the public domain to the frontend/API. Do not directly expose the database.

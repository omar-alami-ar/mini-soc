# Traefik Role

This Ansible role deploys Traefik as a reverse proxy with automatic HTTPS certificate management using Let's Encrypt.

## Role Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `traefik_domain` | Domain for your services | `soc.local` |
| `traefik_dashboard_subdomain` | Subdomain for Traefik dashboard | `traefik` |
| `wazuh_dashboard_subdomain` | Subdomain for Wazuh dashboard | `wazuh` |
| `letsencrypt_email` | Email for Let's Encrypt | `admin@domain` |
| `letsencrypt_staging` | Use staging environment | `true` |
| `traefik_dashboard_auth` | Basic auth for dashboard | `admin:admin` |

## Prerequisites

- Docker Swarm initialized
- Domain pointing to server
- Ports 80/443 open

## Usage

Include in your playbook:

```yaml
roles:
  - traefik
  - your-other-roles
```

## Security

- TLS 1.2/1.3 only
- Strong cipher suites
- Security headers
- Basic auth protection
- Network encryption
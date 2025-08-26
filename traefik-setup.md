# Traefik HTTPS Setup for SOC Infrastructure

This setup integrates Traefik as a reverse proxy with automatic HTTPS certificate management for your SOC infrastructure.

## Features

- **Automatic HTTPS**: Let's Encrypt integration with automatic certificate renewal
- **Security Headers**: Comprehensive security headers and TLS configuration
- **Dashboard Protection**: Basic authentication for Traefik dashboard
- **Docker Swarm Integration**: Native support for Docker Swarm mode
- **Service Discovery**: Automatic service discovery with labels

## Prerequisites

1. Domain name pointing to your server
2. Ports 80 and 443 accessible from the internet
3. Docker Swarm initialized
4. Ansible vault configured

## Configuration

### 1. Configure Domain and Email

Edit the vault file with your domain and email:

```bash
ansible-vault edit ansible/playbooks/roles/traefik/vars/vault.yml
```

Add the following variables:

```yaml
vault_traefik_domain: "your-domain.com"
vault_letsencrypt_email: "admin@your-domain.com"
vault_letsencrypt_staging: false  # Set to true for testing
vault_traefik_dashboard_auth: "admin:$2a$10$..."  # Generate with htpasswd
```

### 2. Generate Dashboard Password

Generate a secure password hash for the Traefik dashboard:

```bash
echo $(htpasswd -nb admin your_password) | sed -e s/\\$/\\$\\$/g
```

### 3. DNS Configuration

Ensure your domain has the following DNS records:

- `traefik.your-domain.com` → Your server IP
- `wazuh.your-domain.com` → Your server IP

## Deployment

The Traefik role is automatically included in the deployment:

```bash
cd ansible
ansible-playbook -i inventory.ini playbooks/deploy-swarm.yml --vault-password-file /path/to/vault_pass
```

## Access URLs

After deployment, your services will be available at:

- **Wazuh Dashboard**: https://wazuh.your-domain.com
- **Traefik Dashboard**: https://traefik.your-domain.com

## Security Features

### TLS Configuration
- TLS 1.2 and 1.3 support
- Strong cipher suites
- Perfect Forward Secrecy

### Security Headers
- HSTS with preload
- X-Frame-Options: SAMEORIGIN
- Content-Type nosniff
- XSS protection
- Referrer policy

### Network Isolation
- Encrypted overlay networks
- Service-to-service communication isolation
- External network only for web services

## Monitoring

Traefik provides built-in metrics for Prometheus:
- Access logs
- Service health monitoring
- Certificate expiration tracking

## Troubleshooting

### Certificate Issues

Check certificate status:
```bash
docker exec $(docker ps -q -f name=traefik) traefik healthcheck
```

### Service Discovery

Verify service labels:
```bash
docker service inspect wazuh_wazuh-dashboard --format='{{json .Spec.Labels}}'
```

### Logs

Check Traefik logs:
```bash
docker service logs traefik_traefik -f
```

## Maintenance

### Certificate Renewal
Certificates are automatically renewed. No manual intervention required.

### Dashboard Access
Access the Traefik dashboard at https://traefik.your-domain.com using the configured credentials.

### Updating Configuration
Modify templates and re-run the playbook to update configurations.
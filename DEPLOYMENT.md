# Deployment Guide

This guide covers deploying the Family Meal Planner application on a Proxmox LXC container using Docker.

## Prerequisites

- Proxmox VE 7.x or later
- LXC container with:
  - Ubuntu 22.04 LTS or Debian 12
  - At least 1GB RAM (2GB recommended)
  - At least 10GB disk space
  - Docker and Docker Compose installed

## Quick Start

### 1. Set Up LXC Container

Create a new LXC container in Proxmox:

```bash
# Example using Proxmox CLI
pct create 100 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname mealplanner \
  --memory 2048 \
  --cores 2 \
  --rootfs local-lvm:10 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1

pct start 100
pct enter 100
```

### 2. Install Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

### 3. Clone and Configure Application

```bash
# Clone repository (or copy files)
cd /opt
git clone https://github.com/yourusername/MealPlanning.git mealplanner
cd mealplanner

# Create environment file
cp .env.example .env

# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Edit .env with your settings
nano .env
```

### 4. Configure Environment Variables

Edit `.env` with the following required settings:

```bash
# Required - generate a unique secret key
SECRET_KEY=your-generated-secret-key

# Database credentials (use strong password)
POSTGRES_DB=mealplanner
POSTGRES_USER=mealplanner
POSTGRES_PASSWORD=your-secure-database-password

# Production settings
DEBUG=false
ALLOWED_HOSTS=meals.yourdomain.com,192.168.1.100
CSRF_TRUSTED_ORIGINS=https://meals.yourdomain.com,http://192.168.1.100

# Optional: Change default port
HTTP_PORT=80
```

### 5. Build and Start Services

```bash
# Build and start in production mode
docker compose -f docker-compose.prod.yml up -d --build

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Create initial admin user
docker compose -f docker-compose.prod.yml exec web \
  uv run python manage.py createsuperuser
```

### 6. Verify Deployment

- Open http://your-server-ip in a browser
- Log in with the admin credentials you created
- Test adding a recipe and planning a meal

## PWA Installation on iOS

To install the app on your iPhone/iPad:

1. Open Safari and navigate to your app URL
2. Tap the Share button (square with arrow)
3. Scroll down and tap "Add to Home Screen"
4. Name it "Meal Planner" and tap "Add"

The app will now appear on your home screen and function like a native app.

## SSL/HTTPS Setup

For production with HTTPS, you have several options:

### Option A: Cloudflare Tunnel (Recommended)

Cloudflare Tunnel provides free SSL and doesn't require port forwarding:

```bash
# Install cloudflared
curl -L --output cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared.deb

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create mealplanner

# Configure tunnel (create ~/.cloudflared/config.yml)
cat > ~/.cloudflared/config.yml << EOF
tunnel: your-tunnel-id
credentials-file: /root/.cloudflared/your-tunnel-id.json
ingress:
  - hostname: meals.yourdomain.com
    service: http://localhost:80
  - service: http_status:404
EOF

# Run tunnel as service
cloudflared service install
systemctl start cloudflared
```

### Option B: Traefik Reverse Proxy

Add Traefik to docker-compose.prod.yml for automatic SSL with Let's Encrypt:

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - letsencrypt:/letsencrypt

  nginx:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.mealplanner.rule=Host(`meals.yourdomain.com`)"
      - "traefik.http.routers.mealplanner.entrypoints=websecure"
      - "traefik.http.routers.mealplanner.tls.certresolver=letsencrypt"
```

## Maintenance

### Backup Database

```bash
# Create backup
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U mealplanner mealplanner > backups/backup-$(date +%Y%m%d).sql

# Or use the backup volume mount
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U mealplanner mealplanner > /backups/backup-$(date +%Y%m%d).sql
```

### Restore Database

```bash
# Stop web service first
docker compose -f docker-compose.prod.yml stop web

# Restore backup
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U mealplanner mealplanner < backups/backup-20240101.sql

# Restart web service
docker compose -f docker-compose.prod.yml start web
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build

# Run migrations if needed
docker compose -f docker-compose.prod.yml exec web \
  uv run python manage.py migrate
```

### View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f db
```

### Container Management

```bash
# Stop all services
docker compose -f docker-compose.prod.yml down

# Stop and remove volumes (WARNING: deletes data!)
docker compose -f docker-compose.prod.yml down -v

# Restart specific service
docker compose -f docker-compose.prod.yml restart web

# Enter container shell
docker compose -f docker-compose.prod.yml exec web bash
```

## Troubleshooting

### Service Won't Start

Check logs for errors:
```bash
docker compose -f docker-compose.prod.yml logs web
```

Common issues:
- Missing or invalid SECRET_KEY
- Database connection failed (check POSTGRES_PASSWORD)
- Port 80 already in use (change HTTP_PORT)

### Database Connection Issues

```bash
# Check database health
docker compose -f docker-compose.prod.yml exec db pg_isready

# Check database logs
docker compose -f docker-compose.prod.yml logs db
```

### Static Files Not Loading

```bash
# Rebuild static files
docker compose -f docker-compose.prod.yml exec web \
  uv run python manage.py collectstatic --noinput

# Check nginx logs
docker compose -f docker-compose.prod.yml logs nginx
```

### PWA Not Working

- Ensure HTTPS is configured (PWA requires secure context)
- Check browser console for service worker errors
- Verify manifest.json is accessible at /static/manifest.json

## Security Recommendations

1. **Use strong passwords** for database and admin accounts
2. **Enable HTTPS** using Cloudflare Tunnel or Traefik
3. **Regular backups** - schedule daily database backups
4. **Keep updated** - regularly update Docker images and application code
5. **Firewall** - only expose necessary ports (80/443)
6. **Monitor logs** - check for unusual activity

## Resource Usage

Typical resource usage:
- **RAM**: ~500MB idle, ~1GB under load
- **CPU**: Minimal (< 5% idle)
- **Disk**: ~2GB for containers + data growth

For small households, a 1GB RAM container is sufficient.

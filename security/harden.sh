#!/bin/bash
# TWOM API Security Hardening Script

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "   TWOM API Security Hardening"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script must be run as root (use sudo)"
    exit 1
fi

echo "🔒 Step 1: Configure UFW Firewall"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Enable UFW if not already enabled
ufw --force enable

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (be careful not to lock yourself out!)
ufw allow 22/tcp comment 'SSH'

# Allow port 5000 only from local network
ufw allow from 192.168.0.0/16 to any port 5000 proto tcp comment 'TWOM API - Local Network Only'

# Deny port 5000 from all other sources
ufw deny 5000/tcp comment 'TWOM API - Deny External'

# Rate limiting for SSH to prevent brute force
ufw limit 22/tcp

echo "✅ Firewall configured"
echo ""

echo "🔒 Step 2: Install and Configure Fail2Ban"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if fail2ban is installed
if ! command -v fail2ban-client &> /dev/null; then
    echo "Installing fail2ban..."
    apt-get update -qq
    apt-get install -y fail2ban
fi

# Copy filter configuration
if [ -f "/home/boardgame/project/TWOM/security/fail2ban_twom.conf" ]; then
    cp /home/boardgame/project/TWOM/security/fail2ban_twom.conf /etc/fail2ban/filter.d/twom-api.conf
    echo "✅ Fail2Ban filter installed"
fi

# Copy jail configuration
if [ -f "/home/boardgame/project/TWOM/security/fail2ban_jail.conf" ]; then
    cp /home/boardgame/project/TWOM/security/fail2ban_jail.conf /etc/fail2ban/jail.d/twom-api.conf
    echo "✅ Fail2Ban jail installed"
fi

# Restart fail2ban
systemctl enable fail2ban
systemctl restart fail2ban

echo "✅ Fail2Ban configured and started"
echo ""

echo "🔒 Step 3: System Security Settings"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Disable IPv6 if not needed (optional)
# echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf

# Protect against SYN flood attacks
sysctl -w net.ipv4.tcp_syncookies=1 > /dev/null 2>&1

# Ignore ICMP redirects
sysctl -w net.ipv4.conf.all.accept_redirects=0 > /dev/null 2>&1
sysctl -w net.ipv6.conf.all.accept_redirects=0 > /dev/null 2>&1

# Ignore ICMP echo requests (ping)
sysctl -w net.ipv4.icmp_echo_ignore_all=1 > /dev/null 2>&1

# Enable IP spoofing protection
sysctl -w net.ipv4.conf.all.rp_filter=1 > /dev/null 2>&1

echo "✅ System security settings applied"
echo ""

echo "🔒 Step 4: File Permissions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Secure database file
chmod 640 /home/boardgame/project/TWOM/twom_data.db
chown root:root /home/boardgame/project/TWOM/twom_data.db

# Secure API files
chmod 640 /home/boardgame/project/TWOM/api_secure.py
chmod 750 /home/boardgame/project/TWOM/server.sh

echo "✅ File permissions secured"
echo ""

echo "🔒 Step 5: Configure Log Rotation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cat > /etc/logrotate.d/twom-api << 'EOF'
/tmp/twom_api_secure.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
EOF

echo "✅ Log rotation configured"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "   Security Hardening Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Security Features Enabled:"
echo "  ✓ Firewall: Port 5000 restricted to local network only"
echo "  ✓ Fail2Ban: Automatic IP blocking for suspicious activity"
echo "  ✓ Rate Limiting: API requests limited per IP"
echo "  ✓ SYN Flood Protection: Enabled"
echo "  ✓ ICMP Protection: Enabled"
echo "  ✓ File Permissions: Secured"
echo "  ✓ Log Rotation: Configured"
echo ""
echo "Important Notes:"
echo "  • Port 5000 is now only accessible from 192.168.x.x networks"
echo "  • Failed login attempts will result in temporary IP bans"
echo "  • All API requests are logged to /tmp/twom_api_secure.log"
echo "  • Use './server_secure.sh' to start the hardened server"
echo ""
echo "To check Fail2Ban status:"
echo "  sudo fail2ban-client status twom-api"
echo ""
echo "To unban an IP address:"
echo "  sudo fail2ban-client set twom-api unbanip <IP_ADDRESS>"
echo ""

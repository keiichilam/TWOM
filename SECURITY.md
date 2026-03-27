# TWOM API Security Documentation

## 🔒 Security Overview

The TWOM API has been hardened with multiple layers of security to protect against common attacks and vulnerabilities.

## Security Features Implemented

### 1. **Rate Limiting**
Prevents DoS (Denial of Service) attacks by limiting requests per IP address.

**Limits:**
- General endpoints: 200 requests/day, 50 requests/hour
- Search endpoints: 20 requests/hour
- UI pages: 30 requests/minute

**Protection Against:**
- Brute force attacks
- DoS/DDoS attacks
- Resource exhaustion

### 2. **Input Validation & Sanitization**
All user inputs are validated and sanitized before processing.

**Validations:**
- Row numbers: Integer validation with min/max bounds
- Search queries: Character filtering, max length enforcement
- Page parameters: Range validation

**Protection Against:**
- SQL injection
- Command injection
- Path traversal
- XSS (Cross-Site Scripting)

### 3. **SQL Injection Prevention**
Multiple layers of protection:
- Parameterized queries (prepared statements)
- Input validation
- Read-only database mode
- Type checking

**Example Safe Query:**
```python
cursor.execute('SELECT * FROM scripts WHERE row_number = ? LIMIT 1', (row_num,))
```

### 4. **Security Headers**
All responses include comprehensive security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: [strict policy]
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

**Protection Against:**
- Clickjacking
- MIME-type sniffing
- XSS attacks
- Unauthorized framing

### 5. **CORS (Cross-Origin Resource Sharing)**
Configured to restrict cross-origin requests:
- Only GET methods allowed
- Specific origins can be whitelisted
- Credentials not allowed

### 6. **Request Logging**
All requests are logged for security monitoring and audit trails.

**Logged Information:**
- Timestamp
- IP address
- Request method and path
- Response status
- Error messages
- Rate limit violations

**Log Location:** `/tmp/twom_api_secure.log`

### 7. **Firewall Protection**
UFW (Uncomplicated Firewall) configured to:
- Allow port 5000 only from local network (192.168.x.x)
- Deny external access to port 5000
- Rate limit SSH connections
- Default deny incoming

### 8. **Fail2Ban Integration**
Automatic IP blocking for suspicious activity:
- Monitors API logs for attack patterns
- Blocks IPs after 5 failed attempts
- 10-minute detection window
- 1-hour ban duration

### 9. **Read-Only Database**
Database is set to read-only mode to prevent:
- Data modification
- Data deletion
- Database structure changes

### 10. **Error Handling**
Secure error responses that don't leak sensitive information:
- Generic error messages for users
- Detailed logging for administrators
- No stack traces exposed

## Installation & Setup

### 1. Switch to Secure Server

Stop the old server:
```bash
cd /home/boardgame/project/TWOM
./server.sh stop
```

Start the secure server:
```bash
./server_secure.sh start
```

### 2. Apply Security Hardening (Requires Root)

Run the hardening script:
```bash
sudo ./security/harden.sh
```

This will:
- Configure firewall rules
- Install and configure Fail2Ban
- Apply system security settings
- Secure file permissions
- Set up log rotation

### 3. Verify Security

Check security status:
```bash
./server_secure.sh security
```

## Security Monitoring

### View Security Logs
```bash
./server_secure.sh logs
```

### Check Recent Security Events
```bash
grep -E "(WARNING|ERROR|Rate limit)" /tmp/twom_api_secure.log | tail -20
```

### View Fail2Ban Status
```bash
sudo fail2ban-client status twom-api
```

### Check Blocked IPs
```bash
sudo fail2ban-client status twom-api
```

### Unban an IP
```bash
sudo fail2ban-client set twom-api unbanip <IP_ADDRESS>
```

### View Firewall Rules
```bash
sudo ufw status numbered
```

## Attack Mitigation

### SQL Injection
**Protection:**
- Parameterized queries
- Input validation
- Read-only database
- Type checking

**Example Attack Blocked:**
```
/api/scripts/1; DROP TABLE scripts--
→ Blocked by integer validation
```

### XSS (Cross-Site Scripting)
**Protection:**
- Content Security Policy headers
- Input sanitization
- Output encoding

**Example Attack Blocked:**
```
/api/search/scripts?q=<script>alert('XSS')</script>
→ Special characters removed
```

### DoS (Denial of Service)
**Protection:**
- Rate limiting per IP
- Request size limits (16KB max)
- SYN flood protection
- Fail2Ban automatic blocking

**Example Attack Blocked:**
```
1000 requests in 1 minute from same IP
→ Rate limit triggered, IP blocked for 1 hour
```

### Brute Force
**Protection:**
- Rate limiting
- Fail2Ban monitoring
- Automatic IP blocking

**Example Attack Blocked:**
```
Multiple failed requests (404, 400, 429)
→ IP banned after 5 failures in 10 minutes
```

### Path Traversal
**Protection:**
- Input validation
- Whitelist approach (only serve journal.html)
- No directory listing

**Example Attack Blocked:**
```
/../../../../etc/passwd
→ 404 Not Found
```

## Network Security

### Firewall Rules

**Current Configuration:**
```bash
# Allow from local network only
sudo ufw allow from 192.168.0.0/16 to any port 5000 proto tcp

# Deny from all other sources
sudo ufw deny 5000/tcp
```

**To allow specific external IP:**
```bash
sudo ufw allow from <IP_ADDRESS> to any port 5000 proto tcp
```

**To allow entire subnet:**
```bash
sudo ufw allow from <SUBNET>/24 to any port 5000 proto tcp
```

## Best Practices

### 1. Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Python packages
source venv/bin/activate
pip install --upgrade flask flask-limiter flask-cors flask-talisman
```

### 2. Monitor Logs Daily
```bash
# Check for suspicious activity
./server_secure.sh security

# Review recent errors
grep ERROR /tmp/twom_api_secure.log | tail -20
```

### 3. Review Fail2Ban Reports
```bash
# Check banned IPs weekly
sudo fail2ban-client status twom-api
```

### 4. Backup Database
```bash
# Create backup
cp twom_data.db twom_data.db.backup-$(date +%Y%m%d)
```

### 5. Test Security
```bash
# Test rate limiting (should get blocked)
for i in {1..100}; do curl http://192.168.4.232:5000/api/stats; done
```

## Security Checklist

- [x] Rate limiting enabled
- [x] Input validation implemented
- [x] SQL injection prevention
- [x] XSS protection enabled
- [x] Security headers configured
- [x] CORS properly configured
- [x] Request logging enabled
- [x] Firewall configured
- [x] Fail2Ban installed (optional)
- [x] Read-only database mode
- [x] Error handling implemented
- [x] File permissions secured
- [x] Log rotation configured
- [x] Debug mode disabled

## Incident Response

### If Under Attack

1. **Check server status:**
   ```bash
   ./server_secure.sh status
   ```

2. **Review security logs:**
   ```bash
   ./server_secure.sh security
   ```

3. **Check blocked IPs:**
   ```bash
   sudo fail2ban-client status twom-api
   ```

4. **Temporarily block access:**
   ```bash
   sudo ufw deny 5000/tcp
   ```

5. **Review and analyze:**
   ```bash
   grep -E "ERROR|WARNING" /tmp/twom_api_secure.log | less
   ```

6. **Restore access:**
   ```bash
   sudo ufw allow from 192.168.0.0/16 to any port 5000 proto tcp
   ```

## Additional Recommendations

### For Production Deployment

1. **Use HTTPS/SSL:**
   - Obtain SSL certificate (Let's Encrypt)
   - Configure nginx/Apache as reverse proxy
   - Force HTTPS redirects

2. **Add Authentication:**
   - Implement API key authentication
   - Or use OAuth2/JWT tokens
   - Add user session management

3. **Database Isolation:**
   - Move database to separate server
   - Use connection pooling
   - Enable database encryption

4. **Load Balancing:**
   - Use multiple server instances
   - Implement nginx load balancer
   - Add health checks

5. **Enhanced Monitoring:**
   - Set up intrusion detection (OSSEC, Snort)
   - Configure alerting (email, SMS)
   - Use centralized logging (ELK stack)

## Contact & Support

For security issues or questions:
- Review logs: `/tmp/twom_api_secure.log`
- Check status: `./server_secure.sh security`
- Documentation: This file

## Version History

- **v2.0** - Secure version with full hardening
- **v1.0** - Initial version (unsecured)

#!/bin/bash
# TWOM API Secure Server Management Script

PROJECT_DIR="/home/boardgame/project/TWOM"
LOG_FILE="/tmp/twom_api_secure.log"
PID_FILE="/tmp/twom_api_secure.pid"

cd "$PROJECT_DIR" || exit 1

case "$1" in
    start)
        echo "Starting TWOM API Server (Secure)..."
        if pgrep -f "python3 api_secure.py" > /dev/null; then
            echo "⚠️  Server is already running!"
            pgrep -f "python3 api_secure.py"
            exit 1
        fi

        source venv/bin/activate
        nohup python3 api_secure.py > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"

        sleep 2

        if pgrep -f "python3 api_secure.py" > /dev/null; then
            echo "✅ Secure server started successfully!"
            echo ""
            echo "Security Features Enabled:"
            echo "  ✓ Rate limiting (prevents DoS)"
            echo "  ✓ Input validation (prevents injection)"
            echo "  ✓ Security headers (XSS, clickjacking protection)"
            echo "  ✓ Request logging (audit trail)"
            echo "  ✓ Read-only database"
            echo "  ✓ Error handling"
            echo ""
            echo "📊 Access at: http://192.168.4.232:5000/"
            echo "📝 Security logs: tail -f $LOG_FILE"
        else
            echo "❌ Failed to start server. Check logs: tail $LOG_FILE"
            exit 1
        fi
        ;;

    stop)
        echo "Stopping TWOM API Server (Secure)..."
        if ! pgrep -f "python3 api_secure.py" > /dev/null; then
            echo "⚠️  Server is not running."
            exit 1
        fi

        pkill -f "python3 api_secure.py"
        sleep 1

        if pgrep -f "python3 api_secure.py" > /dev/null; then
            echo "⚠️  Server still running, forcing stop..."
            pkill -9 -f "python3 api_secure.py"
        fi

        rm -f "$PID_FILE"
        echo "✅ Server stopped."
        ;;

    restart)
        echo "Restarting TWOM API Server (Secure)..."
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        if pgrep -f "python3 api_secure.py" > /dev/null; then
            echo "✅ Secure server is running"
            echo ""
            pgrep -f "python3 api_secure.py" | while read pid; do
                echo "PID: $pid"
                ps -p $pid -o pid,cmd,etime,%cpu,%mem
            done
            echo ""
            echo "📊 Access at: http://192.168.4.232:5000/"
            echo "📝 View security logs: tail -f $LOG_FILE"
            echo ""
            echo "Security Status:"
            if command -v fail2ban-client &> /dev/null; then
                echo "  Fail2Ban: $(systemctl is-active fail2ban)"
                sudo fail2ban-client status twom-api 2>/dev/null || echo "  Fail2Ban jail not configured yet"
            else
                echo "  Fail2Ban: Not installed"
            fi
            echo "  Firewall: $(sudo ufw status | grep -c "5000")/1 rules active"
        else
            echo "❌ Server is not running"
        fi
        ;;

    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "❌ Log file not found: $LOG_FILE"
        fi
        ;;

    security)
        echo "═══════════════════════════════════════════════════════════════"
        echo "   TWOM API Security Status"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""

        # Check firewall
        echo "🔒 Firewall Status:"
        sudo ufw status | grep 5000 || echo "  Port 5000 not configured"
        echo ""

        # Check fail2ban
        if command -v fail2ban-client &> /dev/null; then
            echo "🔒 Fail2Ban Status:"
            sudo fail2ban-client status twom-api 2>/dev/null || echo "  Jail not active"
        else
            echo "⚠️  Fail2Ban not installed"
        fi
        echo ""

        # Check recent security events
        if [ -f "$LOG_FILE" ]; then
            echo "🔒 Recent Security Events (last 10):"
            grep -E "(WARNING|ERROR|Rate limit)" "$LOG_FILE" | tail -10 || echo "  No security events"
        fi
        echo ""

        # Check file permissions
        echo "🔒 File Permissions:"
        ls -lh twom_data.db api_secure.py 2>/dev/null || echo "  Files not found"
        echo ""
        ;;

    *)
        echo "TWOM API Secure Server Management"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|security}"
        echo ""
        echo "Commands:"
        echo "  start     - Start the secure API server"
        echo "  stop      - Stop the secure API server"
        echo "  restart   - Restart the secure API server"
        echo "  status    - Check server and security status"
        echo "  logs      - View server logs (Ctrl+C to exit)"
        echo "  security  - View detailed security status"
        echo ""
        echo "Quick Access:"
        echo "  http://192.168.4.232:5000/"
        echo ""
        echo "Security Features:"
        echo "  ✓ Rate limiting"
        echo "  ✓ Input validation"
        echo "  ✓ SQL injection prevention"
        echo "  ✓ XSS protection"
        echo "  ✓ Security headers"
        echo "  ✓ Request logging"
        exit 1
        ;;
esac

exit 0

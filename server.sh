#!/bin/bash
# TWOM API Server Management Script

PROJECT_DIR="/home/boardgame/project/TWOM"
LOG_FILE="/tmp/api_server.log"
PID_FILE="/tmp/twom_api.pid"

cd "$PROJECT_DIR" || exit 1

case "$1" in
    start)
        echo "Starting TWOM API Server..."
        if pgrep -f "python3 api.py" > /dev/null; then
            echo "⚠️  Server is already running!"
            pgrep -f "python3 api.py"
            exit 1
        fi

        source venv/bin/activate
        nohup python3 api.py > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"

        sleep 2

        if pgrep -f "python3 api.py" > /dev/null; then
            echo "✅ Server started successfully!"
            echo "📊 Access at: http://192.168.4.232:5000/journal.html"
            echo "📝 Logs: tail -f $LOG_FILE"
        else
            echo "❌ Failed to start server. Check logs: tail $LOG_FILE"
            exit 1
        fi
        ;;

    stop)
        echo "Stopping TWOM API Server..."
        if ! pgrep -f "python3 api.py" > /dev/null; then
            echo "⚠️  Server is not running."
            exit 1
        fi

        pkill -f "python3 api.py"
        sleep 1

        if pgrep -f "python3 api.py" > /dev/null; then
            echo "⚠️  Server still running, forcing stop..."
            pkill -9 -f "python3 api.py"
        fi

        rm -f "$PID_FILE"
        echo "✅ Server stopped."
        ;;

    restart)
        echo "Restarting TWOM API Server..."
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        if pgrep -f "python3 api.py" > /dev/null; then
            echo "✅ Server is running"
            echo ""
            pgrep -f "python3 api.py" | while read pid; do
                echo "PID: $pid"
                ps -p $pid -o pid,cmd,etime,%cpu,%mem
            done
            echo ""
            echo "📊 Access at: http://192.168.4.232:5000/journal.html"
            echo "📝 View logs: tail -f $LOG_FILE"
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

    *)
        echo "TWOM API Server Management"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the API server"
        echo "  stop     - Stop the API server"
        echo "  restart  - Restart the API server"
        echo "  status   - Check server status"
        echo "  logs     - View server logs (Ctrl+C to exit)"
        echo ""
        echo "Quick Access:"
        echo "  http://192.168.4.232:5000/journal.html"
        exit 1
        ;;
esac

exit 0

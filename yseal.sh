#!/bin/bash
# ySEal Management Script
# Usage: ./yseal.sh {start|stop|restart|status}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
MANAGE_PY="$SCRIPT_DIR/manage.py"
PID_FILE="$SCRIPT_DIR/yseal.pid"
LOG_FILE="$SCRIPT_DIR/yseal.log"
HOST="0.0.0.0"
PORT="8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at $VENV_PATH"
        print_info "Please create a virtual environment first: python3 -m venv venv"
        exit 1
    fi
}

# Get the PID of the running server
get_pid() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        # Check if the process is actually running
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "$PID"
        else
            # PID file exists but process is not running
            rm -f "$PID_FILE"
            echo ""
        fi
    else
        echo ""
    fi
}

# Start the server
start_server() {
    check_venv
    
    PID=$(get_pid)
    if [ -n "$PID" ]; then
        print_warning "ySEal server is already running (PID: $PID)"
        exit 1
    fi
    
    print_info "Starting ySEal server on $HOST:$PORT..."
    
    # Activate virtual environment and start server in background
    cd "$SCRIPT_DIR"
    source "$VENV_PATH/bin/activate"
    
    # Start the server in the background
    nohup python "$MANAGE_PY" runserver "$HOST:$PORT" > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    
    # Save PID to file
    echo "$SERVER_PID" > "$PID_FILE"
    
    # Wait a moment to check if server started successfully
    sleep 2
    
    if ps -p "$SERVER_PID" > /dev/null 2>&1; then
        print_success "ySEal server started successfully (PID: $SERVER_PID)"
        print_info "Server running at http://$HOST:$PORT/"
        print_info "Log file: $LOG_FILE"
    else
        print_error "Failed to start ySEal server"
        print_info "Check log file for errors: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Stop the server
stop_server() {
    PID=$(get_pid)
    
    if [ -z "$PID" ]; then
        print_warning "ySEal server is not running"
        exit 1
    fi
    
    print_info "Stopping ySEal server (PID: $PID)..."
    
    # Try graceful shutdown first
    kill "$PID" 2>/dev/null
    
    # Wait up to 5 seconds for process to stop
    for i in {1..5}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            print_success "ySEal server stopped successfully"
            rm -f "$PID_FILE"
            exit 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    print_warning "Server did not stop gracefully, forcing shutdown..."
    kill -9 "$PID" 2>/dev/null
    sleep 1
    
    if ! ps -p "$PID" > /dev/null 2>&1; then
        print_success "ySEal server stopped (forced)"
        rm -f "$PID_FILE"
    else
        print_error "Failed to stop ySEal server"
        exit 1
    fi
}

# Restart the server
restart_server() {
    print_info "Restarting ySEal server..."
    
    PID=$(get_pid)
    if [ -n "$PID" ]; then
        stop_server
        sleep 1
    fi
    
    start_server
}

# Show server status
show_status() {
    PID=$(get_pid)
    
    echo ""
    echo "═══════════════════════════════════════"
    echo "  ySEal Server Status"
    echo "═══════════════════════════════════════"
    
    if [ -n "$PID" ]; then
        print_success "Status: RUNNING"
        echo "  PID: $PID"
        echo "  URL: http://$HOST:$PORT/"
        
        # Get process info
        if command -v ps &> /dev/null; then
            UPTIME=$(ps -p "$PID" -o etime= | tr -d ' ')
            echo "  Uptime: $UPTIME"
            
            CPU=$(ps -p "$PID" -o %cpu= | tr -d ' ')
            MEM=$(ps -p "$PID" -o %mem= | tr -d ' ')
            echo "  CPU: ${CPU}%"
            echo "  Memory: ${MEM}%"
        fi
        
        if [ -f "$LOG_FILE" ]; then
            echo "  Log file: $LOG_FILE"
            LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
            echo "  Log size: $LOG_SIZE"
        fi
    else
        print_error "Status: STOPPED"
    fi
    
    echo "═══════════════════════════════════════"
    echo ""
}

# Show logs
show_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        print_warning "Log file not found: $LOG_FILE"
        exit 1
    fi
    
    # Default to last 50 lines, or use argument if provided
    LINES=${1:-50}
    
    print_info "Showing last $LINES lines of log file:"
    echo "───────────────────────────────────────"
    tail -n "$LINES" "$LOG_FILE"
}

# Main script logic
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [lines]}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the ySEal server"
        echo "  stop     - Stop the ySEal server"
        echo "  restart  - Restart the ySEal server"
        echo "  status   - Show server status"
        echo "  logs     - Show server logs (default: last 50 lines)"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 status"
        echo "  $0 logs 100"
        exit 1
        ;;
esac

exit 0

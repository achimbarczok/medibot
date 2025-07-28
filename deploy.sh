#!/bin/bash
# Medibot Server Deployment Script

set -e  # Exit on error

echo "🚀 Medibot Server Deployment"
echo "============================"

# Configuration
REPO_URL="https://github.com/DEIN-USERNAME/medibot.git"
APP_DIR="/opt/medibot"
SERVICE_NAME="medibot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root (needed for some operations)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. This is OK for initial setup."
    fi
}

# Install Docker if not present
install_docker() {
    if ! command -v docker &> /dev/null; then
        print_status "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        usermod -aG docker $USER
        systemctl enable docker
        systemctl start docker
        print_success "Docker installed"
    else
        print_success "Docker already installed"
    fi
}

# Install Docker Compose if not present
install_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_status "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose installed"
    else
        print_success "Docker Compose already installed"
    fi
}

# Create application directory
setup_directories() {
    print_status "Setting up directories..."
    
    if [ ! -d "$APP_DIR" ]; then
        mkdir -p $APP_DIR
        print_success "Created $APP_DIR"
    fi
    
    mkdir -p $APP_DIR/logs
    chmod 755 $APP_DIR/logs
    print_success "Created logs directory"
}

# Clone or update repository
setup_repository() {
    print_status "Setting up repository..."
    
    if [ ! -d "$APP_DIR/.git" ]; then
        print_status "Cloning repository..."
        git clone $REPO_URL $APP_DIR
        cd $APP_DIR
    else
        print_status "Updating repository..."
        cd $APP_DIR
        git pull origin main
    fi
    
    print_success "Repository ready"
}

# Setup configuration
setup_config() {
    print_status "Setting up configuration..."
    
    cd $APP_DIR
    
    if [ ! -f "config.py" ]; then
        if [ -f "config.py.template" ]; then
            cp config.py.template config.py
            print_warning "Created config.py from template"
            print_warning "⚠️  IMPORTANT: Edit config.py with your credentials!"
            print_warning "⚠️  nano $APP_DIR/config.py"
        else
            print_error "No config template found!"
            exit 1
        fi
    else
        print_success "config.py already exists"
    fi
}

# Start container (choose deployment mode)
start_container() {
    print_status "Building and starting container..."
    
    cd $APP_DIR
    
    # Ask user for deployment mode
    echo ""
    echo "Choose deployment mode:"
    echo "1) Simple mode (container runs script once and exits)"
    echo "2) Cron mode (container runs continuously with internal cron)"
    echo ""
    read -p "Enter choice (1 or 2): " mode_choice
    
    case $mode_choice in
        1)
            print_status "Using simple mode with docker-compose.yml"
            docker-compose build
            docker-compose up -d
            
            # Setup host-based cron for simple mode
            setup_host_cron
            ;;
        2)
            print_status "Using cron mode with docker-compose.cron.yml"
            docker-compose -f docker-compose.cron.yml build
            docker-compose -f docker-compose.cron.yml up -d
            ;;
        *)
            print_error "Invalid choice. Using simple mode by default."
            docker-compose build
            docker-compose up -d
            setup_host_cron
            ;;
    esac
    
    print_success "Container started"
}

# Setup host-based cron for simple mode
setup_host_cron() {
    print_status "Setting up host-based cron (every 10 minutes)..."
    
    # Create cron job
    cron_job="*/10 * * * * cd $APP_DIR && docker-compose run --rm medibot >> $APP_DIR/logs/host-cron.log 2>&1"
    
    # Add to cron if not already exists
    (crontab -l 2>/dev/null | grep -v "medibot"; echo "$cron_job") | crontab -
    
    print_success "Host cron job added"
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create health check script
    cat > /usr/local/bin/medibot-health.sh << EOF
#!/bin/bash
cd $APP_DIR

# Check if container is running
if ! docker-compose ps | grep -q "Up"; then
    echo "\$(date): Medibot container down, restarting..." >> $APP_DIR/logs/health.log
    docker-compose up -d
fi

# Check if cron-mode container is running
if ! docker-compose -f docker-compose.cron.yml ps | grep -q "Up" 2>/dev/null; then
    # Only log if we're actually using cron mode
    if [ -f ".cron-mode" ]; then
        echo "\$(date): Medibot cron container down, restarting..." >> $APP_DIR/logs/health.log
        docker-compose -f docker-compose.cron.yml up -d
    fi
fi
EOF
    
    chmod +x /usr/local/bin/medibot-health.sh
    
    # Add to cron (check every 5 minutes)
    health_cron="*/5 * * * * /usr/local/bin/medibot-health.sh"
    (crontab -l 2>/dev/null | grep -v "medibot-health"; echo "$health_cron") | crontab -
    
    print_success "Health monitoring setup complete"
}

# Create management script
create_management_script() {
    print_status "Creating management script..."
    
    cat > /usr/local/bin/medibot << 'EOF'
#!/bin/bash
# Medibot Management Script

APP_DIR="/opt/medibot"
cd $APP_DIR

# Detect mode
if docker-compose -f docker-compose.cron.yml ps | grep -q "Up" 2>/dev/null; then
    COMPOSE_FILE="docker-compose.cron.yml"
    MODE="cron"
else
    COMPOSE_FILE="docker-compose.yml"
    MODE="simple"
fi

case "$1" in
    start)
        echo "Starting Medibot ($MODE mode)..."
        docker-compose -f $COMPOSE_FILE up -d
        ;;
    stop)
        echo "Stopping Medibot..."
        docker-compose -f docker-compose.yml down 2>/dev/null || true
        docker-compose -f docker-compose.cron.yml down 2>/dev/null || true
        ;;
    restart)
        echo "Restarting Medibot ($MODE mode)..."
        docker-compose -f $COMPOSE_FILE restart
        ;;
    logs)
        echo "Showing Medibot logs..."
        if [ "$MODE" = "cron" ]; then
            echo "=== Container Logs ==="
            docker-compose -f $COMPOSE_FILE logs --tail=20
            echo ""
            echo "=== Cron Logs ==="
            tail -n 20 logs/cron.log 2>/dev/null || echo "No cron logs yet"
        else
            docker-compose -f $COMPOSE_FILE logs --tail=20
            echo ""
            echo "=== Host Cron Logs ==="
            tail -n 20 logs/host-cron.log 2>/dev/null || echo "No host cron logs yet"
        fi
        ;;
    status)
        echo "Medibot Status ($MODE mode):"
        docker-compose -f $COMPOSE_FILE ps
        echo ""
        echo "Recent activity:"
        tail -n 5 logs/*.log 2>/dev/null || echo "No logs found"
        ;;
    update)
        echo "Updating Medibot..."
        git pull origin main
        docker-compose -f $COMPOSE_FILE build
        docker-compose -f $COMPOSE_FILE up -d
        ;;
    config)
        echo "Editing configuration..."
        ${EDITOR:-nano} config.py
        ;;
    test)
        echo "Testing Medibot..."
        docker-compose -f $COMPOSE_FILE run --rm medibot python3 medibot.py
        ;;
    switch-mode)
        echo "Switching deployment mode..."
        echo "Current mode: $MODE"
        echo ""
        echo "Available modes:"
        echo "1) Simple (host cron + single-run containers)"
        echo "2) Cron (persistent container with internal cron)"
        echo ""
        read -p "Choose new mode (1 or 2): " new_mode
        
        # Stop current containers
        docker-compose -f docker-compose.yml down 2>/dev/null || true
        docker-compose -f docker-compose.cron.yml down 2>/dev/null || true
        
        case $new_mode in
            1)
                echo "Switching to simple mode..."
                docker-compose -f docker-compose.yml up -d
                rm -f .cron-mode
                ;;
            2)
                echo "Switching to cron mode..."
                docker-compose -f docker-compose.cron.yml up -d
                touch .cron-mode
                ;;
            *)
                echo "Invalid choice. Keeping current mode."
                docker-compose -f $COMPOSE_FILE up -d
                ;;
        esac
        ;;
    *)
        echo "Medibot Management Commands:"
        echo "  start        - Start container"
        echo "  stop         - Stop container"
        echo "  restart      - Restart container"
        echo "  logs         - Show logs"
        echo "  status       - Show status"
        echo "  update       - Update from Git"
        echo "  config       - Edit configuration"
        echo "  test         - Run manual test"
        echo "  switch-mode  - Switch between simple/cron mode"
        echo ""
        echo "Current mode: $MODE"
        exit 1
        ;;
esac
EOF
    
    chmod +x /usr/local/bin/medibot
    print_success "Management script created: 'medibot' command available"
}

# Main installation
main() {
    print_status "Starting Medibot installation..."
    
    check_root
    install_docker
    install_docker_compose
    setup_directories
    setup_repository
    setup_config
    start_container
    setup_monitoring
    create_management_script
    
    echo ""
    print_success "🎉 Medibot installation complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit configuration: nano $APP_DIR/config.py"
    echo "2. Restart container: medibot restart"
    echo "3. Check logs: medibot logs"
    echo "4. Check status: medibot status"
    echo ""
    echo "🛠️  Management commands:"
    echo "  medibot start        - Start container"
    echo "  medibot stop         - Stop container"
    echo "  medibot restart      - Restart container"
    echo "  medibot logs         - Show logs"
    echo "  medibot status       - Show status"
    echo "  medibot update       - Update from Git"
    echo "  medibot config       - Edit configuration"
    echo "  medibot test         - Run manual test"
    echo "  medibot switch-mode  - Switch deployment mode"
    echo ""
    print_warning "⚠️  Don't forget to configure your Telegram bot and doctor URLs!"
    print_warning "⚠️  Run: medibot config"
}

# Run main function
main "$@"

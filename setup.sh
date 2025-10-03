#!/bin/bash

set -e

echo "🚀 Setting up Employee Monitoring System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm -v)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is required but not installed"
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p data
    
    cd ..
    print_success "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install npm dependencies
    print_status "Installing npm dependencies..."
    npm install
    
    cd ..
    print_success "Frontend setup completed"
}

# Create start scripts
create_start_scripts() {
    print_status "Creating start scripts..."
    
    # Start backend script
    cat > start_backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
EOF
    
    # Start frontend script
    cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm run dev
EOF
    
    # Start all script
    cat > start_all.sh << 'EOF'
#!/bin/bash
# Start backend in background
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Documentation: http://localhost:8000/docs"

# Handle script termination
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait
EOF
    
    # Stop all script
    cat > stop_all.sh << 'EOF'
#!/bin/bash
echo "Stopping all services..."
pkill -f "uvicorn main:app"
pkill -f "npm run dev"
echo "All services stopped"
EOF
    
    # Make scripts executable
    chmod +x start_backend.sh start_frontend.sh start_all.sh stop_all.sh
    
    print_success "Start scripts created"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test backend
    cd backend
    source venv/bin/activate
    python -c "import fastapi; print('FastAPI OK')" && \
    python -c "import cv2; print('OpenCV OK')" && \
    python -c "import deepface; print('DeepFace OK')"
    cd ..
    
    # Test frontend
    cd frontend
    npm list react && npm list vite
    cd ..
    
    print_success "Installation test completed"
}

# Main setup process
main() {
    print_status "Starting Employee Monitoring System setup..."
    
    check_prerequisites
    setup_backend
    setup_frontend
    create_start_scripts
    test_installation
    
    print_success "🎉 Setup completed successfully!"
    echo ""
    print_status "Next steps:"
    echo "  1. Run './start_all.sh' to start both backend and frontend"
    echo "  2. Open http://localhost:5173 in your browser"
    echo "  3. Check http://localhost:8000/docs for API documentation"
    echo ""
    print_status "Available scripts:"
    echo "  ./start_backend.sh  - Start backend only"
    echo "  ./start_frontend.sh - Start frontend only"
    echo "  ./start_all.sh      - Start both services"
    echo "  ./stop_all.sh       - Stop all services"
    echo ""
    print_warning "Note: Make sure your camera is connected and accessible"
}

# Run main function
main
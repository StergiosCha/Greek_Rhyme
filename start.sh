#!/bin/bash

echo "🎭 Greek Rhyme System - Startup Script"
echo "======================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys before continuing."
    echo "   nano .env"
    exit 1
fi

echo "✓ Environment file found"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Starting services:"
echo "  • Backend API: http://localhost:8000"
echo "  • Frontend: http://localhost:8080"
echo ""

# Start backend in background
echo "🚀 Starting backend..."
python3 app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend server
echo "🌐 Starting frontend..."
cd "$(dirname "$0")"
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "✅ System is running!"
echo ""
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🎨 Frontend Interface: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle cleanup on exit
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Keep script running
wait

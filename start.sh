#!/bin/bash

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧱 Minifig Builder - Setup & Run${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env with your BrickLink API credentials${NC}"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

# Check for Node
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites found${NC}"
echo ""

# Setup backend
echo -e "${BLUE}Setting up Backend...${NC}"
cd backend

if [ ! -d venv ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✅ Backend ready${NC}"
cd ..

# Setup frontend
echo -e "${BLUE}Setting up Frontend...${NC}"
cd frontend

if [ ! -d node_modules ]; then
    echo "Installing npm dependencies..."
    npm install > /dev/null 2>&1
fi

echo -e "${GREEN}✅ Frontend ready${NC}"
cd ..

echo ""
echo -e "${GREEN}🚀 All set! Starting services...${NC}"
echo ""
echo -e "${BLUE}Backend${NC}  : http://localhost:8000"
echo -e "${BLUE}Frontend${NC} : http://localhost:3000"
echo -e "${BLUE}API Docs${NC} : http://localhost:8000/docs"
echo ""

# Start backend and frontend in background
echo -e "${YELLOW}Starting Backend...${NC}"
(cd backend && source venv/bin/activate && python app.py) &
BACKEND_PID=$!

sleep 2

read -r -p "Start frontend dev server? [y/N] " START_FRONTEND
if [[ "$START_FRONTEND" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Starting Frontend...${NC}"
    (cd frontend && npm run dev) &
    FRONTEND_PID=$!

    sleep 2
else
    echo -e "${YELLOW}Skipping frontend start${NC}"
    FRONTEND_PID=
fi

echo -e "${GREEN}✅ Both services started!${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both services${NC}"
echo ""

# Handle cleanup
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo 'Services stopped'; exit 0" INT

wait

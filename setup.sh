#!/bin/bash

echo "========================================"
echo "Pipecat Voice Agent Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo ""

echo "[2/4] Activating virtual environment..."
source venv/bin/activate
echo ""

echo "[3/4] Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "[4/4] Setting up environment file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "========================================"
    echo "IMPORTANT: Edit .env file and add your Azure credentials:"
    echo "- AZURE_SPEECH_API_KEY"
    echo "- AZURE_SPEECH_REGION"
    echo "========================================"
else
    echo ".env file already exists."
fi
echo ""

echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Azure credentials"
echo "2. Run: python main.py"
echo "3. Open browser to: http://localhost:8000/client"
echo ""

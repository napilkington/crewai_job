#!/bin/bash
# Quick setup script for the browser extension workflow

echo "======================================"
echo "🚀 CrewAI Job Extension Setup"
echo "======================================"
echo ""

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "📦 Activating virtual environment..."
    source nat_venv/bin/activate
fi

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📥 Installing Flask and Flask-CORS..."
    pip install flask flask-cors
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "======================================"
echo "📖 Next Steps:"
echo "======================================"
echo ""
echo "1️⃣  Install Browser Extension:"
echo "   • Open Chrome/Edge → chrome://extensions/"
echo "   • Enable 'Developer mode'"
echo "   • Click 'Load unpacked'"
echo "   • Select: $(pwd)/browser-extension"
echo ""
echo "2️⃣  Start the local server:"
echo "   python server.py"
echo ""
echo "3️⃣  Use the extension:"
echo "   • Go to a LinkedIn job posting"
echo "   • Click the extension icon"
echo "   • Click 'Extract & Process Job'"
echo ""
echo "======================================"
echo ""

read -p "Start the server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python server.py
fi

#!/usr/bin/env bash
# ==============================================================================
#  👟 STARBOYZ FOOTWEAR — AI SALES OS & ENTERPRISE CRM PLATFORM LAUNCHER
# ==============================================================================

set -e

echo ""
echo "==============================================================================="
echo "   👟 STARBOYZ FOOTWEAR — AI SALES AGENT + UNIFIED CRM PLATFORM"
echo "==============================================================================="
echo ""

# Check python environment
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH."
    exit 1
fi

echo "🔹 Checking environment configuration (.env)..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "⚠️ .env not found. Copying from .env.example..."
        cp .env.example .env
    else
        echo "⚠️ No .env file found. Creating default .env..."
        cat <<EOF > .env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
AI_PROVIDER=gemini
FIREBASE_PROJECT_ID=ai-sales-agent---shoe
PORT=8000
HOST=127.0.0.1
EOF
    fi
fi

echo "✅ Environment configured."
echo ""
echo "🚀 Available Interfaces:"
echo "   1. 🌐 SaaS CRM Command Center : http://localhost:8000"
echo "   2. 📚 Interactive OpenAPI Docs: http://localhost:8000/docs"
echo "   3. 👟 Terminal AI Sales Chat  : Run 'python terminal_chat.py' in another terminal"
echo ""
echo "==============================================================================="
echo "   Starting FastAPI Server & CRM Backend on http://127.0.0.1:8000"
echo "   Press Ctrl+C to terminate the server."
echo "==============================================================================="
echo ""

exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

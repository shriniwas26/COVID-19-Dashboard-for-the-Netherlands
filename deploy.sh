#!/bin/bash

# COVID-19 Dashboard Deployment Script
# This script helps with local testing and deployment preparation

echo "🚀 COVID-19 Dashboard Deployment Script"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "covid_dashboard_nl.py" ]; then
    echo "❌ Error: covid_dashboard_nl.py not found. Please run this script from the project root."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found."
    exit 1
fi

# Check if data files exist
if [ ! -f "data/COVID-19_aantallen_gemeente_cumulatief.csv" ]; then
    echo "⚠️  Warning: COVID-19 data file not found. The app may not work properly."
fi

if [ ! -f "data/NL_Population_Latest.csv" ]; then
    echo "⚠️  Warning: Population data file not found. The app may not work properly."
fi

echo "✅ Project structure looks good!"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Test the application
echo "🧪 Testing application..."
python -c "import covid_dashboard_nl; print('✅ Application imports successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Application test passed!"
else
    echo "❌ Application test failed"
    exit 1
fi

echo ""
echo "🎉 Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Set up Render hosting platform"
echo "3. Configure GitHub secrets (RENDER_SERVICE_ID and RENDER_API_KEY)"
echo "4. Your dashboard will be automatically deployed!"
echo ""
echo "For detailed instructions, see DEPLOYMENT.md"

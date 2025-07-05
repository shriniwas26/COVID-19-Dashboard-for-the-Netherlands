#!/bin/bash

# COVID-19 Dashboard Docker Runner
# This script makes it easy to run the dashboard using Docker Compose

set -e

echo "🚀 COVID-19 Dashboard - Docker Runner"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &>/dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &>/dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if data files exist
if [ ! -f "data/COVID-19_aantallen_gemeente_cumulatief.csv" ]; then
    echo "⚠️  Warning: COVID-19 data file not found."
    echo "   The dashboard may not work properly without data files."
fi

if [ ! -f "data/NL_Population_Latest.csv" ]; then
    echo "⚠️  Warning: Population data file not found."
    echo "   The dashboard may not work properly without data files."
fi

echo "✅ Docker environment check passed!"

# Function to show usage
show_usage() {
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the dashboard (default)"
    echo "  stop      - Stop the dashboard"
    echo "  restart   - Restart the dashboard"
    echo "  logs      - Show application logs"
    echo "  build     - Build the Docker image"
    echo "  clean     - Remove containers and images"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start the dashboard"
    echo "  $0 logs     # View logs"
    echo "  $0 stop     # Stop the dashboard"
    echo ""
}

# Function to start the dashboard
start_dashboard() {
    echo "🔧 Building and starting the dashboard..."
    docker-compose up --build -d

    echo ""
    echo "✅ Dashboard is starting up!"
    echo "🌐 Access the dashboard at: http://localhost:5005"
    echo "📊 The dashboard will be available in a few moments..."
    echo ""
    echo "Useful commands:"
    echo "  $0 logs     # View logs"
    echo "  $0 stop     # Stop the dashboard"
    echo ""
}

# Function to stop the dashboard
stop_dashboard() {
    echo "🛑 Stopping the dashboard..."
    docker-compose down
    echo "✅ Dashboard stopped!"
}

# Function to restart the dashboard
restart_dashboard() {
    echo "🔄 Restarting the dashboard..."
    docker-compose restart
    echo "✅ Dashboard restarted!"
}

# Function to show logs
show_logs() {
    echo "📋 Showing dashboard logs..."
    docker-compose logs -f covid-dashboard
}

# Function to build the image
build_image() {
    echo "🔨 Building Docker image..."
    docker-compose build
    echo "✅ Image built successfully!"
}

# Function to clean up
clean_up() {
    echo "🧹 Cleaning up Docker resources..."
    docker-compose down --rmi all --volumes --remove-orphans
    echo "✅ Cleanup completed!"
}

# Main script logic
case "${1:-start}" in
"start")
    start_dashboard
    ;;
"stop")
    stop_dashboard
    ;;
"restart")
    restart_dashboard
    ;;
"logs")
    show_logs
    ;;
"build")
    build_image
    ;;
"clean")
    clean_up
    ;;
"help" | "-h" | "--help")
    show_usage
    ;;
*)
    echo "❌ Unknown command: $1"
    show_usage
    exit 1
    ;;
esac

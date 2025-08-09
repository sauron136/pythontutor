#!/bin/bash

echo "🐍 Setting up Interactive Python Tutor..."

# Function to detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    else
        echo "unknown"
    fi
}

# Install Python, pip, git, and vim based on OS
install_prerequisites() {
    OS=$(detect_os)
    echo "📦 Detected OS: $OS"
    case $OS in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y python3 python3-pip git vim
            ;;
        fedora)
            sudo dnf install -y python3 python3-pip git vim
            ;;
        arch|manjaro)
            sudo pacman -Syu --noconfirm python python-pip git vim
            ;;
        opensuse*)
            sudo zypper install -y python3 python3-pip git vim
            ;;
        *)
            echo "⚠️ Unsupported OS. Please install Python 3.6+, pip, git, and vim manually."
            exit 1
            ;;
    esac
}

# Check if Python and pip are installed
if ! command -v python3 &>/dev/null; then
    echo "⚠️ Python3 not found. Installing..."
    install_prerequisites
fi

if ! command -v pip3 &>/dev/null; then
    echo "⚠️ pip3 not found. Installing..."
    install_prerequisites
fi

# Create virtual environment
echo "📁 Creating virtual environment..."
python3 -m venv ~/python-tutor-venv
source ~/python-tutor-venv/bin/activate

# Install package and dependencies
echo "📦 Installing python-tutor package..."
pip install git+https://github.com/yourusername/python-tutor.git

# Create student workspace
echo "📁 Creating student workspace..."
mkdir -p ~/my_projects

echo ""
echo "✅ Setup complete!"
echo ""
echo "📁 Created structure:"
echo "   • Virtual environment: ~/python-tutor-venv/"
echo "   • Student workspace: ~/my_projects/"
echo ""
echo "🚀 To get started:"
echo "   1. Activate the virtual environment: source ~/python-tutor-venv/bin/activate"
echo "   2. Run 'python-tutor' to start the interactive shell"
echo "   3. To deactivate the virtual environment, run: deactivate"

#!/bin/bash

echo "🐍 Setting up Interactive Python Tutor..."

# Function to detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
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
            sudo apt install -y python3 python3-pip git vim openssh-client
            ;;
        fedora)
            sudo dnf install -y python3 python3-pip git vim openssh-clients
            ;;
        arch|manjaro)
            sudo pacman -Syu --noconfirm python python-pip git vim openssh
            ;;
        opensuse*)
            sudo zypper install -y python3 python3-pip git vim openssh
            ;;
        macos)
            if ! command -v brew &>/dev/null; then
                echo "📦 Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install python git vim
            ;;
        *)
            echo "⚠️ Unsupported OS. Please install Python 3.6+, pip, git, vim, and SSH client manually."
            exit 1
            ;;
    esac
}

# Setup SSH key for GitHub
setup_ssh_for_github() {
    echo ""
    echo "🔑 Setting up SSH access for GitHub..."
    
    # Check if SSH key already exists
    if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
        echo "✅ SSH key already exists!"
        
        # Show the public key
        if [ -f ~/.ssh/id_ed25519.pub ]; then
            echo "📋 Your SSH public key (Ed25519):"
            cat ~/.ssh/id_ed25519.pub
        elif [ -f ~/.ssh/id_rsa.pub ]; then
            echo "📋 Your SSH public key (RSA):"
            cat ~/.ssh/id_rsa.pub
        fi
    else
        echo "🔧 No SSH key found. Let's create one..."
        
        # Get user's email for SSH key
        read -p "Enter your GitHub email address: " github_email
        
        if [ -z "$github_email" ]; then
            echo "❌ Email is required for SSH key generation."
            return 1
        fi
        
        # Generate Ed25519 key (more secure and faster)
        echo "🔑 Generating Ed25519 SSH key..."
        ssh-keygen -t ed25519 -C "$github_email" -f ~/.ssh/id_ed25519 -N ""
        
        # Start SSH agent and add the key
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/id_ed25519
        
        echo "✅ SSH key generated successfully!"
        echo ""
        echo "📋 Your SSH public key:"
        cat ~/.ssh/id_ed25519.pub
    fi
    
    echo ""
    echo "🚀 To complete GitHub SSH setup:"
    echo "   1. Copy the SSH key above (the entire line starting with 'ssh-ed25519')"
    echo "   2. Go to https://github.com/settings/keys"
    echo "   3. Click 'New SSH key'"
    echo "   4. Paste your key and give it a title (e.g., 'Python Tutor Machine')"
    echo "   5. Click 'Add SSH key'"
    echo ""
    
    # Test SSH connection
    read -p "Press Enter after adding your SSH key to GitHub to test the connection..."
    
    echo "🧪 Testing SSH connection to GitHub..."
    if ssh -T git@github.com -o ConnectTimeout=10 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ SSH connection to GitHub successful!"
        return 0
    else
        echo "⚠️ SSH connection test inconclusive. This might be normal."
        echo "   If you see 'Permission denied', double-check your SSH key setup."
        echo "   You can test manually with: ssh -T git@github.com"
        return 1
    fi
}

# Get GitHub username
get_github_username() {
    echo ""
    read -p "Enter your GitHub username: " github_username
    
    if [ -z "$github_username" ]; then
        echo "❌ GitHub username is required for project pushes."
        return 1
    fi
    
    # Save username for later use
    echo "$github_username" > ~/.python_tutor_github_user
    echo "✅ GitHub username saved: $github_username"
    return 0
}

# Main installation process
main() {
    # Check if Python and pip are installed
    if ! command -v python3 &>/dev/null; then
        echo "⚠️ Python3 not found. Installing..."
        install_prerequisites
    fi

    if ! command -v pip3 &>/dev/null; then
        echo "⚠️ pip3 not found. Installing..."
        install_prerequisites
    fi

    if ! command -v git &>/dev/null; then
        echo "⚠️ git not found. Installing..."
        install_prerequisites
    fi

    # Create virtual environment
    echo "📁 Creating virtual environment..."
    python3 -m venv ~/pythontutor-venv
    source ~/pythontutor-venv/bin/activate

    # Install package and dependencies
    echo "📦 Installing pythontutor package..."
    pip install git+https://github.com/sauron136/pythontutor.git

    # Create student workspace
    echo "📁 Creating student workspace..."
    mkdir -p ~/my_projects

    # Setup SSH for GitHub
    echo ""
    read -p "Would you like to set up SSH access for GitHub? (recommended) [Y/n]: " setup_ssh
    if [[ $setup_ssh != "n" && $setup_ssh != "N" ]]; then
        if setup_ssh_for_github; then
            get_github_username
        fi
    else
        echo "⚠️ Skipping SSH setup. You'll need to configure GitHub authentication manually."
        echo "💡 You can run this script again or set up SSH later using: ssh-keygen -t ed25519"
    fi

    # Configure git if not already configured
    if [ -z "$(git config --global user.name)" ] || [ -z "$(git config --global user.email)" ]; then
        echo ""
        echo "🔧 Configuring Git..."
        read -p "Enter your full name for Git commits: " git_name
        read -p "Enter your email for Git commits: " git_email
        
        git config --global user.name "$git_name"
        git config --global user.email "$git_email"
        echo "✅ Git configured!"
    fi

    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "📁 Created structure:"
    echo "   • Virtual environment: ~/pythontutor-venv/"
    echo "   • Student workspace: ~/my_projects/"
    if [ -f ~/.python_tutor_github_user ]; then
        echo "   • GitHub user: $(cat ~/.python_tutor_github_user)"
    fi
    echo ""
    echo "🚀 To get started:"
    echo "   1. Activate the virtual environment: source ~/pythontutor-venv/bin/activate"
    echo "   2. Run 'pythontutor' to start the interactive shell"
    echo "   3. To deactivate the virtual environment, run: deactivate"
    echo ""
    echo "🔑 SSH Key Management:"
    echo "   • Your SSH keys are in ~/.ssh/"
    echo "   • Test GitHub connection: ssh -T git@github.com"
    echo "   • Manage keys at: https://github.com/settings/keys"
}

# Run main function
main "$@"

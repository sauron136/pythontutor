# Interactive Python Tutor

A command-line based interactive Python learning system where students:
1. **Read** lesson content
2. **Practice** with guided exercises  
3. **Build** real projects to apply their skills

## Quick Start

### Installation
Install directly from GitHub:

```bash
pip install git+https://github.com/sauron136/python-tutor.git
```

### Start Learning
After installation, you can run the tutor from anywhere:

```bash
pythontutor
```

## System Requirements

- **Operating System**: Linux, macOS, or WSL on Windows
- **Python**: 3.6 or higher
- **Tools**: `git`, `vim` (recommended for editing)
- **Internet**: Required for package installation and GitHub integration

## GitHub Integration

The tutor includes seamless GitHub integration using SSH keys - no Personal Access Tokens needed!

### SSH Setup
To push your projects to GitHub, you'll need SSH keys set up:

1. **Generate SSH Key** (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **Add to SSH Agent**:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. **Copy Public Key**:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

4. **Add to GitHub**:
   - Go to [GitHub SSH Settings](https://github.com/settings/keys)
   - Click "New SSH key"
   - Paste your public key
   - Give it a descriptive title (e.g., "Python Tutor Laptop")

5. **Test Connection**:
   ```bash
   ssh -T git@github.com
   ```

### In-App SSH Management
The Python Tutor includes built-in SSH management:
- Use the `ssh` command in project mode to set up SSH
- Use the Settings menu to test your SSH connection
- Get guided help if SSH isn't working

## How It Works

### Lesson Structure
Each lesson follows the same pattern:
1. **📖 Read** - Markdown content explaining concepts
2. **🎯 Practice** - Interactive coding exercises with validation
3. **🚀 Build** - Real projects to apply what you learned

### Project Development
Projects are created in `~/my_projects/project_XX/` with:
- **Template code** to get you started
- **Implementation guides** explaining what to build
- **Automated tests** to check your work
- **GitHub integration** to share your projects

### Progress Tracking
Your progress is automatically saved:
- Completed lessons and projects
- Exercise attempts and hints used
- Current lesson position
- GitHub username and settings

## Directory Structure

```
~/my_projects/                # Your project workspace
  ├── project_01/
  ├── project_02/
  └── ...
~/.python_tutor_progress.json # Progress tracking
~/.python_tutor_github_user   # GitHub username
~/.ssh/                       # SSH keys for GitHub
```

## Available Commands

### Main Menu
- **Start/Continue Current Lesson** - Follow the structured learning path
- **Practice Exercises** - Repeat exercises from any lesson
- **Work on Project** - Continue working on any project
- **View Progress** - See your learning statistics
- **Settings** - Configure GitHub and SSH
- **Reset Progress** - Start over (careful!)

### Project Mode Commands
- `edit` - Open your code in vim
- `run` - Execute your project
- `test` - Run automated tests
- `push` - Push to GitHub
- `submit` - Mark project complete and advance
- `ssh` - Set up or test SSH connection
- `user` - Set GitHub username
- `help` - Show available commands

## Advanced Features

### Code Quality Checks
Projects are automatically checked for:
- Proper docstrings
- Main function structure
- PEP 8 style compliance
- Error-free execution

### GitHub Repository Creation
When you push a project, the tutor can:
- Automatically create repositories on GitHub
- Use meaningful commit messages
- Set up proper git configuration
- Handle authentication securely via SSH

### Smart Exercise Validation
Exercises include:
- Variable type checking
- Output validation
- Helpful error messages
- Progressive hints
- Multiple attempt tracking

## Troubleshooting

### Installation Issues
**Problem**: Command not found after installation
**Solution**: Make sure you're using the correct command:
```bash
pythontutor  # Note: no dash or underscore
```

**Problem**: Module not found errors
**Solution**: Try reinstalling:
```bash
pip uninstall pythontutor
pip install git+https://github.com/sauron136/python-tutor.git
```

### SSH Issues
**Problem**: `Permission denied (publickey)`
**Solution**: 
```bash
# Test SSH connection
ssh -T git@github.com

# If it fails, check your SSH key
ls -la ~/.ssh/
cat ~/.ssh/id_ed25519.pub

# Make sure it's added to GitHub: https://github.com/settings/keys
```

### Project Issues
**Problem**: Lessons not found
**Solution**: This usually indicates a packaging issue. Try reinstalling the package.

**Problem**: Repository doesn't exist
**Solution**: The tutor will guide you to create it manually at https://github.com/new

## Development Installation

If you want to contribute or modify the code:

```bash
git clone https://github.com/sauron136/python-tutor.git
cd python-tutor
pip install -e .
```

## Customization

### Adding Your Own Content
The package structure allows easy customization:
- Lessons: `src/python_tutor/lessons/lesson_XX/`
- Projects: `src/python_tutor/projects/project_XX/`

### Extending the Curriculum
Each lesson needs:
- `content.md` - Lesson material
- `exercises.json` - Interactive exercises

Each project needs:
- `requirements.md` - Project description
- `template.py` - Starting code
- `implementation_guide.md` - Step-by-step guide
- `test.py` - Automated validation

## Support

- **Issues**: [GitHub Issues](https://github.com/sauron136/python-tutor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sauron136/python-tutor/discussions)
- **SSH Help**: [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

## Contributing

Contributions welcome! Please see our contributing guidelines and submit pull requests for:
- New lessons and projects
- Bug fixes and improvements
- Documentation updates
- Additional OS support

## License

MIT License - see LICENSE file for details.

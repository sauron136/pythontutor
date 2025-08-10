"""
GitHub integration and SSH management module for Python Tutor.
Handles SSH key setup, GitHub authentication, and repository operations.
"""

import subprocess
import os
from pathlib import Path


class GitHubIntegration:
    """Handles all GitHub-related operations and SSH setup"""
    
    def __init__(self, github_user_file):
        self.github_user_file = Path(github_user_file)
        self.github_username = self.load_github_user()
    
    def load_github_user(self):
        """Load GitHub username from file"""
        try:
            with open(self.github_user_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def save_github_user(self, username):
        """Save GitHub username to file"""
        self.github_username = username
        with open(self.github_user_file, 'w') as f:
            f.write(username)
    
    def check_ssh_setup(self):
        """Check if SSH is properly configured for GitHub"""
        try:
            result = subprocess.run(
                ["ssh", "-T", "git@github.com", "-o", "ConnectTimeout=5"],
                capture_output=True, text=True, timeout=10
            )
            return "successfully authenticated" in result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def setup_github_ssh(self):
        """Guide user through SSH setup with interactive prompts"""
        print("\n🔑 GITHUB SSH SETUP")
        print("=" * 40)
        
        if self.check_ssh_setup():
            print("✅ SSH is already configured for GitHub!")
            return True
        
        print("🔧 SSH setup required for pushing projects to GitHub.")
        print("\nSteps to set up SSH:")
        print("1. Generate an SSH key:")
        print("   ssh-keygen -t ed25519 -C \"your_email@example.com\"")
        print("2. Add the key to your SSH agent:")
        print("   eval \"$(ssh-agent -s)\"")
        print("   ssh-add ~/.ssh/id_ed25519")
        print("3. Copy your public key:")
        print("   cat ~/.ssh/id_ed25519.pub")
        print("4. Add it to GitHub at: https://github.com/settings/keys")
        print("5. Test the connection:")
        print("   ssh -T git@github.com")
        
        setup_now = input("\nWould you like me to help you set this up now? (y/n): ").lower()
        if setup_now == 'y':
            return self.guided_ssh_setup()
        else:
            print("💡 You can run the 'ssh' command anytime to set this up.")
            return False
    
    def guided_ssh_setup(self):
        """Provide step-by-step SSH setup guidance"""
        print("\n🔧 GUIDED SSH SETUP")
        print("=" * 30)
        
        # Step 1: Check for existing keys
        ssh_dir = Path.home() / ".ssh"
        ed25519_key = ssh_dir / "id_ed25519"
        rsa_key = ssh_dir / "id_rsa"
        
        if ed25519_key.exists() or rsa_key.exists():
            print("✅ SSH key already exists!")
            if ed25519_key.with_suffix('.pub').exists():
                print("\n📋 Your public key:")
                with open(ed25519_key.with_suffix('.pub')) as f:
                    print(f.read())
            elif rsa_key.with_suffix('.pub').exists():
                print("\n📋 Your public key:")
                with open(rsa_key.with_suffix('.pub')) as f:
                    print(f.read())
        else:
            # Step 2: Generate new key
            email = input("Enter your GitHub email address: ").strip()
            if not email:
                print("❌ Email is required for SSH key generation.")
                return False
            
            print("🔑 Generating SSH key...")
            try:
                subprocess.run([
                    "ssh-keygen", "-t", "ed25519", "-C", email,
                    "-f", str(ed25519_key), "-N", ""
                ], check=True)
                
                print("✅ SSH key generated successfully!")
                print("\n📋 Your public key:")
                with open(ed25519_key.with_suffix('.pub')) as f:
                    print(f.read())
            except subprocess.CalledProcessError:
                print("❌ Failed to generate SSH key.")
                return False
        
        print("\n🌐 Now add this key to GitHub:")
        print("1. Go to: https://github.com/settings/keys")
        print("2. Click 'New SSH key'")
        print("3. Paste the key above")
        print("4. Give it a title and click 'Add SSH key'")
        
        input("\nPress Enter after adding the key to GitHub...")
        
        # Test the connection
        print("🧪 Testing SSH connection...")
        if self.check_ssh_setup():
            print("✅ SSH setup successful! You can now push projects to GitHub.")
            return True
        else:
            print("❌ SSH test failed. Please check your setup.")
            print("💡 Try manually: ssh -T git@github.com")
            return False
    
    def push_to_github_ssh(self, lesson_num, project_dir):
        """Push project to GitHub using SSH"""
        if not self.github_username:
            print("❌ GitHub username not set. Use 'user' command first.")
            return False
        
        if not self.check_ssh_setup():
            print("❌ SSH not configured for GitHub. Use 'ssh' command first.")
            return False
        
        # Verify git is available
        if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
            print("❌ Git is not installed. Please install git and try again.")
            return False
        
        repo_name = f"python-tutor-project-{lesson_num:02d}"
        repo_url = f"git@github.com:{self.github_username}/{repo_name}.git"
        
        try:
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_dir)
            
            # Initialize git if needed
            if not os.path.exists(".git"):
                print("🔧 Initializing git repository...")
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "branch", "-M", "main"], check=True)
                subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
                
                # Create a basic README
                with open("README.md", "w") as f:
                    f.write(f"# Python Tutor - Project {lesson_num}\n\n")
                    f.write(f"This is my solution for Project {lesson_num} from the Interactive Python Tutor.\n\n")
                    f.write("## How to Run\n\n")
                    f.write("```bash\npython main.py\n```\n")
            
            # Stage all files
            subprocess.run(["git", "add", "."], check=True)
            
            # Check if there are changes to commit
            status_result = subprocess.run(["git", "status", "--porcelain"], 
                                         capture_output=True, text=True)
            if not status_result.stdout.strip():
                print("ℹ️ No changes to commit.")
                return True
            
            # Commit changes
            commit_msg = f"Complete project {lesson_num}: Python Tutor Assignment"
            commit_result = subprocess.run(["git", "commit", "-m", commit_msg], 
                                         capture_output=True, text=True)
            
            if commit_result.returncode != 0 and "nothing to commit" not in commit_result.stdout:
                print(f"⚠️ Commit warning: {commit_result.stdout}")
            
            # Push to GitHub
            print(f"🚀 Pushing to GitHub...")
            push_result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                                       capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print(f"✅ Successfully pushed to GitHub!")
                print(f"🌐 View your project: https://github.com/{self.github_username}/{repo_name}")
                return True
            else:
                # Handle common push errors
                if "does not exist" in push_result.stderr or "repository not found" in push_result.stderr:
                    print(f"⚠️ Repository '{repo_name}' doesn't exist yet.")
                    create_repo = input(f"Create repository '{repo_name}' on GitHub? (y/n): ").lower()
                    if create_repo == 'y':
                        print("🌐 Please create the repository manually:")
                        print(f"   1. Go to: https://github.com/new")
                        print(f"   2. Repository name: {repo_name}")
                        print(f"   3. Make it public (recommended)")
                        print(f"   4. Don't initialize with README (we have one)")
                        print(f"   5. Click 'Create repository'")
                        print(f"   6. Then run 'push' command again")
                        return False
                    else:
                        print("❌ Push cancelled.")
                        return False
                elif "permission denied" in push_result.stderr.lower():
                    print("❌ Permission denied. Check your SSH key setup.")
                    print("💡 Run 'ssh' command to reconfigure SSH.")
                    return False
                else:
                    print(f"❌ Push failed: {push_result.stderr}")
                    return False
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
            print("💡 Make sure your repository exists and you have write permissions.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        finally:
            # Always return to original directory
            os.chdir(original_dir)
    
    def test_ssh_connection(self):
        """Test SSH connection to GitHub and provide feedback"""
        print("🧪 Testing SSH connection to GitHub...")
        
        if self.check_ssh_setup():
            print("✅ SSH connection successful!")
            print(f"👤 Authenticated as: {self.github_username or 'GitHub user'}")
            return True
        else:
            print("❌ SSH connection failed.")
            print("\n🔧 Troubleshooting steps:")
            print("1. Make sure you have an SSH key: ls ~/.ssh/")
            print("2. Check if key is added to agent: ssh-add -l")
            print("3. Verify key is on GitHub: https://github.com/settings/keys")
            print("4. Test manually: ssh -T git@github.com")
            return False
    
    def get_github_profile_url(self):
        """Get the user's GitHub profile URL"""
        if self.github_username:
            return f"https://github.com/{self.github_username}"
        return None
    
    def get_project_repository_url(self, lesson_num):
        """Get the expected repository URL for a project"""
        if self.github_username:
            repo_name = f"python-tutor-project-{lesson_num:02d}"
            return f"https://github.com/{self.github_username}/{repo_name}"
        return None

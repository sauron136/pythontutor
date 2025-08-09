#!/usr/bin/env python3
"""
Interactive Python Learning Shell
A command-line based Python tutor with integrated practice exercises
"""

import os
import sys
import json
import subprocess
import tempfile
import importlib.util
import importlib.resources
from typing import Dict, List, Any
from pathlib import Path

class PythonTutor:
    def __init__(self):
        self.current_lesson = 1
        self.current_exercise = 0
        self.progress_file = Path.home() / ".python_tutor_progress.json"
        self.github_user_file = Path.home() / ".python_tutor_github_user"
        self.lessons_dir = Path(str(importlib.resources.files('python_tutor') / 'lessons'))
        self.projects_dir = Path(str(importlib.resources.files('python_tutor') / 'projects'))
        self.load_progress()
        self.load_github_user()
        
    def load_progress(self):
        """Load student progress from JSON file"""
        try:
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        except FileNotFoundError:
            self.progress = {
                "current_lesson": 1,
                "completed_lessons": [],
                "completed_projects": [],
                "exercise_attempts": {}
            }
    
    def save_progress(self):
        """Save current progress to JSON file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def load_github_user(self):
        """Load GitHub username from file"""
        try:
            with open(self.github_user_file, 'r') as f:
                self.github_username = f.read().strip()
        except FileNotFoundError:
            self.github_username = None
    
    def save_github_user(self, username):
        """Save GitHub username to file"""
        self.github_username = username
        with open(self.github_user_file, 'w') as f:
            f.write(username)
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_banner(self):
        """Display welcome banner"""
        print("=" * 60)
        print("🐍 INTERACTIVE PYTHON TUTOR")
        print("=" * 60)
        print(f"📚 Lesson {self.current_lesson}/30")
        print(f"🏆 Projects Completed: {len(self.progress['completed_projects'])}/30")
        if self.github_username:
            print(f"👤 GitHub: {self.github_username}")
        print("=" * 60)
    
    def show_lesson_content(self, lesson_num: int):
        """Display lesson content"""
        lesson_file = self.lessons_dir / f"lesson_{lesson_num:02d}" / "content.md"
        
        if not lesson_file.exists():
            print(f"❌ Lesson {lesson_num} not found!")
            return False
            
        with open(lesson_file, 'r') as f:
            content = f.read()
        
        print("\n📖 LESSON CONTENT")
        print("-" * 40)
        print(content)
        print("-" * 40)
        return True
    
    def load_exercises(self, lesson_num: int) -> List[Dict]:
        """Load exercises for a lesson"""
        exercise_file = self.lessons_dir / f"lesson_{lesson_num:02d}" / "exercises.json"
        
        try:
            with open(exercise_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def validate_code(self, code: str, expected_vars: Dict[str, Any] = None, 
                     expected_output: str = None) -> tuple:
        """Validate student's code"""
        try:
            namespace = {}
            exec(code, namespace)
            
            if expected_vars:
                for var_name, expected_value in expected_vars.items():
                    if var_name not in namespace:
                        return False, f"❌ Variable '{var_name}' not found. Did you create it?"
                    
                    actual_value = namespace[var_name]
                    if isinstance(expected_value, type):
                        if not isinstance(actual_value, expected_value):
                            return False, f"❌ Variable '{var_name}' should be of type {expected_value.__name__}"
                    elif expected_value == "str" and not isinstance(actual_value, str):
                        return False, f"❌ Variable '{var_name}' should be a string"
                    elif expected_value == "int" and not isinstance(actual_value, int):
                        return False, f"❌ Variable '{var_name}' should be an integer"
                    elif expected_value == "float" and not isinstance(actual_value, float):
                        return False, f"❌ Variable '{var_name}' should be a float"
                    elif expected_value == "bool" and not isinstance(actual_value, bool):
                        return False, f"❌ Variable '{var_name}' should be a boolean"
            
            if expected_output:
                pass
                
            return True, "✅ Excellent! You got it right!"
            
        except Exception as e:
            return False, f"❌ Error in your code: {str(e)}"
    
    def run_exercise_session(self, lesson_num: int):
        """Run interactive exercise session"""
        exercises = self.load_exercises(lesson_num)
        
        if not exercises:
            print("❌ No exercises found for this lesson!")
            return
        
        print("\n🎯 YOUR TURN!")
        print("Let's practice what you just learned...")
        print("Type your Python code and press Enter twice when done.")
        print("Type 'hint' for a hint, 'skip' to skip, 'quit' to exit.\n")
        
        for i, exercise in enumerate(exercises, 1):
            print(f"\n📝 Exercise {i}/{len(exercises)}")
            print("-" * 30)
            print(exercise["prompt"])
            
            if "example" in exercise:
                print(f"💡 Example: {exercise['example']}")
            
            attempts = 0
            max_attempts = 3
            
            while attempts < max_attempts:
                print(f"\n[Attempt {attempts + 1}/{max_attempts}]")
                print(">>> ", end="")
                
                lines = []
                while True:
                    line = input()
                    if line.strip() == "":
                        break
                    if line.strip().lower() in ['hint', 'skip', 'quit']:
                        break
                    lines.append(line)
                
                user_input = '\n'.join(lines).strip()
                
                if user_input.lower() == 'hint':
                    if "hint" in exercise:
                        print(f"💡 Hint: {exercise['hint']}")
                    else:
                        print("💡 Hint: Remember the lesson content above!")
                    continue
                elif user_input.lower() == 'skip':
                    print("⏭️ Skipping this exercise...")
                    break
                elif user_input.lower() == 'quit':
                    return False
                
                success, message = self.validate_code(
                    user_input, 
                    exercise.get("expected_vars", {}),
                    exercise.get("expected_output")
                )
                
                print(message)
                
                if success:
                    print("🎉 Great job! Moving to the next exercise...\n")
                    break
                else:
                    attempts += 1
                    if attempts < max_attempts:
                        print("💪 Try again!")
                    else:
                        print("⏭️ Don't worry, let's move on. You can always come back to practice!")
        
        print("\n🎊 Exercise session complete!")
        return True
    
    def show_project_prompt(self, lesson_num: int):
        """Show project for the lesson"""
        project_file = self.projects_dir / f"project_{lesson_num:02d}" / "requirements.md"
        
        if not project_file.exists():
            print(f"❌ Project {lesson_num} not found!")
            return False
        
        with open(project_file, 'r') as f:
            content = f.read()
        
        print("\n🚀 PROJECT TIME!")
        print("=" * 50)
        print("Now let's build something with what you've learned!")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        return True
    
    def setup_project_environment(self, lesson_num: int):
        """Set up project workspace with proper scaffolding"""
        project_dir = Path.home() / f"my_projects/project_{lesson_num:02d}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        template_dir = self.projects_dir / f"project_{lesson_num:02d}"
        
        if template_dir.exists():
            import shutil
            
            template_file = template_dir / "template.py"
            if template_file.exists():
                shutil.copy(template_file, project_dir / "main.py")
                print(f"📁 Project workspace created at: {project_dir}")
                print("📄 Project template loaded: main.py")
                
                self.show_implementation_guide(lesson_num)
                
            for file_path in template_dir.glob("*.py"):
                if file_path.name not in ["template.py", "test.py"]:
                    shutil.copy(file_path, project_dir / file_path.name)
                    print(f"📄 Additional file: {file_path.name}")
            
            for file_path in template_dir.glob("*.txt"):
                shutil.copy(file_path, project_dir / file_path.name)
                print(f"📄 Data file: {file_path.name}")
                
        else:
            with open(project_dir / "main.py", 'w') as f:
                f.write('#!/usr/bin/env python3\n')
                f.write('"""\n')
                f.write(f'Project {lesson_num} - [Your Project Title]\n')
                f.write('Author: [Your Name]\n')
                f.write('Description: [Brief description of what this project does]\n')
                f.write('"""\n\n')
                f.write('def main():\n')
                f.write('    """\n')
                f.write('    Main function - implement your solution here\n')
                f.write('    """\n')
                f.write('    pass\n\n')
                f.write('if __name__ == "__main__":\n')
                f.write('    main()\n')
            
            print(f"📁 Project workspace created at: {project_dir}")
            print("📄 Basic template created: main.py")
        
        return project_dir
    
    def show_implementation_guide(self, lesson_num: int):
        """Show students what they need to implement"""
        guide_file = self.projects_dir / f"project_{lesson_num:02d}" / "implementation_guide.md"
        
        if guide_file.exists():
            print("\n🎯 IMPLEMENTATION GUIDE")
            print("=" * 50)
            with open(guide_file, 'r') as f:
                print(f.read())
            print("=" * 50)
    
    def check_ssh_setup(self):
        """Check if SSH is properly configured for GitHub"""
        try:
            result = subprocess.run(
                ["ssh", "-T", "git@github.com", "-o", "ConnectTimeout=5"],
                capture_output=True, text=True, timeout=10
            )
            if "successfully authenticated" in result.stderr:
                return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def setup_github_ssh(self):
        """Guide user through SSH setup"""
        print("\n🔑 GITHUB SSH SETUP")
        print("=" * 40)
        
        if self.check_ssh_setup():
            print("✅ SSH is already configured for GitHub!")
            return True
        
        print("SSH access to GitHub is not configured.")
        print("\nTo set up SSH access:")
        print("1. Generate an SSH key (if you haven't already):")
        print("   ssh-keygen -t ed25519 -C 'your_email@example.com'")
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
        
        return False
    
    def guided_ssh_setup(self):
        """Interactive SSH setup guide"""
        print("\n🚀 Let's set up SSH access step by step...")
        
        # Check if key exists
        ssh_dir = Path.home() / ".ssh"
        ed25519_key = ssh_dir / "id_ed25519"
        rsa_key = ssh_dir / "id_rsa"
        
        if ed25519_key.exists() or rsa_key.exists():
            print("✅ SSH key found!")
            key_file = ed25519_key if ed25519_key.exists() else rsa_key
            pub_key_file = Path(str(key_file) + ".pub")
            
            if pub_key_file.exists():
                print(f"📋 Your public key ({key_file.name}):")
                with open(pub_key_file, 'r') as f:
                    print(f.read().strip())
        else:
            print("🔧 No SSH key found. Let's create one...")
            email = input("Enter your GitHub email: ")
            if not email:
                print("❌ Email is required.")
                return False
            
            try:
                subprocess.run([
                    "ssh-keygen", "-t", "ed25519", "-C", email,
                    "-f", str(ed25519_key), "-N", ""
                ], check=True)
                print("✅ SSH key generated!")
                
                with open(str(ed25519_key) + ".pub", 'r') as f:
                    print("📋 Your public key:")
                    print(f.read().strip())
            except subprocess.CalledProcessError:
                print("❌ Failed to generate SSH key.")
                return False
        
        print("\n🌐 Now add this key to GitHub:")
        print("1. Go to: https://github.com/settings/keys")
        print("2. Click 'New SSH key'")
        print("3. Paste the key above")
        print("4. Give it a title and click 'Add SSH key'")
        
        input("\nPress Enter after adding the key to GitHub...")
        
        if self.check_ssh_setup():
            print("✅ SSH setup successful!")
            return True
        else:
            print("⚠️ SSH test failed. Please check your setup manually.")
            return False
    
    def run_project_mode(self, lesson_num: int):
        """Interactive project development mode"""
        if not self.show_project_prompt(lesson_num):
            return False
        
        project_dir = self.setup_project_environment(lesson_num)
        
        print("\n🛠️ PROJECT DEVELOPMENT MODE")
        print("Available commands:")
        print("  edit    - Open your project in vim")
        print("  run     - Run your project")
        print("  test    - Test your project")
        print("  submit  - Submit and move to next lesson")
        print("  push    - Push to GitHub")
        print("  ssh     - Setup/check SSH for GitHub")
        print("  user    - Set GitHub username")
        print("  help    - Show this help")
        print("  quit    - Exit project mode")
        
        os.chdir(project_dir)
        
        while True:
            command = input(f"\n[Project {lesson_num}] >>> ").strip().lower()
            
            if command == "user":
                username = input("Enter your GitHub username: ").strip()
                if username:
                    self.save_github_user(username)
                    print(f"✅ GitHub username set to: {username}")
                else:
                    print("❌ Username cannot be empty.")
            
            elif command == "ssh":
                self.setup_github_ssh()
            
            elif command == "edit":
                subprocess.run(["vim", "main.py"])
            
            elif command == "run":
                try:
                    result = subprocess.run([sys.executable, "main.py"], 
                                          capture_output=True, text=True)
                    print("🏃 Running your project...")
                    print("=" * 30)
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        print(f"❌ Error: {result.stderr}")
                    print("=" * 30)
                except Exception as e:
                    print(f"❌ Error running project: {e}")
            
            elif command == "test":
                self.run_project_tests(lesson_num)
            
            elif command == "submit":
                if self.submit_project(lesson_num):
                    return True
                
            elif command == "push":
                self.push_to_github_ssh(lesson_num)
                
            elif command == "help":
                print("\n🆘 HELP")
                print("This is your project workspace. Edit main.py to complete the project.")
                print("Use 'ssh' to set up GitHub access, then 'push' to share your work.")
                print("Follow Python best practices:")
                print("- Use descriptive variable names")
                print("- Add docstrings to functions")
                print("- Include comments for complex logic")
                print("- Follow PEP 8 style guidelines")
                
            elif command == "quit":
                os.chdir("..")
                return False
                
            else:
                print("❓ Unknown command. Type 'help' for available commands.")
    
    def run_project_tests(self, lesson_num: int):
        """Run automated tests for the project"""
        test_file = self.projects_dir / f"project_{lesson_num:02d}" / "test.py"
        
        if not test_file.exists():
            print("✅ No automated tests available. Manual review required.")
            return True
        
        try:
            result = subprocess.run([sys.executable, str(test_file)], 
                                  capture_output=True, text=True, cwd=".")
            print("🧪 Running tests...")
            print("=" * 30)
            print(result.stdout)
            if result.stderr:
                print(f"❌ Test errors: {result.stderr}")
            print("=" * 30)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
    
    def submit_project(self, lesson_num: int) -> bool:
        """Submit project and proceed to next lesson"""
        print("🏁 Submitting project...")
        
        tests_passed = self.run_project_tests(lesson_num)
        
        if tests_passed:
            print("✅ All tests passed!")
        else:
            proceed = input("⚠️ Some tests failed. Submit anyway? (y/n): ")
            if proceed.lower() != 'y':
                return False
        
        if self.check_code_quality():
            print("✅ Code quality check passed!")
        else:
            improve = input("⚠️ Consider improving code quality. Submit anyway? (y/n): ")
            if improve.lower() != 'y':
                return False
        
        self.progress["completed_projects"].append(lesson_num)
        self.progress["completed_lessons"].append(lesson_num)
        self.save_progress()
        
        print("🎉 Project submitted successfully!")
        print("🚀 Ready for the next lesson!")
        
        return True
    
    def check_code_quality(self) -> bool:
        """Basic code quality check"""
        try:
            with open("main.py", 'r') as f:
                content = f.read()
            
            has_docstring = '"""' in content or "'''" in content
            has_main_function = "def main(" in content
            has_proper_structure = 'if __name__ == "__main__"' in content
            
            score = 0
            if has_docstring:
                score += 1
                print("✅ Has docstrings")
            else:
                print("⚠️ Consider adding docstrings")
                
            if has_main_function:
                score += 1
                print("✅ Has main function")
            else:
                print("⚠️ Consider using a main function")
                
            if has_proper_structure:
                score += 1
                print("✅ Has proper if __name__ == '__main__' structure")
            else:
                print("⚠️ Consider adding if __name__ == '__main__' guard")
            
            return score >= 2
            
        except Exception as e:
            print(f"❌ Error checking code quality: {e}")
            return True
    
    def push_to_github_ssh(self, lesson_num: int):
        """Push project to GitHub using SSH"""
        if not self.github_username:
            print("❌ GitHub username not set. Use 'user' command first.")
            return
        
        if not self.check_ssh_setup():
            print("❌ SSH not configured for GitHub. Use 'ssh' command first.")
            return
        
        print("📤 PUSH TO GITHUB")
        
        if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
            print("❌ Git is not installed. Please install git and try again.")
            return
        
        repo_name = f"python-tutor-project-{lesson_num:02d}"
        repo_url = f"git@github.com:{self.github_username}/{repo_name}.git"
        
        try:
            if not os.path.exists(".git"):
                print("🔧 Initializing git repository...")
                subprocess.run(["git", "init"], check=True)
                subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
            
            subprocess.run(["git", "add", "."], check=True)
            
            commit_msg = f"Complete project {lesson_num}: {repo_name}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            
            print(f"🚀 Pushing to {repo_url}...")
            result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully pushed to GitHub!")
                print(f"🌐 View your project at: https://github.com/{self.github_username}/{repo_name}")
            else:
                if "does not exist" in result.stderr or "repository not found" in result.stderr:
                    print(f"⚠️ Repository doesn't exist. Creating it...")
                    create_repo = input(f"Create repository '{repo_name}' on GitHub? (y/n): ")
                    if create_repo.lower() == 'y':
                        print("🌐 Please create the repository manually at:")
                        print(f"   https://github.com/new")
                        print(f"   Repository name: {repo_name}")
                        print("   Then run 'push' again.")
                else:
                    print(f"❌ Push failed: {result.stderr}")
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e}")
            print("💡 Make sure your repository exists and you have write permissions.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def main_menu(self):
        """Main interactive menu"""
        while True:
            self.clear_screen()
            self.show_banner()
            
            print("\n📋 MAIN MENU")
            print("1. 📖 Start/Continue Current Lesson")
            print("2. 🎯 Practice Exercises")
            print("3. 🚀 Work on Project")
            print("4. 📊 View Progress")
            print("5. ⚙️ Settings")
            print("6. 🔄 Reset Progress")
            print("7. ❌ Exit")
            
            choice = input("\nChoose an option (1-7): ").strip()
            
            if choice == "1":
                self.run_lesson_flow()
            elif choice == "2":
                lesson_num = int(input("Which lesson exercises? ") or self.current_lesson)
                self.run_exercise_session(lesson_num)
                input("\nPress Enter to continue...")
            elif choice == "3":
                lesson_num = int(input("Which project? ") or self.current_lesson)
                if self.run_project_mode(lesson_num):
                    self.current_lesson += 1
                input("\nPress Enter to continue...")
            elif choice == "4":
                self.show_progress()
                input("\nPress Enter to continue...")
            elif choice == "5":
                self.settings_menu()
            elif choice == "6":
                confirm = input("Are you sure you want to reset all progress? (y/n): ")
                if confirm.lower() == 'y':
                    self.progress = {
                        "current_lesson": 1,
                        "completed_lessons": [],
                        "completed_projects": [],
                        "exercise_attempts": {}
                    }
                    self.current_lesson = 1
                    self.save_progress()
                    print("✅ Progress reset!")
                input("Press Enter to continue...")
            elif choice == "7":
                print("👋 Happy coding! See you next time!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def settings_menu(self):
        """Settings and configuration menu"""
        while True:
            self.clear_screen()
            print("⚙️ SETTINGS")
            print("=" * 30)
            print(f"GitHub Username: {self.github_username or 'Not set'}")
            print(f"SSH Status: {'✅ Configured' if self.check_ssh_setup() else '❌ Not configured'}")
            print()
            print("1. 👤 Set GitHub Username")
            print("2. 🔑 Setup SSH for GitHub")
            print("3. 🧪 Test SSH Connection")
            print("4. 📁 Open Projects Folder")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\nChoose an option (1-5): ").strip()
            
            if choice == "1":
                username = input("Enter your GitHub username: ").strip()
                if username:
                    self.save_github_user(username)
                    print(f"✅ GitHub username set to: {username}")
                input("Press Enter to continue...")
            elif choice == "2":
                self.setup_github_ssh()
                input("Press Enter to continue...")
            elif choice == "3":
                if self.check_ssh_setup():
                    print("✅ SSH connection to GitHub successful!")
                else:
                    print("❌ SSH connection failed. Run SSH setup first.")
                input("Press Enter to continue...")
            elif choice == "4":
                projects_dir = Path.home() / "my_projects"
                print(f"📁 Projects folder: {projects_dir}")
                if projects_dir.exists():
                    try:
                        subprocess.run(["xdg-open", str(projects_dir)])
                    except:
                        print("💡 You can manually navigate to this folder")
                else:
                    print("⚠️ Projects folder doesn't exist yet. Complete a project first!")
                input("Press Enter to continue...")
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def run_lesson_flow(self):
        """Complete lesson flow: content -> exercises -> project"""
        lesson_num = self.current_lesson
        
        if not self.show_lesson_content(lesson_num):
            input("Press Enter to continue...")
            return
        
        input("\nPress Enter when you're ready to practice...")
        
        if self.run_exercise_session(lesson_num):
            ready = input("\n🚀 Ready for the project? (y/n): ").lower()
            if ready == 'y':
                if self.run_project_mode(lesson_num):
                    self.current_lesson += 1
                    print(f"\n🎉 Congratulations! Moving to lesson {self.current_lesson}")
    
    def show_progress(self):
        """Display student progress"""
        print("\n📊 YOUR PROGRESS")
        print("=" * 40)
        print(f"Current Lesson: {self.current_lesson}/30")
        print(f"Completed Lessons: {len(self.progress['completed_lessons'])}/30")
        print(f"Completed Projects: {len(self.progress['completed_projects'])}/30")
        
        if self.progress['completed_lessons']:
            print(f"Lessons Completed: {', '.join(map(str, self.progress['completed_lessons']))}")
        
        if self.progress['completed_projects']:
            print(f"Projects Completed: {', '.join(map(str, self.progress['completed_projects']))}")

def main():
    tutor = PythonTutor()
    try:
        tutor.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please report this issue!")

if __name__ == "__main__":
    main()

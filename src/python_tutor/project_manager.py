"""
Enhanced Project management with template auto-population and vim guidance.

Handles project creation, template setup, testing, and workspace management.
"""

import os
import shutil
import subprocess
import tempfile
import importlib.resources
from pathlib import Path

class ProjectManager:
    """Enhanced project manager with template population and vim guidance"""

    def __init__(self, projects_dir, workspace_dir="~/my_projects"):
        self.projects_dir = Path(projects_dir)
        self.workspace_dir = Path(workspace_dir).expanduser()
        self.workspace_dir.mkdir(exist_ok=True)

    def create_project_workspace(self, lesson_num):
        """Create a project workspace with auto-populated main.py from template"""
        
        project_dir = self.workspace_dir / f"project_{lesson_num:02d}"
        template_dir = self.projects_dir / f"project_{lesson_num:02d}"

        if not template_dir.exists():
            print(f"❌ Project {lesson_num} template not found!")
            return None

        # Create project directory
        project_dir.mkdir(exist_ok=True)

        # Copy template files
        try:
            for item in template_dir.glob("*"):
                if item.is_file():
                    dest = project_dir / item.name
                    
                    # Special handling for template.py -> main.py
                    if item.name == "template.py":
                        dest = project_dir / "main.py"
                        # Only copy if main.py doesn't exist or is empty
                        if not dest.exists() or dest.stat().st_size == 0:
                            shutil.copy2(item, dest)
                            print(f"📄 Created main.py from template")
                    elif not dest.exists():  # Don't overwrite existing work
                        shutil.copy2(item, dest)
                        
                elif item.is_dir() and item.name not in ['.git', '__pycache__']:
                    dest_dir = project_dir / item.name
                    if not dest_dir.exists():
                        shutil.copytree(item, dest_dir)

            print(f"📁 Project workspace created: {project_dir}")
            
            # Show vim hints after workspace creation
            self._show_project_vim_hints()
            
            return project_dir

        except Exception as e:
            print(f"❌ Error creating project workspace: {e}")
            return None

    def _show_project_vim_hints(self):
        """Show vim hints specific to project editing"""
        
        print("\n" + "="*50)
        print("📝 VIM EDITOR GUIDE FOR PROJECTS")
        print("="*50)
        print("🚀 Quick Start:")
        print("  • The template code is already loaded in main.py")
        print("  • Press 'i' to start editing (INSERT mode)")
        print("  • Press 'Esc' when done editing")
        print("  • Type ':wq' to save and exit")
        print("")
        print("✏️ Essential Commands:")
        print("  • 'i' - Start typing at cursor")
        print("  • 'a' - Start typing after cursor") 
        print("  • 'o' - Create new line below and start typing")
        print("  • 'A' - Go to end of line and start typing")
        print("")
        print("🧭 Navigation:")
        print("  • Arrow keys work, or use: h(←) j(↓) k(↑) l(→)")
        print("  • 'w' - Jump to next word")
        print("  • '0' - Go to start of line")
        print("  • '$' - Go to end of line")
        print("  • 'gg' - Go to top of file")
        print("  • 'G' - Go to bottom of file")
        print("")
        print("🔧 Editing:")
        print("  • 'dd' - Delete entire line")
        print("  • 'x' - Delete character at cursor")
        print("  • 'u' - Undo last change")
        print("  • 'Ctrl+r' - Redo")
        print("")
        print("💾 Saving & Exiting:")
        print("  • ':w' - Save file (stay in vim)")
        print("  • ':q' - Quit vim")
        print("  • ':wq' - Save and quit")
        print("  • ':q!' - Quit without saving changes")
        print("")
        print("🆘 Emergency Exit:")
        print("  • If stuck: Press 'Esc' then type ':q!' and press Enter")
        print("="*50)
        print("💡 Remember: Press 'Esc' first, then use : commands!")
        input("Press Enter when you're ready to start coding...")

    def open_project_in_vim_with_guidance(self, project_dir):
        """Open main.py in vim with pre-session guidance"""
        
        main_file = project_dir / "main.py"
        
        # Ensure main.py exists with template content
        if not main_file.exists():
            template_file = self.projects_dir / f"project_{project_dir.name.split('_')[1]}" / "template.py"
            if template_file.exists():
                shutil.copy2(template_file, main_file)
                print("📄 Created main.py from template")
            else:
                # Create a basic main.py if no template exists
                with open(main_file, 'w') as f:
                    f.write('"""Your Python project solution"""\n\n')
                    f.write('def main():\n')
                    f.write('    """Main function - write your code here"""\n')
                    f.write('    pass  # Replace this with your code\n\n')
                    f.write('if __name__ == "__main__":\n')
                    f.write('    main()\n')
                print("📄 Created basic main.py template")
        
        # Show file content preview before opening vim
        try:
            with open(main_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
            print(f"\n📖 Current main.py content preview:")
            print("-" * 40)
            for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
                print(f"{i:2d} | {line}")
            
            if len(lines) > 20:
                print(f"... ({len(lines) - 20} more lines)")
            print("-" * 40)
            
        except Exception as e:
            print(f"⚠️ Could not preview file: {e}")

        # Show vim reminders
        print("\n🎯 EDITING SESSION STARTING")
        print("Remember:")
        print("  • Press 'i' to start typing")
        print("  • Press 'Esc' to stop typing") 
        print("  • Type ':wq' to save and exit")
        print("  • Type ':q!' to exit without saving")
        
        ready = input("\nReady to open vim? (Enter to continue, 'tips' for more help): ").strip()
        if ready.lower() == 'tips':
            self._show_project_vim_hints()

        # Open in vim
        try:
            subprocess.run(["vim", str(main_file)], cwd=project_dir)
            
            # Show post-edit summary
            print("\n✅ Vim session completed!")
            self._show_file_changes_summary(main_file, content if 'content' in locals() else "")
            
        except FileNotFoundError:
            print("❌ Vim not found! Please install vim or use another editor.")
            print("💡 You can edit the file manually at:", main_file)
        except KeyboardInterrupt:
            print("\n⏹️ Vim session cancelled.")

    def _show_file_changes_summary(self, main_file, original_content):
        """Show a summary of changes made to the file"""
        
        try:
            with open(main_file, 'r') as f:
                new_content = f.read()
            
            original_lines = len(original_content.split('\n'))
            new_lines = len(new_content.split('\n'))
            
            print(f"📊 File changes:")
            print(f"  • Original lines: {original_lines}")
            print(f"  • Current lines: {new_lines}")
            print(f"  • Line difference: {new_lines - original_lines:+d}")
            
            # Check if significant changes were made
            if new_content.strip() != original_content.strip():
                print("✅ Changes detected in your code!")
            else:
                print("ℹ️ No changes detected.")
                
        except Exception as e:
            print(f"⚠️ Could not analyze changes: {e}")

    def show_project_info(self, lesson_num):
        """Display comprehensive project information with vim guidance"""
        
        print(f"\n🚀 PROJECT {lesson_num}")
        print("=" * 50)

        # Show requirements
        requirements = self.load_project_requirements(lesson_num)
        print("📋 REQUIREMENTS:")
        print(requirements)
        print("\n" + "=" * 50)

        # Show implementation guide
        guide = self.load_implementation_guide(lesson_num)
        print("📖 IMPLEMENTATION GUIDE:")
        print(guide)
        print("=" * 50)
        
        # Add vim guidance context
        print("\n💡 CODING TIPS:")
        print("  • Your template code will be loaded automatically")
        print("  • Follow the comments and TODO items in the template")
        print("  • Test your code frequently with the 'run' command")
        print("  • Use 'test' command to check if your solution works")

    def load_project_requirements(self, lesson_num):
        """Load project requirements and description"""
        req_file = self.projects_dir / f"project_{lesson_num:02d}" / "requirements.md"
        
        if not req_file.exists():
            return f"Project {lesson_num} requirements not available."

        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error loading requirements: {e}"

    def load_implementation_guide(self, lesson_num):
        """Load step-by-step implementation guide"""
        guide_file = self.projects_dir / f"project_{lesson_num:02d}" / "implementation_guide.md"
        
        if not guide_file.exists():
            return "Implementation guide not available for this project."

        try:
            with open(guide_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error loading implementation guide: {e}"

    def run_project_tests(self, lesson_num, project_dir):
        """Run automated tests for a project"""
        test_file = self.projects_dir / f"project_{lesson_num:02d}" / "test.py"
        project_main = project_dir / "main.py"

        if not test_file.exists():
            print("ℹ️ No automated tests available for this project.")
            return True, "No tests to run"

        if not project_main.exists():
            return False, "❌ main.py not found! Create your solution first."

        try:
            print("🧪 Running automated tests...")
            
            # Copy test file to project directory temporarily
            temp_test = project_dir / "test_temp.py"
            shutil.copy2(test_file, temp_test)

            # Run tests
            result = subprocess.run(
                ["python", str(temp_test)],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Clean up
            temp_test.unlink()

            if result.returncode == 0:
                print("✅ All tests passed!")
                print(f"📄 Test output:\n{result.stdout}")
                return True, result.stdout
            else:
                print("❌ Some tests failed:")
                print(f"📄 Test output:\n{result.stderr}")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            if temp_test.exists():
                temp_test.unlink()
            return False, "❌ Tests timed out (took longer than 30 seconds)"
        except Exception as e:
            if 'temp_test' in locals() and temp_test.exists():
                temp_test.unlink()
            return False, f"❌ Error running tests: {e}"

    def list_student_projects(self):
        """List all projects in student workspace"""
        if not self.workspace_dir.exists():
            return []

        projects = []
        for project_dir in sorted(self.workspace_dir.glob("project_*")):
            if project_dir.is_dir():
                project_num = int(project_dir.name.split('_')[1])
                main_file = project_dir / "main.py"
                projects.append({
                    "number": project_num,
                    "path": project_dir,
                    "has_main": main_file.exists(),
                    "files": list(project_dir.glob("*.py"))
                })

        return projects

    def get_project_status(self, lesson_num):
        """Get current status of a specific project"""
        project_dir = self.workspace_dir / f"project_{lesson_num:02d}"
        
        if not project_dir.exists():
            return "not_started"

        main_file = project_dir / "main.py"
        if not main_file.exists():
            return "created"

        try:
            with open(main_file, 'r') as f:
                content = f.read().strip()
                
            # Check if it's just the template
            if len(content) < 100 or "# TODO" in content or content.count("pass") > 1:
                return "template"
            else:
                return "in_progress"
        except Exception:
            return "created"

    def show_project_progress(self, progress_tracker):
        """Display overview of all project progress"""
        projects = self.list_student_projects()
        completed_projects = progress_tracker.progress.get("completed_projects", [])

        print("\n🚀 PROJECT PORTFOLIO")
        print("=" * 40)
        
        if not projects:
            print("📂 No projects started yet.")
            print("💡 Choose 'Work on Project' from the main menu to begin!")
            return

        for project in projects:
            status_emoji = {
                "not_started": "⚪",
                "created": "🔵", 
                "template": "🟡",
                "in_progress": "🟠",
                "completed": "✅"
            }
            
            if project["number"] in completed_projects:
                status = "completed"
            else:
                status = self.get_project_status(project["number"])

            emoji = status_emoji.get(status, "❓")
            print(f"{emoji} Project {project['number']:02d} - {status.replace('_', ' ').title()}")
            
            if project["files"]:
                file_count = len(project["files"])
                print(f"     📄 {file_count} Python file{'s' if file_count != 1 else ''}")

        print(f"\n📊 Summary: {len(completed_projects)} of {len(projects)} projects completed")

    def cleanup_project_workspace(self, lesson_num):
        """Clean up project workspace (remove generated files)"""
        project_dir = self.workspace_dir / f"project_{lesson_num:02d}"
        
        if not project_dir.exists():
            return

        # Remove common generated files
        cleanup_patterns = [
            "*.pyc",
            "__pycache__",
            "*.log",
            ".pytest_cache",
            "*.tmp"
        ]

        cleaned_files = []
        for pattern in cleanup_patterns:
            for file_path in project_dir.glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                    cleaned_files.append(file_path.name)
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    cleaned_files.append(file_path.name)

        if cleaned_files:
            print(f"🧹 Cleaned up: {', '.join(cleaned_files)}")
        else:
            print("✨ Workspace is already clean!")

    def validate_project_structure(self, lesson_num):
        """Validate that project template has all required files"""
        template_dir = self.projects_dir / f"project_{lesson_num:02d}"
        
        if not template_dir.exists():
            return False, f"Project {lesson_num} template directory not found"

        required_files = ["requirements.md", "template.py"]
        optional_files = ["implementation_guide.md", "test.py"]

        issues = []
        for req_file in required_files:
            if not (template_dir / req_file).exists():
                issues.append(f"Missing required file: {req_file}")

        # Check template.py structure
        template_file = template_dir / "template.py"
        if template_file.exists():
            try:
                with open(template_file, 'r') as f:
                    content = f.read()
                    
                if "def main():" not in content:
                    issues.append("template.py should include a main() function")
                    
                if 'if __name__ == "__main__":' not in content:
                    issues.append("template.py should include if __name__ == '__main__' guard")
                    
            except Exception as e:
                issues.append(f"Could not read template.py: {e}")

        if issues:
            return False, f"Project {lesson_num} issues: " + "; ".join(issues)
        else:
            return True, f"Project {lesson_num} structure is valid"

    def backup_project(self, lesson_num):
        """Create a backup of current project work"""
        import time
        
        project_dir = self.workspace_dir / f"project_{lesson_num:02d}"
        if not project_dir.exists():
            print("❌ No project to backup!")
            return False

        backup_dir = project_dir.parent / f"project_{lesson_num:02d}_backup_{int(time.time())}"
        
        try:
            shutil.copytree(project_dir, backup_dir)
            print(f"💾 Project backed up to: {backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

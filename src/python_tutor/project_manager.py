"""
Project management module for Python Tutor.
Handles project creation, template setup, testing, and workspace management.
"""

import os
import shutil
import subprocess
import importlib.resources
from pathlib import Path


class ProjectManager:
    """Manages student projects, templates, and testing"""
    
    def __init__(self, projects_dir, workspace_dir="~/my_projects"):
        self.projects_dir = Path(projects_dir)
        self.workspace_dir = Path(workspace_dir).expanduser()
        self.workspace_dir.mkdir(exist_ok=True)
    
    def create_project_workspace(self, lesson_num):
        """Create a project workspace for a specific lesson"""
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
                    if not dest.exists():  # Don't overwrite existing work
                        shutil.copy2(item, dest)
                elif item.is_dir() and item.name not in ['.git', '__pycache__']:
                    dest_dir = project_dir / item.name
                    if not dest_dir.exists():
                        shutil.copytree(item, dest_dir)
            
            print(f"📁 Project workspace created: {project_dir}")
            return project_dir
            
        except Exception as e:
            print(f"❌ Error creating project workspace: {e}")
            return None
    
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
    
    def show_project_info(self, lesson_num):
        """Display comprehensive project information"""
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
            if len(content) < 100 or "# TODO" in content or "pass" in content:
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
                print(f"   📄 {file_count} Python file{'s' if file_count != 1 else ''}")
        
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

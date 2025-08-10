"""
Main Interactive Python Tutor application.
Orchestrates all modules to provide a comprehensive learning experience.
"""

import os
import sys
import subprocess
import importlib.resources
from pathlib import Path

# Import our custom modules
from .code_checker import CodeChecker
from .github_integration import GitHubIntegration
from .progress_tracker import ProgressTracker
from .lesson_manager import LessonManager
from .project_manager import ProjectManager
from .utils import Utils, DisplayFormatter


class PythonTutor:
    """Main Interactive Python Tutor application"""
    
    def __init__(self):
        # Initialize core settings
        self.current_lesson = 1
        self.current_exercise = 0
        
        # Set up file paths
        self.progress_file = Path.home() / ".python_tutor_progress.json"
        self.github_user_file = Path.home() / ".python_tutor_github_user"
        
        # Set up resource directories
        self.lessons_dir = Path(str(importlib.resources.files('python_tutor') / 'lessons'))
        self.projects_dir = Path(str(importlib.resources.files('python_tutor') / 'projects'))
        
        # Initialize all modules
        self.progress_tracker = ProgressTracker(self.progress_file)
        self.github_integration = GitHubIntegration(self.github_user_file)
        self.lesson_manager = LessonManager(self.lessons_dir)
        self.project_manager = ProjectManager(self.projects_dir)
        self.code_checker = CodeChecker()
        
        # Load current lesson from progress
        self.current_lesson = self.progress_tracker.get_current_lesson()
    
    def show_header(self):
        """Display application header with current status"""
        Utils.clear_screen()
        
        width = Utils.get_terminal_width()
        print("=" * width)
        print("🐍 INTERACTIVE PYTHON TUTOR".center(width))
        print("=" * width)
        
        # Status information
        completed_lessons = len(self.progress_tracker.progress['completed_lessons'])
        completed_projects = len(self.progress_tracker.progress['completed_projects'])
        
        print(f"📚 Lesson {self.current_lesson}/30")
        print(f"🏆 Projects Completed: {completed_projects}/30")
        
        if self.github_integration.github_username:
            print(f"👤 GitHub: {self.github_integration.github_username}")
        
        print("=" * width)
    
    def main_menu(self):
        """Display and handle main menu"""
        while True:
            self.show_header()
            
            print("📋 MAIN MENU")
            print("1. 📖 Start/Continue Current Lesson")
            print("2. 🎯 Practice Exercises")
            print("3. 🚀 Work on Project") 
            print("4. 📊 View Progress")
            print("5. ⚙️ Settings")
            print("6. 🔄 Reset Progress")
            print("7. ❌ Exit")
            
            choice = input("\nChoose an option (1-7): ").strip()
            
            if choice == "1":
                self.start_current_lesson()
            elif choice == "2":
                self.practice_exercises()
            elif choice == "3":
                self.work_on_project()
            elif choice == "4":
                self.view_progress()
            elif choice == "5":
                self.settings_menu()
            elif choice == "6":
                self.reset_progress()
            elif choice == "7":
                self.exit_application()
                break
            else:
                print("❌ Invalid choice. Please try again.")
                input("Press Enter to continue...")
    
    def start_current_lesson(self):
        """Start or continue the current lesson"""
        if self.progress_tracker.is_lesson_completed(self.current_lesson):
            print(f"✅ Lesson {self.current_lesson} is already completed!")
            choice = Utils.get_user_choice(
                "Would you like to review it or move to the next lesson?",
                ["review", "next", "back"]
            )
            
            if choice == "next":
                if self.current_lesson < 30:
                    self.current_lesson += 1
                    self.progress_tracker.set_current_lesson(self.current_lesson)
                else:
                    print("🎓 Congratulations! You've completed all lessons!")
                    input("Press Enter to continue...")
                    return
            elif choice == "back":
                return
        
        # Show lesson content
        print(f"\n📖 STARTING LESSON {self.current_lesson}")
        if not self.lesson_manager.show_lesson_content(self.current_lesson):
            input("Press Enter to continue...")
            return
        
        # Ask if they want to do exercises
        if input("\nWould you like to practice the exercises? (y/n): ").lower() == 'y':
            if self.lesson_manager.run_interactive_exercises(self.current_lesson, self.progress_tracker):
                # Mark lesson as completed after successful exercises
                self.progress_tracker.complete_lesson(self.current_lesson)
                print(f"🎉 Lesson {self.current_lesson} completed!")
                
                # Suggest moving to project
                if input("Ready to work on the project for this lesson? (y/n): ").lower() == 'y':
                    self.work_on_specific_project(self.current_lesson)
        
        input("Press Enter to continue...")
    
    def practice_exercises(self):
        """Practice exercises from any completed lesson"""
        self.lesson_manager.practice_previous_exercises(self.progress_tracker)
        input("Press Enter to continue...")
    
    def work_on_project(self):
        """Work on projects - show menu of available projects"""
        Utils.clear_screen()
        print("🚀 PROJECT WORKSPACE")
        print("=" * 40)
        
        # Show project portfolio
        self.project_manager.show_project_progress(self.progress_tracker)
        
        print("\nOptions:")
        print("1. 📝 Start/Continue Current Project")
        print("2. 🔍 Choose Specific Project")
        print("3. 📊 View All Projects")
        print("4. 🔙 Back to Main Menu")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            self.work_on_specific_project(self.current_lesson)
        elif choice == "2":
            self.choose_project_menu()
        elif choice == "3":
            self.project_manager.show_project_progress(self.progress_tracker)
            input("Press Enter to continue...")
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice.")
            input("Press Enter to continue...")
    
    def work_on_specific_project(self, project_num):
        """Work on a specific project"""
        # Check if lesson is completed first
        if not self.progress_tracker.is_lesson_completed(project_num):
            if not Utils.confirm_action(f"Lesson {project_num} isn't completed yet. Continue anyway?"):
                return
        
        # Show project information
        self.project_manager.show_project_info(project_num)
        
        # Create or navigate to project workspace
        project_dir = self.project_manager.create_project_workspace(project_num)
        if not project_dir:
            input("Press Enter to continue...")
            return
        
        # Enter project mode
        self.project_mode(project_num, project_dir)
    
    def project_mode(self, project_num, project_dir):
        """Interactive project development mode"""
        original_dir = os.getcwd()
        os.chdir(project_dir)
        
        try:
            print(f"\n🚀 PROJECT {project_num} MODE")
            print(f"📁 Working directory: {project_dir}")
            print("=" * 50)
            
            while True:
                print("\nAvailable commands:")
                print("  edit    - Open your project in vim")
                print("  run     - Run your project")
                print("  test    - Test your project")
                print("  submit  - Submit and move to next lesson")
                print("  push    - Push to GitHub")
                print("  ssh     - Setup/check SSH for GitHub")
                print("  user    - Set GitHub username")
                print("  help    - Show this help")
                print("  quit    - Exit project mode")
                
                command = input(f"\n[Project {project_num}] >>> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "user":
                    username = input("Enter your GitHub username: ").strip()
                    if username:
                        self.github_integration.save_github_user(username)
                        print(f"✅ GitHub username set to: {username}")
                    else:
                        print("❌ Username cannot be empty.")
                
                elif command == "ssh":
                    self.github_integration.setup_github_ssh()
                
                elif command == "edit":
                    subprocess.run(["vim", "main.py"])
                
                elif command == "run":
                    if os.path.exists("main.py"):
                        print("🏃 Running your project...")
                        subprocess.run([sys.executable, "main.py"])
                    else:
                        print("❌ main.py not found! Create your solution first.")
                
                elif command == "test":
                    success, output = self.project_manager.run_project_tests(project_num, project_dir)
                    if success:
                        print("✅ All tests passed! Great work!")
                    else:
                        print("❌ Some tests failed. Keep working on it!")
                
                elif command == "submit":
                    if self.submit_project(project_num, project_dir):
                        break
                
                elif command == "push":
                    self.github_integration.push_to_github_ssh(project_num, project_dir)
                
                elif command == "help":
                    print("\n🆘 PROJECT MODE HELP")
                    print("=" * 30)
                    print("You're working on a coding project. Here's how to succeed:")
                    print("1. Use 'edit' to write your code in main.py")
                    print("2. Use 'run' to test your code")
                    print("3. Use 'test' to run automated tests")
                    print("4. When ready, 'submit' to complete the project")
                    print("5. Use 'push' to share your work on GitHub")
                    print("\n💡 Tips:")
                    print("• Follow Python best practices")
                    print("• Add docstrings to your functions")
                    print("• Use descriptive variable names")
                    print("• Test your code thoroughly")
                
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
        
        finally:
            os.chdir(original_dir)
    
    def submit_project(self, project_num, project_dir):
        """Submit project after quality checks"""
        main_file = project_dir / "main.py"
        
        if not main_file.exists():
            print("❌ No main.py file found! Create your solution first.")
            return False
        
        # Run comprehensive code quality check
        passed, message = self.code_checker.comprehensive_check(main_file, project_num)
        
        if passed:
            self.progress_tracker.complete_project(project_num)
            print(f"🎉 Project {project_num} submitted successfully!")
            
            # Encourage GitHub push
            if self.github_integration.github_username:
                if Utils.confirm_action("Would you like to push this to GitHub?"):
                    self.github_integration.push_to_github_ssh(project_num, project_dir)
            else:
                print("💡 Set up GitHub to share your projects with the world!")
            
            return True
        else:
            if message == "retry":
                # User wants to edit and try again
                subprocess.run(["vim", "main.py"])
                return self.submit_project(project_num, project_dir)
            else:
                print("📚 Keep working on your project and try submitting again!")
                return False
    
    def choose_project_menu(self):
        """Menu to choose a specific project to work on"""
        print("\n🎯 CHOOSE PROJECT")
        print("=" * 30)
        
        completed_lessons = self.progress_tracker.progress.get("completed_lessons", [])
        completed_projects = self.progress_tracker.progress.get("completed_projects", [])
        
        if not completed_lessons:
            print("❌ No lessons completed yet.")
            print("💡 Complete some lessons first to unlock projects!")
            input("Press Enter to continue...")
            return
        
        print("Available projects:")
        for lesson_num in sorted(completed_lessons):
            status = "✅" if lesson_num in completed_projects else "📝"
            print(f"  {status} Project {lesson_num}")
        
        try:
            choice = input("\nEnter project number (or 'back'): ").strip()
            if choice.lower() == 'back':
                return
            
            project_num = int(choice)
            if project_num in completed_lessons:
                self.work_on_specific_project(project_num)
            else:
                print("❌ Complete the lesson first to unlock this project!")
                input("Press Enter to continue...")
        except ValueError:
            print("❌ Please enter a valid project number.")
            input("Press Enter to continue...")
    
    def view_progress(self):
        """Display comprehensive progress information"""
        Utils.clear_screen()
        self.progress_tracker.display_progress_report()
        
        # Show insights and next steps
        insights = self.progress_tracker.get_learning_insights()
        if insights:
            print("\n🧠 LEARNING INSIGHTS")
            print("=" * 30)
            for insight in insights:
                print(f"• {insight}")
        
        print(f"\n{self.progress_tracker.get_next_milestone()}")
        
        input("\nPress Enter to continue...")
    
    def settings_menu(self):
        """Settings and configuration menu"""
        while True:
            Utils.clear_screen()
            print("⚙️ SETTINGS")
            print("=" * 30)
            
            github_status = "✅ Configured" if self.github_integration.check_ssh_setup() else "❌ Not configured"
            print(f"GitHub Username: {self.github_integration.github_username or 'Not set'}")
            print(f"SSH Status: {github_status}")
            
            print("\nOptions:")
            print("1. 👤 Set GitHub Username")
            print("2. 🔑 Setup SSH for GitHub")
            print("3. 🧪 Test SSH Connection")
            print("4. 📊 Export Progress Summary")
            print("5. 🔙 Back to Main Menu")
            
            choice = input("\nChoose option (1-5): ").strip()
            
            if choice == "1":
                username = input("Enter your GitHub username: ").strip()
                if username:
                    self.github_integration.save_github_user(username)
                    print(f"✅ GitHub username set to: {username}")
                else:
                    print("❌ Username cannot be empty.")
                input("Press Enter to continue...")
            
            elif choice == "2":
                self.github_integration.setup_github_ssh()
                input("Press Enter to continue...")
            
            elif choice == "3":
                self.github_integration.test_ssh_connection()
                input("Press Enter to continue...")
            
            elif choice == "4":
                summary_file = self.progress_tracker.export_progress_summary()
                print(f"✅ Progress summary exported!")
                input("Press Enter to continue...")
            
            elif choice == "5":
                break
            
            else:
                print("❌ Invalid choice.")
                input("Press Enter to continue...")
    
    def reset_progress(self):
        """Reset all progress with confirmation"""
        Utils.clear_screen()
        print("🔄 RESET PROGRESS")
        print("=" * 30)
        
        if self.progress_tracker.reset_progress():
            self.current_lesson = 1
            print("🆕 Starting fresh! Good luck on your Python journey!")
        
        input("Press Enter to continue...")
    
    def exit_application(self):
        """Clean exit with progress save"""
        print("\n👋 Thanks for using Interactive Python Tutor!")
        
        # Show quick stats
        completed_lessons = len(self.progress_tracker.progress['completed_lessons'])
        completed_projects = len(self.progress_tracker.progress['completed_projects'])
        
        if completed_lessons > 0 or completed_projects > 0:
            print(f"📊 Session Summary:")
            print(f"   • Lessons completed: {completed_lessons}")
            print(f"   • Projects completed: {completed_projects}")
            print(f"   • Keep up the great work! 🌟")
        
        # Save progress
        self.progress_tracker.save_progress()
        print("\n💾 Progress saved. See you next time!")


def main():
    """Main entry point for the application"""
    try:
        tutor = PythonTutor()
        tutor.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("💡 Please report this issue if it persists.")
        sys.exit(1)


if __name__ == "__main__":
    main()

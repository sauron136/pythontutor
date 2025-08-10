"""
Utility functions and common helpers for Python Tutor.
Contains shared functionality used across multiple modules.
"""

import os
import time
import subprocess
from pathlib import Path


class Utils:
    """Common utility functions used throughout the application"""
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen cross-platform"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    @staticmethod
    def format_time_duration(seconds):
        """Format time duration in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            if minutes > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{hours} hour{'s' if hours != 1 else ''}"
    
    @staticmethod
    def validate_lesson_number(lesson_num_str, max_lessons=30):
        """Validate and convert lesson number input"""
        try:
            lesson_num = int(lesson_num_str)
            if 1 <= lesson_num <= max_lessons:
                return lesson_num, None
            else:
                return None, f"Lesson number must be between 1 and {max_lessons}"
        except ValueError:
            return None, "Please enter a valid number"
    
    @staticmethod
    def get_user_choice(prompt, valid_choices, default=None):
        """Get user input with validation"""
        while True:
            if default:
                user_input = input(f"{prompt} (default: {default}): ").strip()
                if not user_input:
                    return default
            else:
                user_input = input(f"{prompt}: ").strip()
            
            if user_input.lower() in [str(choice).lower() for choice in valid_choices]:
                return user_input.lower()
            
            print(f"❌ Please choose from: {', '.join(map(str, valid_choices))}")
    
    @staticmethod
    def confirm_action(message, require_exact_match=None):
        """Get user confirmation for important actions"""
        if require_exact_match:
            response = input(f"{message} Type '{require_exact_match}' to confirm: ")
            return response == require_exact_match
        else:
            response = input(f"{message} (y/n): ").lower()
            return response in ['y', 'yes']
    
    @staticmethod
    def check_system_requirements():
        """Check if required system tools are available"""
        requirements = {
            "python": ["python3", "--version"],
            "git": ["git", "--version"],
            "vim": ["vim", "--version"]
        }
        
        missing = []
        available = []
        
        for tool, command in requirements.items():
            try:
                result = subprocess.run(command, capture_output=True, timeout=5)
                if result.returncode == 0:
                    available.append(tool)
                else:
                    missing.append(tool)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing.append(tool)
        
        return available, missing
    
    @staticmethod
    def create_progress_bar(current, total, width=20):
        """Create a visual progress bar"""
        if total == 0:
            return "░" * width
        
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        percentage = (current / total) * 100
        return f"[{bar}] {percentage:.1f}%"
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def safe_filename(name):
        """Convert a string to a safe filename"""
        import re
        # Replace spaces and special chars with underscores
        safe = re.sub(r'[^\w\-_.]', '_', name)
        # Remove multiple consecutive underscores
        safe = re.sub(r'_+', '_', safe)
        return safe.strip('_')
    
    @staticmethod
    def get_terminal_width():
        """Get current terminal width, with fallback"""
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 80  # Default fallback
    
    @staticmethod
    def wrap_text(text, width=None):
        """Wrap text to fit terminal width"""
        if width is None:
            width = Utils.get_terminal_width() - 4  # Leave some margin
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    @staticmethod
    def print_boxed_message(message, title=None, width=None):
        """Print a message in a nice box"""
        if width is None:
            width = min(Utils.get_terminal_width() - 4, 60)
        
        lines = message.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        box_width = min(max(max_line_length + 4, width), Utils.get_terminal_width() - 2)
        
        # Top border
        print("┌" + "─" * (box_width - 2) + "┐")
        
        # Title if provided
        if title:
            title_line = f"│ {title.center(box_width - 4)} │"
            print(title_line)
            print("├" + "─" * (box_width - 2) + "┤")
        
        # Content lines
        for line in lines:
            if len(line) > box_width - 4:
                # Wrap long lines
                wrapped_lines = Utils.wrap_text(line, box_width - 4).split('\n')
                for wrapped_line in wrapped_lines:
                    content_line = f"│ {wrapped_line.ljust(box_width - 4)} │"
                    print(content_line)
            else:
                content_line = f"│ {line.ljust(box_width - 4)} │"
                print(content_line)
        
        # Bottom border
        print("└" + "─" * (box_width - 2) + "┘")
    
    @staticmethod
    def print_header(title, subtitle=None, width=None):
        """Print a formatted header"""
        if width is None:
            width = Utils.get_terminal_width()
        
        print("=" * width)
        print(title.center(width))
        if subtitle:
            print(subtitle.center(width))
        print("=" * width)
    
    @staticmethod
    def colorize_text(text, color="default"):
        """Add color codes to text (basic terminal colors)"""
        colors = {
            "default": "",
            "red": "\033[91m",
            "green": "\033[92m", 
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "bold": "\033[1m",
            "underline": "\033[4m"
        }
        
        reset = "\033[0m"
        color_code = colors.get(color.lower(), "")
        
        if color_code:
            return f"{color_code}{text}{reset}"
        return text
    
    @staticmethod
    def show_loading_animation(message, duration=2):
        """Show a simple loading animation"""
        import sys
        
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                sys.stdout.write(f"\r{frame} {message}")
                sys.stdout.flush()
                time.sleep(0.1)
        
        sys.stdout.write(f"\r✅ {message} - Done!\n")
        sys.stdout.flush()
    
    @staticmethod
    def get_directory_info(path):
        """Get information about a directory"""
        path = Path(path)
        
        if not path.exists():
            return None
        
        info = {
            "path": str(path),
            "exists": True,
            "is_dir": path.is_dir(),
            "files": [],
            "subdirs": [],
            "total_size": 0
        }
        
        if path.is_dir():
            try:
                for item in path.iterdir():
                    if item.is_file():
                        size = item.stat().st_size
                        info["files"].append({
                            "name": item.name,
                            "size": size,
                            "size_human": Utils.format_file_size(size)
                        })
                        info["total_size"] += size
                    elif item.is_dir():
                        info["subdirs"].append(item.name)
            except PermissionError:
                info["error"] = "Permission denied"
        
        info["total_size_human"] = Utils.format_file_size(info["total_size"])
        return info
    
    @staticmethod
    def backup_file(file_path, backup_suffix=None):
        """Create a backup of a file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False, "File does not exist"
        
        if backup_suffix is None:
            backup_suffix = f".backup.{int(time.time())}"
        
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            return True, str(backup_path)
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def find_python_files(directory, recursive=True):
        """Find all Python files in a directory"""
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            return []
        
        pattern = "**/*.py" if recursive else "*.py"
        python_files = list(directory.glob(pattern))
        
        return sorted([str(f.relative_to(directory)) for f in python_files])
    
    @staticmethod
    def validate_email(email):
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        return re.match(pattern, email) is not None
    
    @staticmethod
    def truncate_string(text, max_length, suffix="..."):
        """Truncate a string to a maximum length"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def parse_time_input(time_str):
        """Parse various time input formats (e.g., '5m', '1h', '30s')"""
        import re
        
        time_str = time_str.lower().strip()
        
        # Match patterns like: 5m, 1h, 30s, 1h30m
        pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        match = re.match(pattern, time_str)
        
        if not match:
            return None
        
        hours, minutes, seconds = match.groups()
        total_seconds = 0
        
        if hours:
            total_seconds += int(hours) * 3600
        if minutes:
            total_seconds += int(minutes) * 60
        if seconds:
            total_seconds += int(seconds)
        
        return total_seconds if total_seconds > 0 else None


class DisplayFormatter:
    """Helper class for consistent display formatting"""
    
    @staticmethod
    def format_lesson_title(lesson_num, title=None):
        """Format a lesson title consistently"""
        if title:
            return f"📚 Lesson {lesson_num}: {title}"
        else:
            return f"📚 Lesson {lesson_num}"
    
    @staticmethod
    def format_project_title(project_num, title=None):
        """Format a project title consistently"""
        if title:
            return f"🚀 Project {project_num}: {title}"
        else:
            return f"🚀 Project {project_num}"
    
    @staticmethod
    def format_achievement(achievement_key):
        """Format achievement names for display"""
        achievement_names = {
            "first_lesson": "🌱 First Steps",
            "first_project": "🚀 Project Pioneer",
            "lesson_5": "📚 Early Learner",
            "lesson_10": "🎯 Committed Student", 
            "lesson_15": "💪 Persistent Learner",
            "lesson_20": "🌟 Advanced Student",
            "lesson_25": "🔥 Almost There!",
            "lesson_30": "🎓 Python Graduate",
            "week_streak": "📅 Week Warrior",
            "month_streak": "🗓️ Monthly Master",
            "perfect_exercise": "💎 Flawless Victory",
            "no_hints_master": "🧠 Independent Thinker",
            "all_projects": "👑 Project Master",
            "speed_demon": "⚡ Speed Demon",
            "helper": "🤝 Community Helper",
            "explorer": "🔍 Code Explorer"
        }
        
        return achievement_names.get(achievement_key, f"🏆 {achievement_key.replace('_', ' ').title()}")
    
    @staticmethod
    def format_status_indicator(status):
        """Format status with appropriate emoji"""
        status_emojis = {
            "completed": "✅",
            "in_progress": "🟡",
            "not_started": "⚪",
            "failed": "❌",
            "skipped": "⏭️",
            "locked": "🔒"
        }
        
        emoji = status_emojis.get(status, "❓")
        return f"{emoji} {status.replace('_', ' ').title()}"
    
    @staticmethod
    def create_menu_divider(char="=", width=None):
        """Create a menu divider line"""
        if width is None:
            width = Utils.get_terminal_width()
        return char * width
    
    @staticmethod
    def format_code_snippet(code, language="python"):
        """Format code snippet for display"""
        lines = code.strip().split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines, 1):
            line_num = str(i).rjust(2)
            formatted_lines.append(f"{line_num} │ {line}")
        
        return '\n'.join(formatted_lines)

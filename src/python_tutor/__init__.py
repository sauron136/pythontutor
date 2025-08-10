"""
Interactive Python Tutor - A comprehensive Python learning system.

This package provides an interactive command-line environment for learning Python
through structured lessons, hands-on exercises, and practical projects.
"""

__version__ = "0.1.0"
__author__ = "Krystian Nmeze"
__email__ = "krystianmaccs@gmail.com"

# Import main classes for external use
from .tutor import PythonTutor, main
from .code_checker import CodeChecker
from .github_integration import GitHubIntegration
from .progress_tracker import ProgressTracker
from .lesson_manager import LessonManager
from .project_manager import ProjectManager
from .utils import Utils, DisplayFormatter

__all__ = [
    "PythonTutor",
    "main", 
    "CodeChecker",
    "GitHubIntegration",
    "ProgressTracker", 
    "LessonManager",
    "ProjectManager",
    "Utils",
    "DisplayFormatter"
]

"""
Progress tracking and statistics module for Python Tutor.
Handles saving/loading student progress, achievements, and learning analytics.
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta


class ProgressTracker:
    """Manages student progress, achievements, and learning statistics"""
    
    def __init__(self, progress_file):
        self.progress_file = Path(progress_file)
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load student progress from JSON file"""
        default_progress = {
            "current_lesson": 1,
            "completed_lessons": [],
            "completed_projects": [],
            "completed_exercises": {},
            "hints_used": {},
            "attempt_counts": {},
            "start_date": time.time(),
            "last_active": time.time(),
            "total_time_spent": 0,
            "session_start": time.time(),
            "achievements": [],
            "streaks": {
                "current": 0,
                "longest": 0,
                "last_activity": None
            }
        }
        
        try:
            with open(self.progress_file, 'r') as f:
                saved_progress = json.load(f)
                # Merge with defaults to handle new fields
                default_progress.update(saved_progress)
                return default_progress
        except FileNotFoundError:
            return default_progress
        except json.JSONDecodeError:
            print("⚠️ Progress file corrupted. Starting fresh.")
            return default_progress
    
    def save_progress(self):
        """Save current progress to JSON file"""
        # Update session time
        if 'session_start' in self.progress:
            session_time = time.time() - self.progress['session_start']
            self.progress['total_time_spent'] += session_time
        
        self.progress['last_active'] = time.time()
        self.progress['session_start'] = time.time()
        
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save progress: {e}")
    
    def complete_lesson(self, lesson_num):
        """Mark a lesson as completed and update achievements"""
        if lesson_num not in self.progress["completed_lessons"]:
            self.progress["completed_lessons"].append(lesson_num)
            self.progress["current_lesson"] = max(self.progress["current_lesson"], lesson_num + 1)
            
            # Update streak
            self._update_streak()
            
            # Check for achievements
            self._check_lesson_achievements(lesson_num)
            
            self.save_progress()
    
    def complete_project(self, project_num):
        """Mark a project as completed"""
        if project_num not in self.progress["completed_projects"]:
            self.progress["completed_projects"].append(project_num)
            
            # Update streak
            self._update_streak()
            
            # Check for achievements
            self._check_project_achievements(project_num)
            
            self.save_progress()
    
    def complete_exercise(self, lesson_num, exercise_num, attempts=1, hints_used=0):
        """Record exercise completion with attempt and hint tracking"""
        lesson_key = str(lesson_num)
        
        if lesson_key not in self.progress["completed_exercises"]:
            self.progress["completed_exercises"][lesson_key] = []
        
        if exercise_num not in self.progress["completed_exercises"][lesson_key]:
            self.progress["completed_exercises"][lesson_key].append(exercise_num)
        
        # Track attempts and hints
        exercise_key = f"{lesson_num}_{exercise_num}"
        self.progress["attempt_counts"][exercise_key] = attempts
        self.progress["hints_used"][exercise_key] = hints_used
        
        # Check for achievements
        self._check_exercise_achievements(lesson_num, exercise_num, attempts, hints_used)
        
        self.save_progress()
    
    def _update_streak(self):
        """Update daily activity streak"""
        today = datetime.now().date()
        last_activity = self.progress["streaks"].get("last_activity")
        
        if last_activity:
            last_date = datetime.fromisoformat(last_activity).date()
            days_diff = (today - last_date).days
            
            if days_diff == 1:
                # Consecutive day
                self.progress["streaks"]["current"] += 1
            elif days_diff > 1:
                # Streak broken
                self.progress["streaks"]["current"] = 1
            # Same day = no change
        else:
            # First activity
            self.progress["streaks"]["current"] = 1
        
        # Update longest streak
        current_streak = self.progress["streaks"]["current"]
        if current_streak > self.progress["streaks"]["longest"]:
            self.progress["streaks"]["longest"] = current_streak
        
        self.progress["streaks"]["last_activity"] = today.isoformat()
    
    def _check_lesson_achievements(self, lesson_num):
        """Check and award lesson-based achievements"""
        achievements = []
        
        # First lesson
        if lesson_num == 1 and "first_lesson" not in self.progress["achievements"]:
            achievements.append("first_lesson")
            print("🏆 Achievement Unlocked: First Steps!")
        
        # Milestone lessons
        milestones = [5, 10, 15, 20, 25, 30]
        for milestone in milestones:
            if (lesson_num == milestone and 
                f"lesson_{milestone}" not in self.progress["achievements"]):
                achievements.append(f"lesson_{milestone}")
                print(f"🏆 Achievement Unlocked: {milestone} Lessons Mastered!")
        
        # Streak achievements
        current_streak = self.progress["streaks"]["current"]
        if current_streak == 7 and "week_streak" not in self.progress["achievements"]:
            achievements.append("week_streak")
            print("🔥 Achievement Unlocked: Week-Long Streak!")
        elif current_streak == 30 and "month_streak" not in self.progress["achievements"]:
            achievements.append("month_streak")
            print("🔥 Achievement Unlocked: Month-Long Dedication!")
        
        self.progress["achievements"].extend(achievements)
    
    def _check_project_achievements(self, project_num):
        """Check and award project-based achievements"""
        achievements = []
        
        # First project
        if project_num == 1 and "first_project" not in self.progress["achievements"]:
            achievements.append("first_project")
            print("🚀 Achievement Unlocked: First Project Complete!")
        
        # All projects completed
        if len(self.progress["completed_projects"]) == 30 and "all_projects" not in self.progress["achievements"]:
            achievements.append("all_projects")
            print("🎓 Achievement Unlocked: Python Master!")
        
        self.progress["achievements"].extend(achievements)
    
    def _check_exercise_achievements(self, lesson_num, exercise_num, attempts, hints_used):
        """Check for exercise-specific achievements"""
        achievements = []
        
        # Perfect exercise (no hints, first try)
        if attempts == 1 and hints_used == 0:
            if "perfect_exercise" not in self.progress["achievements"]:
                achievements.append("perfect_exercise")
                print("💎 Achievement Unlocked: Flawless Victory!")
        
        # Problem solver (completed without hints)
        if hints_used == 0 and "no_hints_master" not in self.progress["achievements"]:
            # Check if they've completed 10 exercises without hints
            no_hint_count = sum(1 for key, hints in self.progress["hints_used"].items() 
                               if hints == 0)
            if no_hint_count >= 10:
                achievements.append("no_hints_master")
                print("🧠 Achievement Unlocked: Independent Thinker!")
        
        self.progress["achievements"].extend(achievements)
    
    def get_statistics(self):
        """Generate comprehensive learning statistics"""
        total_lessons = 30
        total_projects = 30
        
        completed_lessons = len(self.progress["completed_lessons"])
        completed_projects = len(self.progress["completed_projects"])
        
        # Calculate time spent
        total_time = self.progress.get("total_time_spent", 0)
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        
        # Calculate learning pace
        days_active = len(set(
            datetime.fromtimestamp(lesson_time).date().isoformat()
            for lesson_time in [self.progress.get("start_date", time.time())]
        ))
        
        # Exercise statistics
        total_exercises = sum(len(exercises) for exercises in self.progress["completed_exercises"].values())
        total_attempts = sum(self.progress["attempt_counts"].values())
        total_hints = sum(self.progress["hints_used"].values())
        
        avg_attempts = total_attempts / max(total_exercises, 1)
        
        return {
            "lessons": {
                "completed": completed_lessons,
                "total": total_lessons,
                "percentage": (completed_lessons / total_lessons) * 100
            },
            "projects": {
                "completed": completed_projects,
                "total": total_projects,
                "percentage": (completed_projects / total_projects) * 100
            },
            "time": {
                "total_hours": hours,
                "total_minutes": minutes,
                "days_active": days_active
            },
            "exercises": {
                "completed": total_exercises,
                "average_attempts": avg_attempts,
                "hints_used": total_hints
            },
            "streaks": self.progress["streaks"],
            "achievements": self.progress["achievements"]
        }
    
    def display_progress_report(self):
        """Display a formatted progress report"""
        stats = self.get_statistics()
        
        print("\n📊 YOUR LEARNING PROGRESS")
        print("=" * 50)
        
        # Lessons progress
        lesson_progress = "█" * int(stats["lessons"]["percentage"] // 10)
        lesson_progress += "░" * (10 - int(stats["lessons"]["percentage"] // 10))
        print(f"📚 Lessons: {stats['lessons']['completed']}/{stats['lessons']['total']} "
              f"[{lesson_progress}] {stats['lessons']['percentage']:.1f}%")
        
        # Projects progress
        project_progress = "█" * int(stats["projects"]["percentage"] // 10)
        project_progress += "░" * (10 - int(stats["projects"]["percentage"] // 10))
        print(f"🚀 Projects: {stats['projects']['completed']}/{stats['projects']['total']} "
              f"[{project_progress}] {stats['projects']['percentage']:.1f}%")
        
        # Time and engagement
        print(f"\n⏱️ Time Invested: {stats['time']['total_hours']}h {stats['time']['total_minutes']}m")
        print(f"📅 Days Active: {stats['time']['days_active']}")
        print(f"🔥 Current Streak: {stats['streaks']['current']} days")
        print(f"🏆 Longest Streak: {stats['streaks']['longest']} days")
        
        # Exercise performance
        print(f"\n🎯 Exercises Completed: {stats['exercises']['completed']}")
        print(f"📈 Average Attempts: {stats['exercises']['average_attempts']:.1f}")
        print(f"💡 Hints Used: {stats['exercises']['hints_used']}")
        
        # Achievements
        if stats["achievements"]:
            print(f"\n🏆 Achievements Unlocked: {len(stats['achievements'])}")
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
                "all_projects": "👑 Project Master"
            }
            
            for achievement in stats["achievements"][-5:]:  # Show last 5
                name = achievement_names.get(achievement, f"🏆 {achievement}")
                print(f"   {name}")
        
        print("=" * 50)
    
    def reset_progress(self):
        """Reset all progress (with confirmation)"""
        print("⚠️ WARNING: This will delete ALL your progress!")
        print("   • Completed lessons and projects")
        print("   • Exercise attempts and achievements") 
        print("   • Time tracking and streaks")
        
        confirm1 = input("\nAre you absolutely sure? Type 'RESET' to confirm: ")
        if confirm1 != 'RESET':
            print("❌ Reset cancelled.")
            return False
        
        confirm2 = input("Last chance! Type 'YES DELETE EVERYTHING' to proceed: ")
        if confirm2 != 'YES DELETE EVERYTHING':
            print("❌ Reset cancelled.")
            return False
        
        # Create fresh progress
        self.progress = {
            "current_lesson": 1,
            "completed_lessons": [],
            "completed_projects": [],
            "completed_exercises": {},
            "hints_used": {},
            "attempt_counts": {},
            "start_date": time.time(),
            "last_active": time.time(),
            "total_time_spent": 0,
            "session_start": time.time(),
            "achievements": [],
            "streaks": {
                "current": 0,
                "longest": 0,
                "last_activity": None
            }
        }
        
        self.save_progress()
        print("✅ Progress reset successfully. Welcome back to the beginning!")
        return True
    
    def get_current_lesson(self):
        """Get the current lesson number"""
        return self.progress.get("current_lesson", 1)
    
    def set_current_lesson(self, lesson_num):
        """Set the current lesson number"""
        self.progress["current_lesson"] = lesson_num
        self.save_progress()
    
    def is_lesson_completed(self, lesson_num):
        """Check if a specific lesson is completed"""
        return lesson_num in self.progress["completed_lessons"]
    
    def is_project_completed(self, project_num):
        """Check if a specific project is completed"""
        return project_num in self.progress["completed_projects"]
    
    def get_completion_percentage(self):
        """Get overall completion percentage"""
        total_items = 60  # 30 lessons + 30 projects
        completed_items = len(self.progress["completed_lessons"]) + len(self.progress["completed_projects"])
        return (completed_items / total_items) * 100
    
    def get_learning_insights(self):
        """Generate insights about learning patterns"""
        insights = []
        
        # Lesson completion rate
        lessons_completed = len(self.progress["completed_lessons"])
        projects_completed = len(self.progress["completed_projects"])
        
        if lessons_completed > projects_completed + 3:
            insights.append("📚 You're great at lessons! Try working on more projects to apply your skills.")
        elif projects_completed > lessons_completed:
            insights.append("🚀 You love building! Make sure to keep up with the lessons for new concepts.")
        
        # Exercise performance
        if self.progress["attempt_counts"]:
            avg_attempts = sum(self.progress["attempt_counts"].values()) / len(self.progress["attempt_counts"])
            if avg_attempts <= 1.5:
                insights.append("🎯 Excellent problem-solving! You get exercises right quickly.")
            elif avg_attempts >= 3:
                insights.append("🤔 Take your time with exercises. Re-reading the lesson might help!")
        
        # Hint usage
        if self.progress["hints_used"]:
            total_hints = sum(self.progress["hints_used"].values())
            total_exercises = len(self.progress["hints_used"])
            hints_per_exercise = total_hints / total_exercises
            
            if hints_per_exercise <= 0.5:
                insights.append("🧠 You're very independent! Great problem-solving skills.")
            elif hints_per_exercise >= 2:
                insights.append("💡 Don't be afraid to experiment! Try solutions before asking for hints.")
        
        # Streak insights
        current_streak = self.progress["streaks"]["current"]
        if current_streak >= 7:
            insights.append(f"🔥 Amazing {current_streak}-day streak! Consistency is key to mastering Python.")
        elif current_streak == 0:
            insights.append("📅 Try to code a little bit every day. Even 10 minutes helps!")
        
        return insights
    
    def get_next_milestone(self):
        """Get the next achievement milestone"""
        completed_lessons = len(self.progress["completed_lessons"])
        milestones = [5, 10, 15, 20, 25, 30]
        
        for milestone in milestones:
            if completed_lessons < milestone:
                remaining = milestone - completed_lessons
                return f"🎯 Next milestone: {remaining} lessons until {milestone}-lesson achievement!"
        
        return "🎓 You've mastered all lessons! Amazing work!"
    
    def export_progress_summary(self):
        """Export a summary for sharing or backup"""
        stats = self.get_statistics()
        summary = {
            "completion_date": datetime.now().isoformat(),
            "lessons_completed": stats["lessons"]["completed"],
            "projects_completed": stats["projects"]["completed"],
            "total_time_hours": stats["time"]["total_hours"],
            "achievements_earned": len(stats["achievements"]),
            "longest_streak": stats["streaks"]["longest"]
        }
        
        summary_file = Path.home() / "python_tutor_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Progress summary exported to: {summary_file}")
        return summary_file

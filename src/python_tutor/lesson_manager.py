"""
Lesson management and exercise handling module for Python Tutor.
Handles lesson content display, exercise loading, and interactive practice sessions.
"""

import json
import os
import importlib.resources
from pathlib import Path


class LessonManager:
    """Manages lesson content, exercises, and interactive learning sessions"""
    
    def __init__(self, lessons_dir):
        self.lessons_dir = Path(lessons_dir)
    
    def show_lesson_content(self, lesson_num):
        """Display lesson content from markdown file"""
        lesson_file = self.lessons_dir / f"lesson_{lesson_num:02d}" / "content.md"
        
        if not lesson_file.exists():
            print(f"❌ Lesson {lesson_num} not found!")
            return False
        
        try:
            with open(lesson_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"\n📖 LESSON {lesson_num}")
            print("=" * 50)
            print(content)
            print("=" * 50)
            return True
            
        except Exception as e:
            print(f"❌ Error reading lesson {lesson_num}: {e}")
            return False
    
    def load_exercises(self, lesson_num):
        """Load exercises for a specific lesson"""
        exercise_file = self.lessons_dir / f"lesson_{lesson_num:02d}" / "exercises.json"
        
        if not exercise_file.exists():
            print(f"❌ No exercises found for lesson {lesson_num}")
            return None
        
        try:
            with open(exercise_file, 'r', encoding='utf-8') as f:
                exercises = json.load(f)
            return exercises
        except json.JSONDecodeError as e:
            print(f"❌ Error in exercises file for lesson {lesson_num}: {e}")
            return None
        except Exception as e:
            print(f"❌ Could not load exercises for lesson {lesson_num}: {e}")
            return None
    
    def run_interactive_exercises(self, lesson_num, progress_tracker):
        """Run interactive exercise session for a lesson"""
        exercises = self.load_exercises(lesson_num)
        
        if not exercises:
            print(f"❌ No exercises available for lesson {lesson_num}")
            return False
        
        print(f"\n🎯 LESSON {lesson_num} EXERCISES")
        print("=" * 40)
        print(f"📝 {len(exercises)} exercises to complete")
        print("💡 Type 'hint' for help, 'skip' to move on, 'quit' to exit")
        print("=" * 40)
        
        completed_count = 0
        
        for i, exercise in enumerate(exercises, 1):
            print(f"\n🔢 Exercise {i}/{len(exercises)}")
            print("-" * 30)
            
            if self._run_single_exercise(exercise, lesson_num, i, progress_tracker):
                completed_count += 1
                print("✅ Correct! Well done.")
            else:
                print("⏭️ Moving to next exercise...")
        
        # Summary
        print(f"\n📋 EXERCISE SESSION COMPLETE")
        print(f"✅ Completed: {completed_count}/{len(exercises)}")
        
        if completed_count == len(exercises):
            print("🎉 Perfect score! You've mastered this lesson's concepts.")
        elif completed_count >= len(exercises) * 0.7:
            print("👍 Great work! You understand most concepts.")
        else:
            print("📚 Keep practicing! Review the lesson and try again.")
        
        return completed_count > 0
    
    def _run_single_exercise(self, exercise, lesson_num, exercise_num, progress_tracker):
        """Run a single interactive exercise"""
        question = exercise.get("question", "")
        expected_type = exercise.get("expected_type", "string")
        expected_value = exercise.get("expected_value")
        hints = exercise.get("hints", [])
        explanation = exercise.get("explanation", "")
        
        print(f"\n📝 {question}")
        
        attempts = 0
        hints_used = 0
        max_attempts = 3
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                user_input = input("\n>>> ").strip()
                
                if user_input.lower() == 'quit':
                    return False
                elif user_input.lower() == 'skip':
                    print("⏭️ Skipping this exercise...")
                    return False
                elif user_input.lower() == 'hint':
                    if hints and hints_used < len(hints):
                        print(f"💡 Hint {hints_used + 1}: {hints[hints_used]}")
                        hints_used += 1
                        continue
                    else:
                        print("💡 No more hints available!")
                        continue
                
                # Validate answer
                if self._validate_answer(user_input, expected_type, expected_value):
                    if explanation:
                        print(f"💡 {explanation}")
                    
                    # Record completion
                    progress_tracker.complete_exercise(lesson_num, exercise_num, attempts, hints_used)
                    return True
                else:
                    if attempts < max_attempts:
                        print(f"❌ Not quite right. Try again! ({max_attempts - attempts} attempts left)")
                        if hints and hints_used == 0:
                            print("💭 Type 'hint' if you need help")
                    else:
                        print(f"❌ The correct answer was: {expected_value}")
                        if explanation:
                            print(f"💡 {explanation}")
                        return False
                        
            except KeyboardInterrupt:
                print("\n⏹️ Exercise interrupted.")
                return False
            except Exception as e:
                print(f"❌ Error processing input: {e}")
                continue
        
        return False
    
    def _validate_answer(self, user_input, expected_type, expected_value):
        """Validate user's answer against expected result"""
        try:
            if expected_type == "string":
                return user_input.lower().strip() == str(expected_value).lower().strip()
            
            elif expected_type == "integer":
                return int(user_input) == int(expected_value)
            
            elif expected_type == "float":
                return abs(float(user_input) - float(expected_value)) < 0.01
            
            elif expected_type == "boolean":
                user_bool = user_input.lower() in ['true', '1', 'yes', 'y']
                expected_bool = str(expected_value).lower() in ['true', '1', 'yes', 'y']
                return user_bool == expected_bool
            
            elif expected_type == "list":
                # For list answers, accept various formats
                try:
                    # Try to evaluate as Python literal
                    import ast
                    user_list = ast.literal_eval(user_input)
                    return user_list == expected_value
                except:
                    # Fallback to string comparison
                    return user_input.strip() == str(expected_value)
            
            elif expected_type == "code":
                # For code exercises, execute and compare output
                try:
                    # This is basic - you might want more sophisticated code checking
                    exec_globals = {}
                    exec(user_input, exec_globals)
                    return True  # If it executes without error
                except:
                    return False
            
            else:
                # Default to string comparison
                return user_input.strip() == str(expected_value).strip()
                
        except (ValueError, TypeError):
            return False
    
    def practice_previous_exercises(self, progress_tracker):
        """Allow students to practice exercises from completed lessons"""
        completed_lessons = progress_tracker.progress.get("completed_lessons", [])
        
        if not completed_lessons:
            print("❌ No completed lessons available for practice.")
            print("💡 Complete some lessons first!")
            return
        
        print("\n🎯 PRACTICE MODE")
        print("=" * 30)
        print("Choose a lesson to practice:")
        
        for lesson_num in sorted(completed_lessons):
            exercise_count = len(self.load_exercises(lesson_num) or [])
            print(f"  {lesson_num}. Lesson {lesson_num} ({exercise_count} exercises)")
        
        try:
            choice = input("\nEnter lesson number (or 'back' to return): ").strip()
            
            if choice.lower() == 'back':
                return
            
            lesson_num = int(choice)
            if lesson_num in completed_lessons:
                print(f"\n🔄 Practicing Lesson {lesson_num} exercises...")
                self.run_interactive_exercises(lesson_num, progress_tracker)
            else:
                print("❌ Invalid lesson number or lesson not completed yet.")
                
        except ValueError:
            print("❌ Please enter a valid lesson number.")
    
    def get_lesson_summary(self, lesson_num):
        """Get a brief summary of lesson content"""
        lesson_file = self.lessons_dir / f"lesson_{lesson_num:02d}" / "content.md"
        
        if not lesson_file.exists():
            return f"Lesson {lesson_num} (content not available)"
        
        try:
            with open(lesson_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract first few lines as summary
            lines = content.split('\n')
            title_line = next((line for line in lines if line.startswith('#')), f"Lesson {lesson_num}")
            title = title_line.replace('#', '').strip()
            
            return title
            
        except Exception:
            return f"Lesson {lesson_num}"
    
    def list_available_lessons(self):
        """List all available lessons with their status"""
        lessons = []
        
        for lesson_dir in sorted(self.lessons_dir.glob("lesson_*")):
            if lesson_dir.is_dir():
                lesson_num = int(lesson_dir.name.split('_')[1])
                title = self.get_lesson_summary(lesson_num)
                
                content_exists = (lesson_dir / "content.md").exists()
                exercises_exist = (lesson_dir / "exercises.json").exists()
                
                lessons.append({
                    "number": lesson_num,
                    "title": title,
                    "content_ready": content_exists,
                    "exercises_ready": exercises_exist
                })
        
        return lessons
    
    def validate_lesson_structure(self, lesson_num):
        """Validate that a lesson has all required files"""
        lesson_dir = self.lessons_dir / f"lesson_{lesson_num:02d}"
        
        if not lesson_dir.exists():
            return False, f"Lesson {lesson_num} directory not found"
        
        content_file = lesson_dir / "content.md"
        exercise_file = lesson_dir / "exercises.json"
        
        issues = []
        
        if not content_file.exists():
            issues.append("Missing content.md")
        
        if not exercise_file.exists():
            issues.append("Missing exercises.json")
        else:
            # Validate JSON structure
            try:
                with open(exercise_file, 'r') as f:
                    exercises = json.load(f)
                if not isinstance(exercises, list):
                    issues.append("exercises.json should contain a list")
                else:
                    for i, ex in enumerate(exercises):
                        required_fields = ["question", "expected_value"]
                        missing = [field for field in required_fields if field not in ex]
                        if missing:
                            issues.append(f"Exercise {i+1} missing: {', '.join(missing)}")
            except json.JSONDecodeError:
                issues.append("exercises.json is not valid JSON")
        
        if issues:
            return False, f"Lesson {lesson_num} issues: " + "; ".join(issues)
        else:
            return True, f"Lesson {lesson_num} structure is valid"

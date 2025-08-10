"""
Lesson management and exercise handling module for Python Tutor.
Handles lesson content display, exercise loading, and interactive practice sessions.
"""

import json
import os
import importlib.resources
from pathlib import Path
import io
import sys
from contextlib import redirect_stdout, redirect_stderr


class ExerciseValidator:
    """Generic exercise validation engine that handles all Python concepts"""
    
    def __init__(self, lesson_namespace):
        self.namespace = lesson_namespace
    
    def validate_exercise(self, exercise, user_input=None):
        """Main validation dispatcher - routes to appropriate validator"""
        exercise_type = exercise.get("expected_type", "string")
        
        validators = {
            "string": self._validate_string,
            "integer": self._validate_integer,
            "float": self._validate_float,
            "boolean": self._validate_boolean,
            "list": self._validate_list,
            "code": self._validate_code,
            "code_sequence": self._validate_code_sequence,
            "function_definition": self._validate_function_definition,
            "function_complete": self._validate_function_complete,
            "interactive_code": self._validate_interactive_code,
            "output_match": self._validate_output_match,
            "variable_check": self._validate_variable_check
        }
        
        validator = validators.get(exercise_type, self._validate_string)
        return validator(exercise, user_input)
    
    def _validate_string(self, exercise, user_input):
        expected = exercise.get("expected_value", "")
        return user_input.lower().strip() == str(expected).lower().strip()
    
    def _validate_integer(self, exercise, user_input):
        try:
            expected = exercise.get("expected_value", 0)
            return int(user_input) == int(expected)
        except ValueError:
            return False
    
    def _validate_float(self, exercise, user_input):
        try:
            expected = exercise.get("expected_value", 0.0)
            return abs(float(user_input) - float(expected)) < 0.01
        except ValueError:
            return False
    
    def _validate_boolean(self, exercise, user_input):
        user_bool = user_input.lower() in ['true', '1', 'yes', 'y']
        expected = exercise.get("expected_value", False)
        expected_bool = str(expected).lower() in ['true', '1', 'yes', 'y']
        return user_bool == expected_bool
    
    def _validate_list(self, exercise, user_input):
        try:
            import ast
            user_list = ast.literal_eval(user_input)
            expected = exercise.get("expected_value", [])
            return user_list == expected
        except:
            return user_input.strip() == str(exercise.get("expected_value", ""))
    
    def _validate_code(self, exercise, user_input):
        """Single line of code execution"""
        try:
            exec(user_input, self.namespace)
            return True
        except Exception as e:
            print(f"Code execution error: {e}")
            return False
    
    def _validate_code_sequence(self, exercise, user_input=None):
        """Multi-step code sequence with step-by-step validation"""
        expected_steps = exercise.get("expected_steps", [])
        
        if not expected_steps:
            print("❌ No steps defined for this exercise")
            return False
        
        print(f"This exercise has {len(expected_steps)} steps. Enter each line of code:")
        
        for step_num, expected_step in enumerate(expected_steps, 1):
            while True:
                step_input = input(f"Step {step_num}>>> ").strip()
                
                if step_input.lower() in ['quit', 'skip']:
                    return False
                
                try:
                    exec(step_input, self.namespace)
                    if step_input.strip() == expected_step.strip():
                        print(f"✅ Step {step_num} correct!")
                        break
                    else:
                        print(f"⚠️ Code works but expected: {expected_step}")
                        print("Try the exact format or continue if your solution works.")
                        choice = input("Continue anyway? (y/n): ").strip().lower()
                        if choice == 'y':
                            break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    print("Try again!")
        
        return True
    
    def _validate_function_definition(self, exercise, user_input):
        """Validate function definition without calling it"""
        try:
            exec(user_input, self.namespace)
            func_name = exercise.get("function_name")
            if func_name and func_name in self.namespace:
                if callable(self.namespace[func_name]):
                    print(f"✅ Function '{func_name}' defined successfully!")
                    return True
            return True  # Function executed without error
        except Exception as e:
            print(f"Function definition error: {e}")
            return False
    
    def _validate_function_complete(self, exercise, user_input=None):
        """Complete function exercise: define, test, and validate"""
        expected_steps = exercise.get("expected_steps", [])
        test_calls = exercise.get("test_calls", [])
        func_name = exercise.get("function_name", "")
        
        # Step 1: Get function definition
        print("Define your function (press Enter twice when done):")
        function_lines = []
        while True:
            line = input(">>> ").strip()
            if line == "" and function_lines:
                break
            if line:
                function_lines.append(line)
        
        function_code = '\n'.join(function_lines)
        
        # Step 2: Execute function definition
        try:
            exec(function_code, self.namespace)
            print("✅ Function defined successfully!")
        except Exception as e:
            print(f"❌ Function definition error: {e}")
            return False
        
        # Step 3: Test function calls
        if test_calls:
            print("\n🧪 Testing your function:")
            for i, test in enumerate(test_calls, 1):
                try:
                    # Capture output
                    output_buffer = io.StringIO()
                    with redirect_stdout(output_buffer):
                        result = eval(test["input"], self.namespace)
                    
                    captured_output = output_buffer.getvalue().strip()
                    expected_output = test["expected_output"]
                    
                    # Check if result matches expected
                    if str(result) == str(expected_output):
                        print(f"✅ Test {i}: {test['input']} → {result}")
                    else:
                        print(f"❌ Test {i}: {test['input']} → Got {result}, expected {expected_output}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Test {i} error: {e}")
                    return False
            
            print("🎉 All tests passed!")
        
        return True
    
    def _validate_interactive_code(self, exercise, user_input=None):
        """Interactive code session - students can type multiple lines"""
        print("Interactive coding session. Type 'DONE' when finished:")
        
        code_lines = []
        while True:
            line = input(">>> ")
            if line.strip().upper() == 'DONE':
                break
            code_lines.append(line)
        
        full_code = '\n'.join(code_lines)
        
        try:
            exec(full_code, self.namespace)
            print("✅ Code executed successfully!")
            
            # Optional: Check for specific variables or outputs
            required_vars = exercise.get("required_variables", [])
            for var_name in required_vars:
                if var_name not in self.namespace:
                    print(f"⚠️ Expected variable '{var_name}' not found")
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Code execution error: {e}")
            return False
    
    def _validate_output_match(self, exercise, user_input):
        """Execute code and check if output matches expected"""
        expected_output = exercise.get("expected_output", "")
        
        try:
            # Capture stdout
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                exec(user_input, self.namespace)
            
            actual_output = output_buffer.getvalue().strip()
            return actual_output == expected_output.strip()
        except Exception as e:
            print(f"Code execution error: {e}")
            return False
    
    def _validate_variable_check(self, exercise, user_input):
        """Execute code then check if specific variables exist with correct values"""
        try:
            exec(user_input, self.namespace)
            
            # Check required variables
            required_vars = exercise.get("required_variables", {})
            for var_name, expected_value in required_vars.items():
                if var_name not in self.namespace:
                    print(f"❌ Variable '{var_name}' not found")
                    return False
                
                actual_value = self.namespace[var_name]
                if actual_value != expected_value:
                    print(f"❌ Variable '{var_name}': got {actual_value}, expected {expected_value}")
                    return False
            
            print("✅ All variables correct!")
            return True
        except Exception as e:
            print(f"Code execution error: {e}")
            return False


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
    
    def show_lesson_content_interactive(self, lesson_num, progress_tracker):
        """Display lesson content with interactive reading experience"""
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
            
            # Interactive reading experience
            print("\n📚 Take your time to read through the lesson content above.")
            print("💡 When you're ready, we'll move on to hands-on practice!")
            
            while True:
                choice = input("\nReady for exercises? (y/n/reread): ").strip().lower()
                if choice == 'y':
                    return True
                elif choice == 'n':
                    print("📌 Take your time! Learning at your own pace is important.")
                    return False
                elif choice == 'reread':
                    # Show content again
                    print(f"\n📖 LESSON {lesson_num} (Review)")
                    print("=" * 50)
                    print(content)
                    print("=" * 50)
                else:
                    print("Please enter 'y' for yes, 'n' for no, or 'reread' to see the lesson again.")
            
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
        
        # Create persistent namespace and validator
        lesson_namespace = {}
        validator = ExerciseValidator(lesson_namespace)
        
        print(f"\n🎯 LESSON {lesson_num} EXERCISES")
        print("=" * 40)
        print(f"📝 {len(exercises)} exercises to complete")
        print("💡 Type 'hint' for help, 'skip' to move on, 'quit' to exit")
        print("=" * 40)
        
        completed_count = 0
        
        for i, exercise in enumerate(exercises, 1):
            print(f"\n🔢 Exercise {i}/{len(exercises)}")
            print("-" * 30)
            
            if self._run_single_exercise(exercise, lesson_num, i, progress_tracker, validator):
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
    
    def _run_single_exercise(self, exercise, lesson_num, exercise_num, progress_tracker, validator):
        """Run a single interactive exercise using the generic validator"""
        question = exercise.get("question", "")
        expected_type = exercise.get("expected_type", "string")
        hints = exercise.get("hints", [])
        explanation = exercise.get("explanation", "")
        
        print(f"\n📝 {question}")
        
        # Some exercise types don't need user input (they handle it internally)
        no_input_types = ["code_sequence", "function_complete", "interactive_code"]
        
        if expected_type in no_input_types:
            # These exercise types handle their own input
            try:
                if validator.validate_exercise(exercise):
                    if explanation:
                        print(f"💡 {explanation}")
                    progress_tracker.complete_exercise(lesson_num, exercise_num, 1, 0)
                    return True
                else:
                    return False
            except KeyboardInterrupt:
                print("\n⏹️ Exercise interrupted.")
                return False
        else:
            # Standard input-based exercises
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
                    
                    # Validate answer using generic validator
                    if validator.validate_exercise(exercise, user_input):
                        if explanation:
                            print(f"💡 {explanation}")
                        
                        progress_tracker.complete_exercise(lesson_num, exercise_num, attempts, hints_used)
                        return True
                    else:
                        if attempts < max_attempts:
                            print(f"❌ Not quite right. Try again! ({max_attempts - attempts} attempts left)")
                            if hints and hints_used == 0:
                                print("💭 Type 'hint' if you need help")
                        else:
                            expected_value = exercise.get("expected_value", "")
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
                        required_fields = ["question"]
                        missing = [field for field in required_fields if field not in ex]
                        if missing:
                            issues.append(f"Exercise {i+1} missing: {', '.join(missing)}")
            except json.JSONDecodeError:
                issues.append("exercises.json is not valid JSON")
        
        if issues:
            return False, f"Lesson {lesson_num} issues: " + "; ".join(issues)
        else:
            return True, f"Lesson {lesson_num} structure is valid"
    
    def show_vim_hints(self):
        """Display helpful vim commands for beginners"""
        print("\n📝 VIM QUICK REFERENCE")
        print("=" * 30)
        print("Getting Started:")
        print("  • Press 'i' to enter INSERT mode (start typing)")
        print("  • Press 'Esc' to exit INSERT mode")
        print("  • Type ':wq' to save and quit")
        print("  • Type ':q!' to quit without saving")
        print("\nNavigation:")
        print("  • Arrow keys work in INSERT mode")
        print("  • In normal mode: h(left), j(down), k(up), l(right)")
        print("\nEditing:")
        print("  • 'dd' to delete a line")
        print("  • 'u' to undo")
        print("  • 'Ctrl+r' to redo")
        print("\n💡 Tip: If you get stuck, press 'Esc' then type ':q!' to exit without saving")

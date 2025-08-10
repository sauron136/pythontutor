"""
Code quality checking and analysis module for Python Tutor.
Handles PEP 8 compliance, code structure analysis, and lesson-specific requirements.
"""

import ast
import subprocess
import sys
import os
from pathlib import Path


class CodeChecker:
    """Handles all code quality checking and analysis"""
    
    def __init__(self):
        self.lesson_requirements = {
            1: {
                "concepts": ["variables", "print"],
                "description": "Use variables and print statements"
            },
            2: {
                "concepts": ["input", "variables", "type_conversion"],
                "description": "Get user input and work with different data types"
            },
            3: {
                "concepts": ["if", "elif", "else"],
                "description": "Use conditional statements to control program flow"
            },
            4: {
                "concepts": ["for", "while", "loops"],
                "description": "Use loops to repeat actions"
            },
            5: {
                "concepts": ["functions", "return", "parameters"],
                "description": "Create and use functions with parameters and return values"
            },
            6: {
                "concepts": ["lists", "indexing"],
                "description": "Work with lists and access elements by index"
            },
            7: {
                "concepts": ["dictionaries", "keys", "values"],
                "description": "Use dictionaries to store key-value pairs"
            },
            8: {
                "concepts": ["file_handling", "open", "read", "write"],
                "description": "Read from and write to files"
            },
            # Add more as you create lessons
        }
    
    def check_pep8_compliance(self, file_path):
        """Check if code follows PEP 8 guidelines"""
        try:
            # Try flake8 first (more comprehensive)
            result = subprocess.run([
                'flake8', 
                '--max-line-length=88',
                '--ignore=E203,W503',  # Ignore some overly strict rules
                str(file_path)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return True, "✅ Code follows PEP 8 guidelines!"
            else:
                # Parse and clean up flake8 output
                issues = result.stdout.strip().split('\n')
                clean_issues = []
                
                for issue in issues[:5]:  # Show max 5 issues
                    if issue.strip():
                        parts = issue.split(':', 4)
                        if len(parts) >= 4:
                            line_num = parts[1]
                            col_num = parts[2]
                            message = parts[3].strip()
                            clean_issues.append(f"  • Line {line_num}: {message}")
                
                feedback = "❌ PEP 8 Style Issues:\n" + "\n".join(clean_issues)
                
                if len(issues) > 5:
                    feedback += f"\n  ... and {len(issues) - 5} more issues"
                
                feedback += "\n\n💡 Quick PEP 8 fixes:"
                feedback += "\n  • Use snake_case for variables (my_variable)"
                feedback += "\n  • Add spaces around operators (x + y, not x+y)"
                feedback += "\n  • Keep lines under 88 characters"
                feedback += "\n  • Use 4 spaces for indentation (not tabs)"
                feedback += "\n  • Remove trailing whitespace"
                
                return False, feedback
                
        except FileNotFoundError:
            # Fallback to pycodestyle
            try:
                result = subprocess.run([
                    'pycodestyle', 
                    '--max-line-length=88',
                    str(file_path)
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    return True, "✅ Code style looks good!"
                else:
                    return False, f"❌ Style issues:\n{result.stdout}"
                    
            except FileNotFoundError:
                return True, "⚠️ Style checker not available (install flake8 for feedback)"
        
        except subprocess.TimeoutExpired:
            return True, "⚠️ Style check timed out"
        except Exception as e:
            return True, f"⚠️ Style check failed: {e}"

    def check_code_structure(self, code, lesson_num):
        """Analyze code structure and best practices"""
        try:
            tree = ast.parse(code)
            feedback = []
            score = 0
            total_possible = 0
            
            # Check for functions
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            total_possible += 2
            
            if functions:
                score += 2
                feedback.append("✅ Good: Uses functions to organize code")
                
                # Check for docstrings
                functions_with_docs = [f for f in functions if ast.get_docstring(f)]
                total_possible += 2
                
                if functions_with_docs:
                    score += 2
                    feedback.append("✅ Excellent: Functions have docstrings")
                elif lesson_num >= 5:  # Only expect docstrings after lesson 5
                    feedback.append("💡 Consider adding docstrings: def my_func(): \"\"\"What this function does\"\"\"")
            elif lesson_num >= 5:  # Expect functions after lesson 5
                feedback.append("💡 Consider breaking your code into functions")
            
            # Check for main function pattern
            has_main = any(f.name == 'main' for f in functions)
            if lesson_num >= 8:  # Expect main pattern in later lessons
                total_possible += 2
                if has_main:
                    score += 2
                    feedback.append("✅ Professional: Uses main() function pattern")
                else:
                    feedback.append("💡 Consider using a main() function to organize your code")
            
            # Check for if __name__ == "__main__" guard
            has_main_guard = any(
                isinstance(node, ast.If) and 
                isinstance(node.test, ast.Compare) and
                isinstance(node.test.left, ast.Name) and
                node.test.left.id == '__name__'
                for node in ast.walk(tree)
            )
            
            if lesson_num >= 10:  # Expect main guard in advanced lessons
                total_possible += 1
                if has_main_guard:
                    score += 1
                    feedback.append("✅ Professional: Uses if __name__ == '__main__' guard")
                else:
                    feedback.append("💡 Learn about: if __name__ == '__main__':")
            
            # Check variable naming
            variables = [
                node.id for node in ast.walk(tree) 
                if isinstance(node, ast.Name) and 
                isinstance(node.ctx, ast.Store) and
                not node.id.startswith('_') and 
                node.id not in ['print', 'input', 'len', 'range', 'str', 'int', 'float']
            ]
            
            total_possible += 1
            if variables:
                # Check for descriptive names
                short_vars = [v for v in variables if len(v) <= 2 and v not in ['i', 'j', 'x', 'y']]
                if len(short_vars) <= len(variables) * 0.3:
                    score += 1
                    feedback.append("✅ Good: Uses descriptive variable names")
                else:
                    feedback.append("💡 Try more descriptive names: 'user_name' instead of 'n'")
            
            # Calculate percentage
            if total_possible > 0:
                percentage = (score / total_possible) * 100
                
                if percentage >= 90:
                    overall = "🌟 Outstanding code structure!"
                elif percentage >= 75:
                    overall = "👍 Good code structure"
                elif percentage >= 50:
                    overall = "📈 Decent structure, room for improvement"
                else:
                    overall = "📚 Focus on code organization"
            else:
                overall = "✅ Code structure acceptable for this lesson"
            
            return True, f"{overall}\n" + "\n".join(feedback)
            
        except SyntaxError as e:
            return False, f"❌ Syntax Error on line {e.lineno}: {e.msg}\n💡 Fix the syntax before submitting"
        except Exception as e:
            return True, f"⚠️ Structure analysis failed: {e}"

    def check_lesson_requirements(self, code, lesson_num):
        """Check if code meets lesson-specific requirements"""
        if lesson_num not in self.lesson_requirements:
            return True, "✅ No specific requirements to check"
        
        try:
            tree = ast.parse(code)
            requirements = self.lesson_requirements[lesson_num]["concepts"]
            feedback = []
            missing = []
            found = []
            
            for req in requirements:
                if self._check_concept_usage(tree, code, req):
                    found.append(req)
                    feedback.append(f"✅ Uses {req}")
                else:
                    missing.append(req)
                    feedback.append(f"❌ Missing: {req}")
            
            if not missing:
                overall = f"🎯 Perfect! All lesson {lesson_num} concepts used"
            else:
                overall = f"📚 Missing concepts: {', '.join(missing)}"
            
            return len(missing) == 0, f"{overall}\n" + "\n".join(feedback)
            
        except Exception as e:
            return True, f"⚠️ Requirements check failed: {e}"

    def _check_concept_usage(self, tree, code, concept):
        """Check if a specific programming concept is used in the code"""
        if concept == "variables":
            # Check for variable assignments
            return any(isinstance(node, ast.Assign) for node in ast.walk(tree))
        
        elif concept == "print":
            # Check for print function calls
            return any(
                isinstance(node, ast.Call) and
                isinstance(node.func, ast.Name) and
                node.func.id == 'print'
                for node in ast.walk(tree)
            )
        
        elif concept == "input":
            # Check for input function calls
            return any(
                isinstance(node, ast.Call) and
                isinstance(node.func, ast.Name) and
                node.func.id == 'input'
                for node in ast.walk(tree)
            )
        
        elif concept == "if":
            return any(isinstance(node, ast.If) for node in ast.walk(tree))
        
        elif concept == "elif":
            return any(
                isinstance(node, ast.If) and len(node.orelse) > 0 and
                any(isinstance(alt, ast.If) for alt in node.orelse)
                for node in ast.walk(tree)
            )
        
        elif concept == "else":
            return any(
                isinstance(node, ast.If) and 
                node.orelse and 
                not all(isinstance(alt, ast.If) for alt in node.orelse)
                for node in ast.walk(tree)
            )
        
        elif concept in ["for", "loops"]:
            return any(isinstance(node, ast.For) for node in ast.walk(tree))
        
        elif concept == "while":
            return any(isinstance(node, ast.While) for node in ast.walk(tree))
        
        elif concept == "functions":
            return any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        
        elif concept == "return":
            return any(isinstance(node, ast.Return) for node in ast.walk(tree))
        
        elif concept == "parameters":
            return any(
                isinstance(node, ast.FunctionDef) and len(node.args.args) > 0
                for node in ast.walk(tree)
            )
        
        elif concept == "lists":
            return any(isinstance(node, ast.List) for node in ast.walk(tree))
        
        elif concept == "dictionaries":
            return any(isinstance(node, ast.Dict) for node in ast.walk(tree))
        
        elif concept == "file_handling" or concept == "open":
            return any(
                isinstance(node, ast.Call) and
                isinstance(node.func, ast.Name) and
                node.func.id == 'open'
                for node in ast.walk(tree)
            )
        
        elif concept == "type_conversion":
            conversion_funcs = ['int', 'float', 'str', 'bool']
            return any(
                isinstance(node, ast.Call) and
                isinstance(node.func, ast.Name) and
                node.func.id in conversion_funcs
                for node in ast.walk(tree)
            )
        
        # Default case
        return False

    def run_code_safely(self, file_path, timeout=10):
        """Execute code safely and capture output"""
        try:
            result = subprocess.run(
                [sys.executable, str(file_path)], 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=os.path.dirname(file_path)
            )
            
            if result.returncode == 0:
                return True, "✅ Code runs without errors!", result.stdout
            else:
                return False, f"❌ Runtime error:\n{result.stderr}", result.stderr
                
        except subprocess.TimeoutExpired:
            return False, f"❌ Code took too long to run (>{timeout}s timeout)", ""
        except Exception as e:
            return False, f"❌ Execution failed: {e}", ""

    def comprehensive_check(self, file_path, lesson_num):
        """Run all code quality checks and return detailed report"""
        if not os.path.exists(file_path):
            return False, "❌ File not found!"
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except Exception as e:
            return False, f"❌ Could not read file: {e}"
        
        if not code.strip():
            return False, "❌ File is empty! Write some code first."
        
        print("🔍 Analyzing your code...")
        print("   Checking structure...")
        print("   Validating PEP 8 compliance...")
        print("   Verifying lesson requirements...")
        print("   Testing execution...")
        
        # Run all checks
        structure_ok, structure_msg = self.check_code_structure(code, lesson_num)
        pep8_ok, pep8_msg = self.check_pep8_compliance(file_path)
        requirements_ok, requirements_msg = self.check_lesson_requirements(code, lesson_num)
        execution_ok, execution_msg, output = self.run_code_safely(file_path)
        
        # Display comprehensive report
        self._display_quality_report(
            structure_msg, pep8_msg, requirements_msg, execution_msg,
            structure_ok, pep8_ok, requirements_ok, execution_ok,
            lesson_num
        )
        
        # Determine overall result
        critical_checks = [structure_ok, execution_ok, requirements_ok]
        style_checks = [pep8_ok]
        
        if all(critical_checks + style_checks):
            print(f"\nPERFECT! Your code is ready to submit.")
            return True, "All checks passed!"
        
        elif all(critical_checks):
            print(f"\nGOOD WORK! Code functions correctly with minor style suggestions.")
            submit_anyway = input("\nSubmit anyway? The code works perfectly! (y/n): ").lower()
            return submit_anyway == 'y', "Submitted with style suggestions"
        
        else:
            print(f"\nNEEDS WORK: Please fix the issues above before submitting.")
            retry = input("\nWould you like to edit and try again? (y/n): ").lower()
            return False, "Code needs fixes" if retry != 'y' else "retry"
    
    def _display_quality_report(self, structure_msg, pep8_msg, requirements_msg, 
                               execution_msg, structure_ok, pep8_ok, requirements_ok, 
                               execution_ok, lesson_num):
        """Display a formatted code quality report"""
        print("\n" + "="*60)
        print("CODE QUALITY REPORT")
        print("="*60)
        
        # Execution (most important)
        status = "✅" if execution_ok else "❌"
        print(f"\nEXECUTION {status}")
        print(execution_msg)
        
        # Lesson requirements
        status = "✅" if requirements_ok else "❌"
        print(f"\nLESSON {lesson_num} REQUIREMENTS {status}")
        if lesson_num in self.lesson_requirements:
            print(f"Expected: {self.lesson_requirements[lesson_num]['description']}")
        print(requirements_msg)
        
        # Code structure
        status = "✅" if structure_ok else "❌"
        print(f"\nCODE STRUCTURE {status}")
        print(structure_msg)
        
        # PEP 8 style
        status = "✅" if pep8_ok else "💡"
        print(f"\nPEP 8 STYLE {status}")
        print(pep8_msg)
        
        print("="*60)

    def check_code_structure(self, code, lesson_num):
        """Analyze code structure and best practices"""
        try:
            tree = ast.parse(code)
            feedback = []
            score = 0
            total_possible = 0
            
            # Check for functions (expected after lesson 5)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            if lesson_num >= 5:
                total_possible += 2
                if functions:
                    score += 2
                    feedback.append("Uses functions to organize code")
                    
                    # Check for docstrings in later lessons
                    if lesson_num >= 6:
                        total_possible += 1
                        functions_with_docs = [f for f in functions if ast.get_docstring(f)]
                        if functions_with_docs:
                            score += 1
                            feedback.append("Functions have helpful docstrings")
                        else:
                            feedback.append("Add docstrings: def my_func(): \"\"\"Explain what this does\"\"\"")
                else:
                    feedback.append("Try organizing your code with functions")
            
            # Check for main function pattern (advanced lessons)
            if lesson_num >= 10:
                total_possible += 1
                has_main = any(f.name == 'main' for f in functions)
                if has_main:
                    score += 1
                    feedback.append("Professional: Uses main() function")
                else:
                    feedback.append("Learn about main() function pattern")
            
            # Check variable naming quality
            total_possible += 1
            variables = self._extract_variable_names(tree)
            
            if variables:
                good_names = self._assess_variable_names(variables)
                if good_names:
                    score += 1
                    feedback.append("Uses descriptive variable names")
                else:
                    feedback.append("Use descriptive names: 'user_age' instead of 'a'")
            
            # Overall assessment
            if total_possible > 0:
                percentage = (score / total_possible) * 100
                
                if percentage >= 90:
                    overall = "Exceptional code organization!"
                elif percentage >= 75:
                    overall = "Well-structured code"
                elif percentage >= 50:
                    overall = "Good progress, some improvements possible"
                else:
                    overall = "Keep learning - focus on organization"
            else:
                overall = "Code structure appropriate for this lesson"
            
            return True, f"{overall}\n" + "\n".join(feedback)
            
        except SyntaxError as e:
            return False, f"Syntax Error (line {e.lineno}): {e.msg}"
        except Exception as e:
            return True, f"Structure analysis failed: {e}"

    def _extract_variable_names(self, tree):
        """Extract user-defined variable names from AST"""
        variables = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Skip common built-ins and single letters used appropriately
                        if (target.id not in ['_', '__name__', '__main__'] and 
                            not target.id.startswith('__')):
                            variables.append(target.id)
        return list(set(variables))  # Remove duplicates

    def _assess_variable_names(self, variables):
        """Assess quality of variable names"""
        # Allow common single-letter variables in appropriate contexts
        acceptable_short = ['i', 'j', 'k', 'x', 'y', 'z', 'n']
        
        descriptive_count = 0
        for var in variables:
            if len(var) > 2 or var in acceptable_short:
                descriptive_count += 1
        
        # At least 70% should be descriptive
        return descriptive_count / len(variables) >= 0.7 if variables else True

    def check_lesson_requirements(self, code, lesson_num):
        """Check if code meets specific lesson requirements"""
        if lesson_num not in self.lesson_requirements:
            return True, "No specific requirements for this lesson"
        
        try:
            tree = ast.parse(code)
            requirements = self.lesson_requirements[lesson_num]["concepts"]
            description = self.lesson_requirements[lesson_num]["description"]
            
            feedback = []
            missing = []
            
            print(f"   Checking lesson {lesson_num} concepts...")
            
            for req in requirements:
                if self._check_concept_usage(tree, code, req):
                    feedback.append(f"{req}")
                else:
                    missing.append(req)
                    feedback.append(f"{req}")
            
            if not missing:
                overall = f"Perfect! All required concepts demonstrated"
            else:
                overall = f"Still need to use: {', '.join(missing)}"
                overall += f"\nLesson goal: {description}"
            
            return len(missing) == 0, f"{overall}\n" + "\n".join(feedback)
            
        except Exception as e:
            return True, f"Requirements check failed: {e}"

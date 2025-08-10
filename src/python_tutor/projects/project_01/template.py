"""
Project 1: Personal Information Display
======================================

Your task: Create a program that collects and displays personal information
using the variable concepts you learned in Lesson 1.

Requirements:
- Use string, integer, float, and boolean variables
- Get input from the user 
- Display the information in a formatted way
- Follow Python naming conventions

VIM QUICK REFERENCE:
===================
• Press 'i' to start typing (INSERT mode)
• Press 'Esc' to stop typing  
• Type ':wq' to save and exit
• Type ':q!' to exit without saving

Need help? Use the 'help' command in project mode!
"""

def main():
    """Main function - complete the TODOs below"""
    
    print("🐍 Welcome to My Personal Information Program!")
    print("=" * 50)
    
    # TODO 1: Create variables for personal information
    # Hint: Use input() to get information from the user
    # Example: name = input("What's your name? ")
    
    # String variables (remember to use quotes for default values)
    name = ""  # TODO: Get user's name
    favorite_color = ""  # TODO: Get user's favorite color
    hometown = ""  # TODO: Get user's hometown
    
    # Integer variable  
    age = 0  # TODO: Get user's age (remember to convert with int())
    
    # Float variable
    height = 0.0  # TODO: Get user's height in feet (use float())
    
    # Boolean variable
    is_student = False  # TODO: Ask if they're a student (check for 'yes' or 'y')
    
    # TODO 2: Display the information in a nice format
    # Use print() statements to show all the collected information
    # Try to make it look professional and easy to read
    
    print("\n" + "=" * 50)
    print("📋 YOUR INFORMATION SUMMARY")
    print("=" * 50)
    
    # TODO: Display each piece of information with labels
    # Example: print(f"Name: {name}")
    # Make it look nice and organized!
    
    # TODO 3: Add some calculated information
    # Example: Calculate birth year from age
    # birth_year = 2024 - age
    
    # TODO 4: Display additional formatted information
    # Use f-strings for nice formatting: f"Hello {name}!"
    # Show birth year, describe height in inches too (height * 12)
    
    print("=" * 50)
    print("✨ Thanks for using my program!")

# TODO 5: Add input validation (BONUS - for advanced students)
def get_valid_age():
    """Get a valid age from user input"""
    # This is optional - try to make sure the user enters a valid number
    # You can come back to this after learning about loops and error handling
    pass

def get_yes_no_input(question):
    """Get a yes/no answer and convert to boolean"""
    # This is optional - try to convert 'yes'/'no' answers to True/False
    # You can come back to this after learning about if statements
    pass

# This is the standard Python pattern - don't change this part!
if __name__ == "__main__":
    main()

"""
COMPLETION CHECKLIST:
====================
□ All TODO items completed
□ Program runs without errors  
□ Uses string, int, float, and boolean variables
□ Gets input from the user
□ Displays information in a formatted way
□ Follows Python naming conventions (snake_case)
□ Code is well-commented
□ No syntax errors

TESTING YOUR CODE:
==================
1. Save this file (in vim: press Esc, then type :wq)
2. Run: python main.py
3. Test with different inputs
4. Make sure it handles edge cases
5. Check that output looks professional

VIM TIPS WHILE EDITING:
=======================
Navigation:
• h j k l - move cursor (left/down/up/right)
• w - jump to next word
• 0 - go to start of line
• $ - go to end of line

Editing:
• i - insert at cursor
• a - insert after cursor
• o - new line below and insert
• dd - delete entire line
• u - undo last change

Essential:
• Esc - exit insert mode
• :w - save file
• :wq - save and quit
• :q! - quit without saving

Remember: Always press Esc first before using : commands!
"""

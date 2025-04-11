"""
Written by Misbahur Rahman

Contains all custom exceptions.
"""

from bankapp.util import clear_screen

class InvalidOptionException(Exception):
    def __init__(self, input_option = None):
        message = "Invalid option selected! Choose a valid option"

        if input_option is not None:
            message = f"{input_option} is an invalid option. Choose a valid option"

        super().__init__(message)

class InvalidFormatException(Exception):
    def __init__(self, entity = None):
        message = "Incorrect input format!"

        if entity is not None:
            message = f"Incorrect {entity} format"

        super().__init__(message)

class InvalidCharacterException(Exception):
    def __init__(self, char = None, target_type = None, message = None):
        if message is None:
            message = "Invalid character detected"
            if char is not None and target_type is not None:
                message = f"{char} is an invalid input. Enter a valid {target_type}"
            elif char is not None:
                message = f"{char} is an invalid input. Enter a valid character"
            elif target_type is not None:
                message = f"Invalid input detected. Enter valid {target_type}"

        super().__init__(message)

class NegativeAmountException(Exception):
    def __init__(self):
        message = "Amount cannot be negative"
        super().__init__(message)

class PasswordMismatchException(Exception):
    def __init__(self):
        message = "Passwords doesn't match"
        super().__init__(message)

class InvalidCredentialsException(Exception):
    def __init__(self, username = False, password = False):
        message = "Invalid credentials"

        if username:
            message = "Account doesn't exist! Make sure you have the correct account no"
        elif password:
            message = "Incorrect password"

        super().__init__(message)

class NoUserLoggedInException(Exception):
    def __init__(self, activity = None, raiser = None):
        message = "You must be logged in"
        self.raiser = raiser

        if activity is not None:
            message = f"To {activity}, you must be logged in"

        super().__init__(message)

    def login_prompt(self):
        if self.raiser is not None:
            prompt = input("Would you like to move to the login screen [y/n]: ")
            if prompt.lower()[0] == "y":
                clear_screen()
                self.raiser.interface.login_interface()

class InsufficientFundsException(Exception):
    def __init__(self, amount = None):
        message = "Not enough funds available in your account"

        if amount is not None:
            message = f"Rs {amount} not available in your account"

        super().__init__(message)

class NewBankException(Exception):
    def __init__(self):
        message = "No previous data found. Creating a new bank!"

        super().__init__(message)
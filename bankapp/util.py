"""
Written by Misbahur Rahman

Contains miscellaneous functions to aid in proper functioning of other modules
"""

import hashlib

def validate_name(name: str) -> bool:
    """
    Checks whether the name is a valid alphanumeric string or not

    Args:
        name (str): Name to check

    Returns:
        bool
    """

    return name.replace(" ", "").isalpha()

def format_dob(dob: str) -> tuple:
    """
    Returns individual day, month and year from a date string

    Args:
        dob (str): Date of birth in dd-mm-yyyy format

    Returns:
        tuple
    """

    return tuple(int(i) for i in dob.split('-'))

def display_accounts(accounts: list) -> None:
    """
    Displays the accounts in a formatted manner.

    Args:
        accounts (list of strings): Available account types.
    """

    for idx, item in enumerate(accounts, start = 1):
        print(f"\t{idx}. {item}")

def hash_password(password: str, salt: str | int) -> str:
    """
    Returns the hexadecimal representation of the hashed password
    Args:
        password (str): Input password
        salt (str): Salt added to the input password

    Returns:
        Hexadecimal representation of the hashed password
    """

    salted_password = (password + str(salt))
    return hashlib.sha256(salted_password.encode()).hexdigest()

def validate_account_no(account_no: str) -> bool:
    """
    Check if account_no is a valid account number

    Args:
        account_no (str): Account number of the user.

    Returns:
        bool
    """

    if account_no.isdigit() and len(account_no) == 4:
        return True
    return False

def clear_screen() -> None:
    """
    Clears the output screen

    Returns:
        None
    """

    print("\033c")
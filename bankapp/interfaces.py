"""
Written by Misbahur Rahman

Contains all the user interfaces needed by the bank class.
"""

import sys

from bankapp import exceptions
import pwinput
from bankapp import util


class Interface:
    """
    Handles all user interfaces of the bank.
    """

    def __init__(self, bank):
        """
        Creates an Interface object

        Args:
            bank (Bank): The bank whose interface is handles by this object
        """

        self.bank = bank

    def main_interface(self):
        """
        Defines the main interface of the bank
        """
        util.clear_screen()

        login_status = self.bank.login_status
        main_options = 3
        hidden_options = 4
        total_options = main_options + hidden_options if login_status else main_options
        option = None

        if self.bank.new_bank_status is not None:
            print(self.bank.new_bank_status, '\n')
            self.bank.new_bank_status = None

        print(f"---{self.bank.name} Bank---\n")
        print("Choose an option:")
        print("1. Create an Account")
        print("2. Login")

        if login_status:
            print("3. Display Account Info")
            print("4. Deposit")
            print("5. Withdraw")
            print("6. Logout")

        print("0. Exit")

        print("\nChoose an Option: ", end="")

        try:
            option = input()
            option = int(option)
            if option not in range(0, total_options):
                raise exceptions.InvalidOptionException(option)

            match option:
                case 1:
                    util.clear_screen()
                    self.account_creation_interface()

                case 2:
                    util.clear_screen()
                    self.login_interface()

                case 3:
                    util.clear_screen()
                    self.account_info_interface()

                case 4:
                    util.clear_screen()
                    self.deposit_interface()

                case 5:
                    util.clear_screen()
                    self.withdraw_interface()

                case 6:
                    util.clear_screen()
                    self.logout_interface()

                case 0:
                    util.clear_screen()
                    self.exit_interface()
                    sys.exit(0)

        except ValueError:
            try:
                if option is not None:
                    raise exceptions.InvalidCharacterException(option, "integer")
                raise exceptions.InvalidCharacterException(target_type = "integers")

            except exceptions.InvalidCharacterException as e:
                print()
                print(e.args[0])

        except exceptions.InvalidOptionException as e:
            print()
            print(e.args[0])

        except Exception as e:
            print()
            print(f"An unknown error {e} has occurred")

        finally:
            input()


    def account_creation_interface(self):
        """
        Account creation interfaces.
        """

        try:
            name = input("Enter your name: ")
            dob = input("Enter your date of birth (dd-mm-yyyy): ")

            password = pwinput.pwinput("Enter a password: ")
            confirm_password = pwinput.pwinput("Confirm password: ")

            if password != confirm_password:
                raise exceptions.PasswordMismatchException()

            initial_deposit = input("Enter an initial amount to deposit: ")

            # Ensuring a valid account type is selected
            available_account_types = self.bank.get_account_types(initial_deposit)
            print("Available Account Types:")
            util.display_accounts(available_account_types)
            account_type = input("Enter account type (Sn): ")
            if not (account_type.isdigit() and (len(available_account_types) >= int(account_type) > 0)):
                print(len(available_account_types))
                raise exceptions.InvalidOptionException(account_type)

            acc_no = self.bank.create_account(name, dob, password, initial_deposit, int(account_type))

        except Exception as e:
            print()
            print(e.args[0])
            print("Account creation failed!")
        else:
            print()
            print(f"Account created successfully! Your account number is {acc_no}")

    def login_interface(self):
        """
        Login interface.
        """

        acc_no = input("Enter your account number: ")
        password = pwinput.pwinput("Enter your password: ")
        print()

        try:
            self.bank.login(acc_no, password)

        except exceptions.InvalidFormatException as e:
            print(e.args[0])
            print("Account number must be a 4 digit integer")
        except Exception as e:
            print(e.args[0])
        else:
            print(f"Login successful! Welcome {self.bank.active_account.user_name}")

    def logout_interface(self):
        """
        Logout interface.
        """

        confirm = input("Are you sure you want to logout of your account [y/n]: ")
        print()
        try:
            if confirm.lower()[0] == 'y':
                self.bank.logout()
                print("Logout successful!")
            else:
                print("Logout cancelled!")

        except exceptions.NoUserLoggedInException:
            print("No user logged in")

        except Exception as e:
            print(e.args[0])
            print("An unknown error occurred!")

    def withdraw_interface(self):
        """
        Withdrawal interface
        """

        amount = input("Enter an amount to withdraw: ")
        print()
        try:
            self.bank.withdraw(amount)

        except exceptions.NoUserLoggedInException as e:
            print(e.args[0])
            e.login_prompt()

        except Exception as e:
                print(e.args[0])

        else:
            print(f"Withdrawal of Rs {amount} successful!")

    def deposit_interface(self):
        """
        Deposit interface.
        """

        amount = input("Enter an amount to deposit: ")
        print()
        try:
            self.bank.deposit(amount)

        except exceptions.NoUserLoggedInException as e:
            print(e.args[0])
            e.login_prompt()

        except Exception as e:
                print(e.args[0])

        else:
            print(f"Rs {amount} deposited successful!")

    def exit_interface(self):
        """
        Exit interface
        """
        print("Exiting Bank")
        print("Saving data...")
        self.bank.save_data()
        print("Data saved successfully!")

    def account_info_interface(self):
        """
        Account information interface
        """

        if not self.bank.login_status:
            raise exceptions.NoUserLoggedInException(raiser=self.bank)

        info = self.bank.active_account.account_info_display()
        print(f"{info["account_type"]}")
        print(f"Name: {info["name"]}")
        print(f"Account No: {info["account_no"]}")
        print(f"Balance: {info["balance"]:.2f}")
        print(f"Minimum Balance: {info["minimum_balance"]}")
        print(f"Interest on Balance: {info["interest"] * 100}%")
        print(f"Discount on Loan Interest: {info["discount"] * 100}%")

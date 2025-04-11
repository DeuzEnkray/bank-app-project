"""
Written by Misbahur Rahman

Contains the Bank class, which controls the core logic of maintaining the bank.
"""

from bankapp import exceptions
from bankapp import bank_account
from bankapp.interfaces import Interface
from bankapp import util
import os
import datetime
import threading
import time


class Bank:
    """
    Represents a bank, which handles proper
    communication with bank accounts
    """

    def __init__(self, name: str, day_duration: int = 3):
        """
        Initializes a Bank.

        Args:
            name (str): Name of the bank.
            day_duration (int): Duration of a single day (in seconds)

        Attributes:
            self.new_bank_status (bool): Indicates whether the bank is new or not.
            self.name (str): Name of the bank.
            self.interface (Interface): Handles CLI interface.
            self.active_account (BankAccount): Current active account.
            self.path (str): Path to directory of main file. Helps in loading and saving data.
            self.days_elapsed (int): Number of days the bank has been running for.
            self.__accounts (list): List of accounts handled by the bank.
        """
        self.new_bank_status = None
        self.name = name
        self.interface = Interface(self)
        self.__accounts = []
        self.active_account = None
        base_path = os.path.dirname(os.path.dirname(__file__))
        self.path = os.path.join(base_path, 'data')
        self.days_elapsed = 1

        try:
            self.load_data()

        except exceptions.NewBankException as e:
            self.new_bank_status = e.args[0]

        self.background_tasks(day_duration)

    # Method to show available account types
    @staticmethod
    def get_account_types(amount: int | float) -> list:
        """
        Returns the list of available account types based on amount.
        The possible account types are - Zero Balance Account,
        Value Account and Premium Account

        Args:
             amount(int or float): Available amount in account.

        Returns:
            list: List of available accounts.

        """
        try:
            amount = float(amount)
            if amount < 0:
                raise exceptions.NegativeAmountException()

        except TypeError:
            raise exceptions.InvalidCharacterException(amount, target_type="floats")

        except Exception:
            raise

        else:
            available_types = 1
            account_types = ['Zero Balance Account', 'Value Account', 'Premium Account']
            if amount >= 10000:
                available_types += 1
            if amount >= 50000:
                available_types += 1

            return account_types[:available_types]

    # Method to create account
    def create_account(self, name: str, dob: str, password: str, initial_deposit: int | float, acc_type: int) -> int | None:
        """
        Attempts to create a new bank account by creating a new BankAccount object.

        Args:
            name(str): Name of the user.
            dob(str): Date of birth of the user in dd-mm-yyyy format.
            password(str): Password of the user.
            initial_deposit(int or float): Initial amount deposited by the user.
            acc_type(str): Type of account of the user.

        Returns:
            account_number or None.

        Note:
            None is returned if account creation fails.
            Exception raised by BankAccount are propagated to be handled by Interface.
        """
        acc = None

        try:
            if acc_type not in range(1, 4):
                raise exceptions.InvalidOptionException(acc_type)

            match acc_type:
                case 1:
                    acc = bank_account.ZeroBalanceAccount(name, dob, password, initial_deposit)
                case 2:
                    acc = bank_account.ValueAccount(name, dob, password, initial_deposit)
                case 3:
                    acc = bank_account.PremiumAccount(name, dob, password, initial_deposit)

        except:
            raise
        else:
            self.__accounts.append(acc)
            return acc.account_no

    # Methods to deal with data storage and retrieval
    def save_data(self) -> None:
        """
        Saves account data into a txt file upon exit.

        Returns:
            None
        """

        data = self.encode_data()
        with open(os.path.join(self.path, 'user_data.txt'), 'w') as f:
            f.write(data)

        with open(os.path.join(self.path, 'days.txt'), 'w') as f:
            f.write(str(self.days_elapsed))

    def load_data(self) -> None:
        """
        Loads account data when program starts.

        Returns:
            None
        """

        try:
            with open(os.path.join(self.path, 'user_data.txt'), 'r') as f:
                data = f.readlines()

            count = 0
            decoded_data = self.decode_data(data)

            for i in decoded_data:
                count += 1
                acc_type = i[-1]
                obj = None

                match acc_type:
                    case 1:
                        obj = bank_account.ZeroBalanceAccount.load_account(i)
                    case 2:
                        obj = bank_account.ValueAccount.load_account(i)
                    case 3:
                        obj = bank_account.PremiumAccount.load_account(i)

                self.__accounts.append(obj)

            bank_account.BankAccount.set_available_account_number(count)

        except FileNotFoundError:
            raise exceptions.NewBankException()

        try:
            with open(os.path.join(self.path, 'days.txt'), 'r') as f:
                days = f.read()
                self.days_elapsed = int(days)

        except FileNotFoundError:
            self.days_elapsed = 1

    def encode_data(self) -> str:
        """
        Encodes data into a txt friendly format

        Returns:
            encoded_data (str): txt file friendly string
        """

        data = []
        for i in self.__accounts:
            data.append(i.account_info_save())

        encoded_data = '\n'.join([','.join(i) for i in data])

        return encoded_data

    @staticmethod
    def decode_data(data_strs: list) -> list:
        """
        Decodes txt file strings into program friendly format
        for loading data

        Args:
            data_strs (list): List of strings containing account data

        Returns:
            decoded_data (list): List of program friendly data
        """

        # Data's format: name, dob, adult, acc_no, balance, daily_bal, avg_monthly_bal, pass_hash, acc_type
        decoded_data = []
        for i in data_strs:
            if i[-1] == '\n':
                i = i[:-1]

            curr_data = i.split(',')

            y, m, d = util.format_dob(curr_data[1])
            curr_data[1] = datetime.date(y, m , d)
            curr_data[2] = int(curr_data[2]) == 1
            curr_data[3] = int(curr_data[3])
            curr_data[4] = float(curr_data[4])
            curr_data[5] = float(curr_data[5])
            curr_data[6] = float(curr_data[6])
            curr_data[8] = int(curr_data[8])

            decoded_data.append(curr_data)

        return decoded_data

    # Methods to deal with login/logout
    @property
    def login_status(self) -> bool:
        """
        Returns whether an account is active or not

        Returns:
            bool
        """
        if self.active_account is None:
            return False
        return True

    def login(self, acc_no: str, password: str) -> None:
        """
        Logs a user into their bank account. Raises exceptions
        in case of incorrect account number or passwords

        Args:
            acc_no (str): input account number
            password (str): input password

        Returns:
            None
        """
        if not util.validate_account_no(acc_no):
            raise exceptions.InvalidFormatException("account number")

        for acc in self.__accounts:
            if acc.account_no == int(acc_no):
                input_password_hash = util.hash_password(password, acc.account_no)
                if input_password_hash == acc.password_hash:
                    self.active_account = acc
                    return
                raise exceptions.InvalidCredentialsException(password = True)
        raise exceptions.InvalidCredentialsException(username = True)

    def logout(self) -> None:
        """
        Logs a user out of their bank account.
        If no user is logged in, returns False.

        Returns:
            None
        """
        if self.active_account is not None:
            self.active_account = None
            return
        raise exceptions.NoUserLoggedInException()

    # Methods dealing with transactions
    def withdraw(self, amount:float) -> None:
        """
        Withdraws money from bank account

        Args:
            amount (float): Amount of money to be withdrawn

        Returns:
            None
        """

        if not self.login_status:
            raise exceptions.NoUserLoggedInException("withdraw", self)
        else:
            try:
                amount = float(amount)

            except ValueError:
                raise exceptions.InvalidCharacterException(amount, "Numbers")

            else:
                self.active_account.withdraw(amount)

    def deposit(self, amount):
        """
        Deposits money into the bank account

        Args:
            amount (float): Amount of money to be deposited

        Returns:
            None
        """

        if not self.login_status:
            raise exceptions.NoUserLoggedInException("withdraw", self)
        else:
            try:
                amount = float(amount)

            except ValueError:
                raise exceptions.InvalidCharacterException(amount, "Numbers")

            else:
                self.active_account.deposit(amount)

    # Methods to deal with periodic tasks
    def background_tasks(self, day_duration: int) -> None:
        """
        Creates a thread to execute self.task_cycle()

        Args:
            day_duration (int): Duration of a single day (in seconds)

        Returns:
            None
        """

        bg_thread = threading.Thread(target = self.task_cycle, args = (day_duration,), daemon = True)
        bg_thread.start()

    def task_cycle(self, day_duration: int) -> None:
        """
        Simulates a day. It also executes daily and monthly tasks.

        Args:
            day_duration (int): Duration of a single day (in seconds)

        Returns:
            None
        """

        while True:
            start_time = time.time()

            self.update_daily_amount()
            if self.days_elapsed % 30 == 0:
                self.update_monthly_amount()
                self.interests_penalties()

            self.days_elapsed += 1

            time_elapsed = time.time() - start_time

            time.sleep(max(day_duration - time_elapsed, 0))

    def update_daily_amount(self) -> None:
        """
        Updates the daily balance of each user.

        Returns:
            None
        """

        for acc in self.__accounts:
            acc.update_daily_balance()

    def update_monthly_amount(self) -> None:
        """
        Updates the average monthly balance of each user.

        Returns:
            None
        """

        for acc in self.__accounts:
            acc.update_monthly_balance()

    def interests_penalties(self) -> None:
        """
        Pays out interest or deducts penalties, based on
        whether minimum balance was maintained or not.

        Returns:
            None
        """

        for acc in self.__accounts:
            if acc.avg_monthly_balance >= acc.minimum_balance:
                acc.deposit(acc.avg_monthly_balance * acc.interest / 12)
            else:
                # Ensures that in case of negative monthly balance, no more than allowed
                # penalty amount is deducted

                penalty_percentage = min((acc.minimum_balance - acc.avg_monthly_balance) / acc.minimum_balance, 1)
                penalty_amount = 0.05 * acc.minimum_balance
                acc.withdraw(penalty_amount * penalty_percentage, force = True)


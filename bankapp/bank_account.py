"""
Written by Misbahur Rahman

A core component of bankapp module. It deals with an individual bank account.

Future improvements involve rewriting the code to use multiple inheritance
instead of multiple inheritance.
"""


import datetime
from bankapp import exceptions
from bankapp import util

class BankAccount:
    """
    Represents a single bank account.

    Attributes:
        __available_account_no (int): Current available account number that can be assigned.

    Note:
        Password is hashed using salt + SHA256 encryption. Account number is used as salt.
    """
    __available_account_no = 1000

    def __init__(self, name: str, dob: str, password: str, initial_deposit: float):
        """

        Args:
            name (str): Name of the user.
            dob (str): Date of birth of the user in dd-mm-yyyy format.
            password (str): Raw password of the user.
            initial_deposit (float): Initial money deposited by the user

        Attributes:
            self.name (str): Name of the user.
            self.__account_no (int): Account number of the user.
            self.__password_hash (str): Salt hashed password of the user
            self.__dob (datetime): Date of birth of the user.
            self.__is_adult (bool): States whether the user is adult or not.
            self.__balance (float): Current balance of the user.
            self.__daily_balance (float): Summation of daily balance over the period of one month.
            self.__avg_monthly_balance (float): Average monthly balance of the user.

        Note:
            Password is hashed using SHA256 encryption. Account number is used as salt.
        """

        try:
            # Validating that the name given is a valid alphabet string
            self.name = name
            if not util.validate_name(self.name):
                raise exceptions.InvalidCharacterException(self.name, "string")

            # Validating that the dob is in a correct format
            try:
                d, m, y = util.format_dob(dob)
                self.__dob = datetime.date(y, m, d)
            except ValueError:
                raise exceptions.InvalidFormatException("date")
            except TypeError:
                raise exceptions.InvalidCharacterException(dob, "integers")

            # Checking if the user is a minor or adult
            self.__is_adult = (datetime.date.today() - self.__dob).days / 365 > 18

            try:
                self.__amount = float(initial_deposit)
                if self.__amount < 0:
                    raise exceptions.NegativeAmountException()

            except TypeError:
                raise exceptions.InvalidCharacterException(initial_deposit, "number")
            except Exception:
                raise

            self.__daily_balance = 0
            self.__avg_monthly_balance = 0

            self.__account_no = BankAccount.assign_new_account_no()
            self.__password_hash = util.hash_password(password, str(self.account_no))

        except Exception:
            raise

    @classmethod
    def assign_new_account_no(cls) -> int:
        """
        Returns the current available account number and updates
        the class attributes to ensure every account holder
        gets a unique account number.

        Returns:
            available_account_no (int)
        """
        available_account_no = cls.__available_account_no
        cls.__available_account_no += 1
        return available_account_no

    @classmethod
    def set_available_account_number(cls, extension: int) -> None:
        """
        Updates the class attributes at the time of loading
        data to ensure new accounts receive a valid account
        number.

        Args:
            extension (int): Number by which to increase current available_account_no

        Returns:
            None
        """
        cls.__available_account_no += extension

    @staticmethod
    def load_account(obj, data: list) -> None:
        """
        Creates an account using loaded data.

        Args:
            obj (BankAccount): Bank account whose variables are to be initialized.
            data (list): Data using which variables are initialized

        Returns:
            None
        """

        # Data's format: name, dob, adult, acc_no, balance, daily_bal, avg_monthly_bal, pass_hash

        obj.name = data[0]
        obj.__dob = data[1]
        obj.__is_adult = data[2]
        obj.__account_no = data[3]
        obj.__amount = data[4]
        obj.__daily_balance = data[5]
        obj.__avg_monthly_balance = data[6]
        obj.__password_hash = data[7]

    @property
    def user_name(self) -> str:
        """
        Returns the name of the user.

        Returns:
            str
        """
        return self.name

    @property
    def account_no(self) -> int:
        """
        Returns the account number of the user.

        Returns:
            int
        """

        return self.__account_no

    @property
    def balance(self) -> float:
        """
        Returns the current balance of the user

        Returns:
            float
        """
        return self.__amount

    @property
    def password_hash(self) -> str:
        """
        Returns the hashed password of the user

        Returns:
            str
        """

        return self.__password_hash

    @property
    def avg_monthly_balance(self) -> float:
        """
        Returns the average monthly balance of the user

        Returns:
            float
        """

        return self.__avg_monthly_balance

    def update_daily_balance(self) -> None:
        """
        Updates the daily balance of the user.

        Returns:
            None
        """
        self.__daily_balance += self.balance

    def update_monthly_balance(self) -> None:
        """
        Updates the average monthly balance

        Returns:
            None
        """

        self.__avg_monthly_balance = self.__daily_balance / 30
        self.__daily_balance = 0

    def account_info_save(self) -> list:
        """
        Returns a list of all attributes as string for saving data

        Returns:
            List of attributes
        """
        info = [self.user_name, self.__dob, self.__is_adult, self.account_no, self.balance, self.__daily_balance, self.avg_monthly_balance, self.password_hash]
        info[1] = info[1].strftime('%Y-%m-%d')
        info[2] = 1 if self.__is_adult is True else 0
        for i in range(2, 8):
            info[i] = str(info[i])

        return info

    def account_info_display(self) -> dict:
        """
        Returns a dictionary of relevant attributes for displaying information to user.

        Returns:
            dict
        """

        info = {"name": self.user_name, "account_no": self.account_no, "balance": self.balance}

        return info

    def deposit(self, amount: float) -> None:
        """
        Deposits money to user's account

        Args:
            amount (float): Amount to deposit

        Returns:
            None
        """

        if amount < 0:
            raise exceptions.NegativeAmountException()
        self.__amount += amount

    def withdraw(self, amount: float, force: bool = False) -> None:
        """
        Withdraws money from user's account. Force withdrawal occurs when
        deducting penalties. Force withdrawal can deduct money even if
        enough balance is not available.

        Args:
            amount (float): Money to deduct
            force (bool): Whether withdrawal is forced or not

        Returns:
            None
        """
        if amount < 0:
            raise exceptions.NegativeAmountException()

        if amount > self.balance and not force:
            raise exceptions.InsufficientFundsException(amount)

        self.__amount -= amount

class AccountFunctions:
    """
        Helper class which reduces code redundancy when dealing with
        specific account types, such as ZeroBalanceAccount, ValueAccount, etc.
    """

    account_type: str
    interest: float
    discount: float
    minimum_balance: float
    account_index: int

    @classmethod
    def load_account(cls, data: list) -> BankAccount:
        """
        Creates an object using existing data

        Args:
            data (list): Data with which to create the class

        Returns:
            A subclass of BankAccount
        """

        obj = cls.__new__(cls)
        super(AccountFunctions, cls).load_account(obj, data[:-1])

        return obj

    def account_info_save(self) -> list:
        """
        Returns a list of attributes for saving account information

        Returns:
            list
        """

        info = super().account_info_save()
        info.append(str(self.account_index))
        return info

    def account_info_display(self) -> dict:
        """
        Returns a dictionary of attributes for displaying account info

        Returns:
            dict
        """

        info = {"account_type": self.account_type, "minimum_balance": self.minimum_balance, "interest": self.interest, "discount": self.discount}
        info.update(super().account_info_display())
        return info

class ZeroBalanceAccount(AccountFunctions, BankAccount):
    """
    ZeroBalanceAccount, with minimum balance 0

    Attributes:
        account_type (str): Type of account.
        interest (float): Interest paid on monthly average balance.
        discount (float): Discount on loan interest.
        minimum_balance (float): Minimum balance to maintain.
        account_index (int): Attribute to help when loading or saving account information
    """

    account_type = "Zero Balance Account"
    interest = 0.07
    discount = 0.00
    minimum_balance = 0
    account_index = 1

    def __init__(self, name, dob, password, initial_deposit):
        """
        Creates an object of ZeroBalanceAccount

        Args:
            name (str): Name of the user
            dob (str): Dob of the user in dd-mm-yyyy format
            password (str): Password of the user
            initial_deposit (int or float): Initial deposit of the user
        """
        super().__init__(name, dob, password, initial_deposit)

class ValueAccount(AccountFunctions, BankAccount):
    """
        ValueAccount, with minimum balance 10000

        Attributes:
            account_type (str): Type of account.
            interest (float): Interest paid on monthly average balance.
            discount (float): Discount on loan interest.
            minimum_balance (float): Minimum balance to maintain.
            account_index (int): Attribute to help when loading or saving account information
        """

    account_type = "Value Account"
    interest = 0.085
    discount = 0.10
    minimum_balance = 10000
    account_index = 2

    def __init__(self, name, dob, password, initial_deposit):
        """
        Creates an object of ValueAccount

        Args:
            name (str): Name of the user
            dob (str): Dob of the user in dd-mm-yyyy format
            password (str): Password of the user
            initial_deposit (int or float): Initial deposit of the user
        """
        super().__init__(name, dob, password, initial_deposit)

class PremiumAccount(AccountFunctions, BankAccount):
    """
        PremiumAccount, with minimum balance 50000

        Attributes:
            account_type (str): Type of account.
            interest (float): Interest paid on monthly average balance.
            discount (float): Discount on loan interest.
            minimum_balance (float): Minimum balance to maintain.
            account_index (int): Attribute to help when loading or saving account information
        """

    account_type = "Premium Account"
    interest = 0.10
    discount = 0.20
    minimum_balance = 50000
    account_index = 3

    def __init__(self, name, dob, password, initial_deposit):
        """
        Creates an object of PremiumAccount

        Args:
            name (str): Name of the user
            dob (str): Dob of the user in dd-mm-yyyy format
            password (str): Password of the user
            initial_deposit (int or float): Initial deposit of the user
        """
        super().__init__(name, dob, password, initial_deposit)
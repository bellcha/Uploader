import csv
import mysql.connector
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    Grocery = 1
    Subscriptions = 2
    Entertainment = 3
    Auto_Rental = 4
    Merchandise = 5
    Organizations = 6
    Health_Care = 7
    Other_Travel = 8
    Vehicle_Services = 9
    Services = 10
    Utilities = 11
    Restaurants = 12
    Gas = 13
    Lodging = 14
    Air_Travel = 15
    Account_Transfer = 16
    Household_Expense = 17
    Payroll = 18
    Mortgage = 19
    Credit_Card_Payment = 20
    ATM_Cash_Withdrawl = 21
    Account_Fee = 22
    Interest = 23
    Credit_Card_Rewards = 24
    Loan_Payment = 25
    Deposit = 26


class Account(Enum):
    Citi_Double_Cash_Credit_Card = 1
    Merchants_and_Marine_Bank = 2
    Citi_Custom_Cash_Credit_Card = 3
    Target_Red_Card = 4
    Capital_One_Savor_Card = 5


@dataclass
class TransactionHistory:
    id: int
    date: datetime
    amount: float
    description: str
    category_id: int
    account_id: int

    def __post_init__(self):
        self.date = self.date.strftime("%m-%d-%Y")

    @property
    def category(self):
        return TransactionHistory._convert_spaces(Category(self.category_id).name)

    @property
    def account(self):
        return TransactionHistory._convert_spaces(Account(self.account_id).name)

    @classmethod
    def _convert_spaces(cls, value: str):
        no_spaces = value.split("_")
        return " ".join(no_spaces)


@dataclass
class Transaction:
    transaction_date: datetime
    amount: float
    description: str
    category: str
    account: int

    def __post_init__(self):
        try:
            self.transaction_date = datetime.strptime(
                self.transaction_date.strip(), "%m/%d/%y"
            ).strftime("%Y-%m-%d")
        except ValueError:
            self.transaction_date = datetime.strptime(
                self.transaction_date.strip(), "%m/%d/%Y"
            ).strftime("%Y-%m-%d")
        finally:
            self.amount = float(self.amount)
            self.category = self.category.strip()
            self.account = self.account.strip()

    # Converts the Category Name to the corresponding CategoyID in the Database.
    @property
    def category_id(self):
        return Category[Transaction._convert_spaces(self.category)].value

    @property
    def account_id(self):
        return Account[Transaction._convert_spaces(self.account)].value

    @property
    def insert_value(self):
        return (
            self.transaction_date,
            self.amount,
            self.description,
            self.category_id,
            self.account_id,
        )

    @classmethod
    def _convert_spaces(cls, value: str):
        no_spaces = value.split(" ")
        return "_".join(no_spaces)


class Database:
    def __init__(self, host, user, password, database) -> None:
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, passwd=password, database=database
            )
        except mysql.connector.Error as e:
            print(f"Error connecting to Database: {e}")

    def select_all(self, table):
        query = f"SELECT * FROM {table} where transaction_date between (CURDATE() - INTERVAL 2 MONTH) and CURDATE() ORDER BY transaction_date DESC"

        conn = self.connection

        cursor = conn.cursor()

        cursor.execute(query)

        trans = cursor.fetchall()

        cursor.close()

        conn.close()

        trans_list = [
            TransactionHistory(
                id=t[0],
                date=t[1],
                amount=t[2],
                description=t[3],
                category_id=t[4],
                account_id=t[5],
            )
            for t in trans
        ]

        return trans_list

    def import_csv(self, table, csv_file):
        conn = self.connection
        cursor = conn.cursor()
        with open(csv_file, "r") as file:
            lines = csv.DictReader(file)
            transactions = [Transaction(**line) for line in lines]
            insert_values = [t.insert_value for t in transactions]

            insert_statement = "INSERT INTO {table} (transaction_date, amount, description, category, account) VALUES(%s, %s, %s, %s, %s)".format(
                table=table
            )

            cursor.executemany(insert_statement, insert_values)

            cursor.close()

            conn.commit()

            conn.close()

            return transactions

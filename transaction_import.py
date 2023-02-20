import csv
import sys
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


@dataclass
class Transaction:
    transaction_date: datetime
    amount: float
    description: str
    category: str
    account: int

    def __post_init__(self):
        self.transaction_date = datetime.strptime(
            self.transaction_date, "%m/%d/%y"
        ).strftime("%Y-%m-%d")
        self.amount = float(self.amount)
        self.account = int(self.account)

    # Converts the Category Name to the corresponding CategoyID in the Database.
    @property
    def category_id(self):
        no_spaces = self.category.split(" ")
        return Category["_".join(no_spaces)].value


class Database:
    def __init__(self, host, user, password, database) -> None:
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, passwd=password, database=database
            )
        except mysql.connector.Error as e:
            print(f"Error connecting to Database: {e}")

    def select_all(self, table):
        query = f"SELECT * FROM {table}"

        cursor = self.connection.cursor()

        cursor.execute(query)

        return cursor

    def import_csv(self, table, csv_file):
        cursor = self.connection.cursor()
        with open(csv_file, "r") as file:
            lines = csv.DictReader(file)
            transactions = [Transaction(**line) for line in lines]

            for transaction in transactions:

                insert_statement = "INSERT INTO {table} (transaction_date, amount, description, categoryID, account) VALUES(%s, %s, %s, %s, %s)".format(
                    table=table
                )
                print(f"Inserting {transaction}")

                cursor.execute(
                    insert_statement,
                    (
                        transaction.transaction_date,
                        transaction.amount,
                        transaction.description,
                        transaction.category_id,
                        transaction.account,
                    ),
                )
            print("Import Complete!")
            self.connection.commit()
            return transactions


def main():

    table = sys.argv[1]
    csv_file = sys.argv[2]

    db = Database(
        host="10.69.69.107", user="root", password="1234", database="PurchaseHistory"
    )

    db.import_csv(table, csv_file)


if __name__ == "__main__":
    main()

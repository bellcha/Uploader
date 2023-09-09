import csv
import mysql.connector
from datetime import datetime
from dataclasses import dataclass
import pandas as pd


@dataclass
class TransactionHistory:
    id: int
    date: datetime
    amount: float
    description: str
    category: str
    account: str

    def __post_init__(self):
        self.date = self.date.strftime("%m-%d-%Y")


@dataclass
class Transaction:
    transaction_date: datetime
    amount: float
    description: str
    category: str
    account: int
    category_lookup: dict
    account_lookup: dict

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

    @property
    def category_id(self):
        return self.category_lookup[self.category]

    @property
    def account_id(self):
        return self.account_lookup[self.account]

    @property
    def insert_value(self):
        return (
            self.transaction_date,
            self.amount,
            self.description,
            self.category_id,
            self.account_id,
        )


class Database:
    def __init__(self, host, user, password, database) -> None:
        try:
            self.connection = mysql.connector.connect(
                host=host, user=user, passwd=password, database=database
            )
        except mysql.connector.Error as e:
            print(f"Error connecting to Database: {e}")

    def select_all(self, table):
        query = f"SELECT DISTINCT transactions.id, transaction_date, amount, description, name, AccountName FROM {table} inner join category as ca on ca.id = category inner join Account on AccountID = account where transaction_date between (CURDATE() - INTERVAL 2 MONTH) and CURDATE() ORDER BY transaction_date DESC"

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
                category=t[4],
                account=t[5],
            )
            for t in trans
        ]

        return trans_list

    def get_values(self, query) -> dict:

        conn = self.connection

        cursor = conn.cursor()

        cursor.execute(query)

        items = cursor.fetchall()

        cursor.close()

        conn.close()

        table_dict = dict()

        for k, v in items:

            table_dict[v] = k

        return table_dict

    def import_csv(self, table, csv_file, category_lookup, account_lookup):
        conn = self.connection
        cursor = conn.cursor()
        with open(csv_file, "r") as file:
            lines = csv.DictReader(file)
            transactions = [
                Transaction(
                    **line,
                    account_lookup=account_lookup,
                    category_lookup=category_lookup,
                )
                for line in lines
            ]
            insert_values = [t.insert_value for t in transactions]

            insert_statement = "INSERT INTO {table} (transaction_date, amount, description, category, account) VALUES(%s, %s, %s, %s, %s)".format(
                table=table
            )

            cursor.executemany(insert_statement, insert_values)

            cursor.close()

            conn.commit()

            conn.close()

            return transactions

    def get_dataframe(self) -> pd.DataFrame:
        conn = self.connection

        cursor = conn.cursor()

        query = "SELECT transaction_date, amount, description, AccountName as account, name as category from transactions left join category ca on category = ca.id left join Account acc on account = acc.AccountID"

        cursor.execute(query)

        trans = cursor.fetchall()

        cols = ["transaction_date", "amount", "description", "account", "category"]

        df = pd.DataFrame(trans, columns=cols)

        conn.close()

        return df

select max(transaction_date), AccountName from transactions
inner join Account on account = AccountID
group by AccountName;

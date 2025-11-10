import numpy as np
import pandas as pd
from datetime import datetime

def add_expense(account, cat, note, amount, income_expense):
    df = pd.read_csv("expense_data_1.csv")
    date_obj = datetime.now()

    try:
        amount = float(amount)
    except ValueError:
        print("Amount must be numeric.")
        return
#meow meow
#Bhaww Bhawwww
#kaw kaw
    cat = cat.strip().capitalize()
    note = note.strip() if note else ""
    account = account
    income_expense = income_expense.capitalize()
    new_row = {
        "Date": date_obj.strftime("%Y-%m-%d %H:%M"),
        "Mode": account,
        "Category": cat,
        "Note": note,
        "INR": amount,
        "Income/Expense": income_expense,
        "Amount": amount,
        "Currency": "INR",
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv("expense_data_1.csv", index=False)
    print(f"Added {income_expense.lower()} of ₹{amount} under '{cat}' category.")

def view():
    all_expense = pd.read_csv("expense_data_1.csv")
    return all_expense

def view_par(col_name):
    df = pd.read_csv("expense_data_1.csv")
    return df[col_name.capitalize()]


def delete_expense(row_number):
    df = pd.read_csv("expense_data_1.csv")

    if row_number < 0 or row_number >= len(df):
        print("Invalid row number. Please enter a valid index.")
        return

    df = df.drop(df.index[row_number])
    df.to_csv("expense_data_1.csv", index=False)
    print(f"Expense entry at row {row_number} deleted successfully.")

def calculate_expense(file_path = "expense_data_1.csv"):
    df = pd.read_csv(file_path)

    amounts = df['Amount'].to_numpy()
    income = df.loc[df['Income/Expense'].str.lower() == 'income', 'Amount'].to_numpy()
    expense = df.loc[df['Income/Expense'].str.lower() == 'expense', 'Amount'].to_numpy()

    total_income = np.sum(income)
    total_expense = np.sum(expense)

    avg_transaction = np.mean(amounts)

    print(" Account Summary:")
    print(f"Total Expense: ₹{total_expense:.2f}")
    print(f"Average Transaction: ₹{avg_transaction:.2f}")
    print(f"Total income: {total_income:.2f}")


while True:
    print("\n1.add ")
    print("\n2.view ")
    print("\n3.delete ")
    print("\n4.stats ")
    try:
        ch = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid choice. Please enter a valid choice.")
        continue
    if ch == 1:
        m = input("mode of payment? ")
        n = input("note(not compulsory: ")
        a= input("amount(in rupees): ")
        i = input("income or expense ?")
        if i == "income":

            c = input("reason of income: ")
        else:
            c = input("reason of expense: ")
        print(add_expense(m,c,n,a,i))
    if ch == 2:
        print("1.Particular column. ")
        print("2.Full sheet")
        ch2 = int(input("1 or 2: "))
        if ch2 == 1:
            print("Name of columns:-")
            print("1.Date")
            print("2.Mode")
            print("3.Category")
            print("4.Note")
            print("5.INR")
            print("6.Amount")
            print("7.Currency")
            column_name = input("enter column name: ")
            print(view_par(column_name))
        else:
            print(view())

    if ch == 3:
        df = pd.read_csv("expense_data_1.csv")
        print(df.tail())
        row = int(input("Enter row number: "))
        delete_expense(row)

    if ch == 4:
        print(calculate_expense())



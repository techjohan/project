import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from prettytable import PrettyTable
from decimal import Decimal
from datetime import datetime

mydb = mysql.connector.connect(
    host="localhost", user="root", password="root", database="jobank"
)
mycursor = mydb.cursor()

print(
    """ 
  $$$$$\           $$$$$$$\                      $$\       
   \__$$ |          $$  __$$\                     $$ |      
      $$ | $$$$$$\  $$ |  $$ | $$$$$$\  $$$$$$$\  $$ |  $$\ 
      $$ |$$  __$$\ $$$$$$$\ | \____$$\ $$  __$$\ $$ | $$  |
$$\   $$ |$$ /  $$ |$$  __$$\  $$$$$$$ |$$ |  $$ |$$$$$$  / 
$$ |  $$ |$$ |  $$ |$$ |  $$ |$$  __$$ |$$ |  $$ |$$  _$$<  
\$$$$$$  |\$$$$$$  |$$$$$$$  |\$$$$$$$ |$$ |  $$ |$$ | \$$\ 
 \______/  \______/ \_______/  \_______|\__|  \__|\__|  \__|
                                                            
                                                            
                                                            """
)
print("------------------------------------------------------------------------")


def balance_enquiry():
    username = str(input("enter username"))
    password = str(input("enter password"))
    sql = "SELECT user_id, username,balance FROM users WHERE username =%s and password =%s"
    val = (username, password)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    if result:
        balance = result[2]
        print("You have a balance of {}".format(balance))

        table = PrettyTable()
        table.field_names = ["User ID", "Username", "Balance"]
        table.add_row(result)
        print(table)
    else:
        print("Invalid credentials or user not found.")


def add_user(first_name, last_name, username, password, email):
    sql = "INSERT INTO users (first_name, last_name, username, password, email, balance) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (first_name, last_name, username, password, email, 1000)
    try:
        mycursor.execute(sql, val)
        mydb.commit()  # Commit the changes to the database
        print("User added successfully.")
    except mysql.connector.Error as e:
        print("Error Registration Failed", e)


def netbank():
    mydb = mysql.connector.connect(
        host="localhost", user="root", password="root", database="jobank"
    )
    mycursor = mydb.cursor()

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Check if user exists and password is correct
    check_sql = "SELECT * FROM users WHERE username = %s AND password = %s"
    check_val = (username, password)
    mycursor.execute(check_sql, check_val)
    user = mycursor.fetchone()

    if user:
        print("Login successful.")
        loggedin(user)
    else:
        print("Invalid username or password. Login failed.")


def transfer(sender, receiver, amount):
    sql = "SELECT balance FROM users WHERE username = %s"
    val = (sender,)
    mycursor.execute(sql, val)

    sender_balance = mycursor.fetchone()

    if amount < sender_balance[0]:
        sender_new_balance = sender_balance[0] - Decimal(amount)
        update_sender_sql = "UPDATE users SET balance = %s WHERE username = %s"
        update_sender_val = (sender_new_balance, sender)
        mycursor.execute(update_sender_sql, update_sender_val)

        update_recipient_sql = (
            "UPDATE users SET balance = balance + %s WHERE username = %s"
        )
        update_recipient_val = (amount, receiver)
        mycursor.execute(update_recipient_sql, update_recipient_val)
        mydb.commit()

        insert_transaction = "INSERT INTO transactions (sender, receiver, amount, timestamp) VALUES (%s, %s, %s, %s)"
        timestamp = datetime.now()
        transaction_values = (sender, receiver, amount, timestamp)
        mycursor.execute(insert_transaction, transaction_values)

        mydb.commit()

        print("Transaction Successful! ")
        print("Available Balance ₹{}".format(sender_new_balance))
    else:
        print("insufficent balance")


def loggedin(user):
    name = user[1]
    currentamount = user[6]

    print("Welcome {}!".format(name))
    print()
    print("Your available balance is ₹{}".format(currentamount))

    b = input(
        """
    
    1 - Transfer Money
    2 - View Intrest Rates
    3 - View Transacctions
    """
    )
    if b == "1":
        sender = str(input("Enter Your Username: "))
        receiver = str(input("Enter Reciver Username: "))
        amount = float(input("Enter Amount to send: "))
        transfer(sender, receiver, amount)

    elif b == "2":
        rates()
        loggedin(user)

    elif b == "3":
        sql = "SELECT * FROM transactions WHERE sender =%s OR receiver =%s"
        val = (user[3], user[3])
        mycursor.execute(sql, val)
        result = mycursor.fetchone()
        if result:
            table = PrettyTable()
            table.field_names = [
                "Transaction ID",
                "Sender",
                "Receiver",
                "Amount",
                "Date Time",
            ]

            table.add_row(result)
            print(table)
        else:
            print("something went wrong")


def rates():
    rates = [
        ["Saving Bank", "5%"],
        ["Fixed Deposit", "7%"],
        ["Personal Loan", "12%"],
        ["Home Loan", "9%"],
    ]
    print()
    print()
    print()
    print("------------------------------------------------------------------------")

    df = pd.DataFrame(rates, columns=["Type", "Rate"])
    print(df)
    print()
    print()
    print()
    print("------------------------------------------------------------------------")


a = input(
    """
1 - Open a Savings Account
2 - Login to NetBank
3 - Balance Enquiry
4 - View Rates
5 - Calculate Interest
          """
)
print("------------------------------------------------------------------------")

if a == "1":
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    email = input("Enter email: ")

    add_user(first_name, last_name, username, password, email)

elif a == "2":
    netbank()


elif a == "3":
    balance_enquiry()


elif a == "4":
    rates()

elif a == "5":
    amount = float(input("Enter Amount: "))
    rate = float(input("Enter Intrest Rate: "))
    years = float(input("Enter Total Years: "))
    ci = amount * ((1 + rate / 100) ** years)

    amountint = ci - amount

    y = [amount, amountint]
    mylabels = ["Principal", "Interest"]

    plt.pie(y, labels=mylabels)
    plt.show()

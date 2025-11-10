
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

# Initialize an empty DataFrame for transactions
try:
    transactions_df = pd.read_csv('transactions.csv')
    if 'Type' not in transactions_df.columns:
        transactions_df['Type'] = 'Expenditure'
except FileNotFoundError:
    transactions_df = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Type'])

def save_transactions():
    transactions_df.to_csv('transactions.csv', index=False)

@app.route('/')
def index():
    global transactions_df
    if not transactions_df.empty:
        # Ensure 'Date' column is datetime
        transactions_df['Date'] = pd.to_datetime(transactions_df['Date'])

        # Calculate total income and expenditure
        total_income = transactions_df[transactions_df['Type'] == 'Income']['Amount'].sum()
        total_expenditure = transactions_df[transactions_df['Type'] == 'Expenditure']['Amount'].sum()
        current_balance = total_income - total_expenditure

        # Get current month and year
        now = datetime.now()
        current_month = now.month
        current_year = now.year

        # Filter for current month
        monthly_transactions = transactions_df[(transactions_df['Date'].dt.month == current_month) & (transactions_df['Date'].dt.year == current_year)]
        monthly_spending = monthly_transactions[monthly_transactions['Type'] == 'Expenditure']['Amount'].sum()
        monthly_earnings = monthly_transactions[monthly_transactions['Type'] == 'Income']['Amount'].sum()
    else:
        current_balance = 0
        monthly_spending = 0
        monthly_earnings = 0
        
    return render_template('index.html', 
                           transactions=transactions_df.to_dict('records'),
                           current_balance=current_balance,
                           monthly_spending=monthly_spending,
                           monthly_earnings=monthly_earnings)

@app.route('/add', methods=['POST'])
def add_transaction():
    global transactions_df
    date = request.form['date']
    transaction_type = request.form['transaction_type']
    category = request.form['category']
    if category == 'Other':
        category = request.form.get('other_category', 'Other')
    amount = float(request.form['amount'])
    
    new_transaction = pd.DataFrame([{'Date': date, 'Category': category, 'Amount': amount, 'Type': transaction_type}])
    transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
    save_transactions()
    return redirect(url_for('index'))

@app.route('/plot')
def plot():
    if not transactions_df.empty:
        expenditures_df = transactions_df[transactions_df['Type'] == 'Expenditure']
        if not expenditures_df.empty:
            fig, ax = plt.subplots()
            # Set a larger figure size for better readability
            fig.set_size_inches(10, 6)
            expenditures_df.groupby('Category')['Amount'].sum().plot(kind='bar', ax=ax)
            ax.set_title('Spending by Category')
            ax.set_ylabel('Amount')
            plt.xticks(rotation=45, ha="right") # Rotate labels to prevent overlap
            plt.tight_layout() # Adjust layout

            # Save plot to a string
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close(fig)

            return render_template('plot.html', plot_url=plot_url)
    return redirect(url_for('index'))

@app.route('/download')
def download():
    # Use BytesIO to serve the file from memory without saving it to disk again
    output = io.BytesIO()
    transactions_df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='transactions.csv')

# The main entry point is now managed by devserver.sh for preview
# and can be run directly with `python -m flask run` for local development.

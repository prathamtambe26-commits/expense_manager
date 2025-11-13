import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from stocks import get_price

app = Flask(__name__)

# Initialize an empty DataFrame for transactions
try:
    transactions_df = pd.read_csv('transactions.csv')
    if 'Type' not in transactions_df.columns:
        transactions_df['Type'] = 'Expenditure'
except FileNotFoundError:
    transactions_df = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Type', 'Quantity'])

def save_transactions():
    transactions_df.to_csv('transactions.csv', index=False)

@app.route('/')
def index():
    global transactions_df
    if not transactions_df.empty:
        # Ensure 'Date' column is datetime, handling multiple formats
        transactions_df['Date'] = pd.to_datetime(transactions_df['Date'], errors='coerce')

        # Calculate total income and expenditure
        total_income = transactions_df[transactions_df['Type'] == 'Income']['Amount'].sum()
        total_expenditure = transactions_df[transactions_df['Type'] == 'Expenditure']['Amount'].sum()
        total_investment = transactions_df[transactions_df['Type'] == 'Investment']['Amount'].sum()
        current_balance = total_income - total_expenditure - total_investment

        # Get current month and year
        now = datetime.now()
        current_month = now.month
        current_year = now.year

        # Filter for current month
        monthly_transactions = transactions_df[(transactions_df['Date'].dt.month == current_month) & (transactions_df['Date'].dt.year == current_year)]
        monthly_spending = monthly_transactions[monthly_transactions['Type'] == 'Expenditure']['Amount'].sum()
        monthly_earnings = monthly_transactions[monthly_transactions['Type'] == 'Income']['Amount'].sum()
    # ... (calculations remain the same) ...
    else:
        current_balance = 0
        monthly_spending = 0
        monthly_earnings = 0

    # --- FIX STARTS HERE ---
    # Create a temporary copy for rendering
    render_df = transactions_df.copy()

    # Convert NaT (Pandas specific) to None (Python standard)
    # We cast to 'object' type first to allow mixing Datetime objects and None
    render_df['Date'] = render_df['Date'].astype(object).where(render_df['Date'].notnull(), None)

    return render_template('index.html',
                           transactions=render_df.to_dict('records'), # Use render_df here
                           current_balance=current_balance,
                           monthly_spending=monthly_spending,
                           monthly_earnings=monthly_earnings)

@app.route('/add', methods=['POST'])
def add_transaction():
    global transactions_df
    date = request.form['date']
    transaction_type = request.form['transaction_type']

    if transaction_type == 'Investment':
        stock_symbol = request.form['stock_symbol']
        exchange = request.form['exchange']
        quantity = int(request.form['quantity'])
        price = get_price(stock_symbol, exchange, date)

        # If price is not found, record transaction with 0 amount
        amount = price * quantity if price else 0

        new_transaction = pd.DataFrame([{'Date': date, 'Category': stock_symbol, 'Amount': amount, 'Type': transaction_type, 'Quantity': quantity}])
        transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
        save_transactions()

    else:
        category = request.form['category']
        if category == 'Other':
            category = request.form.get('other_category', 'Other')
        amount = float(request.form['amount'])
        new_transaction = pd.DataFrame([{'Date': date, 'Category': category, 'Amount': amount, 'Type': transaction_type, 'Quantity': 1}])
        transactions_df = pd.concat([transactions_df, new_transaction], ignore_index=True)
        save_transactions()

    return redirect(url_for('index'))

@app.route('/plot')
def plot():
    if not transactions_df.empty:
        expenditures_df = transactions_df[transactions_df['Type'] == 'Expenditure']
        if not expenditures_df.empty:
            fig, ax = plt.subplots()
            fig.set_size_inches(10, 6)

            # Generate Pie Chart
            expenditure_by_category = expenditures_df.groupby('Category')['Amount'].sum()
            ax.pie(expenditure_by_category, labels=expenditure_by_category.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            ax.set_title('Spending by Category')
            plt.tight_layout()

            # Save plot to a string
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close(fig)

            return render_template('plot.html', plot_url=plot_url)
    return redirect(url_for('index'))

@app.route('/stock_analysis')
def stock_analysis():
    # Create a copy to avoid modifying the global view
    investment_transactions = transactions_df[transactions_df['Type'] == 'Investment'].copy()
    stocks_data = []

    for index, row in investment_transactions.iterrows():
        current_price = get_price(row['Category'], 'NSE')

        # --- ROBUST DATE HANDLING ---
        # Try to convert to datetime
        date_obj = pd.to_datetime(row['Date'], errors='coerce')

        if pd.notna(date_obj):
            # If valid, format it as a string immediately
            date_display = date_obj.strftime('%Y-%m-%d')
        else:
            # If invalid (NaT), verify if the original data exists, otherwise show placeholder
            date_display = str(row['Date']) if row['Date'] else "Invalid Date"

        if current_price:
            gain_loss = (current_price * row['Quantity']) - row['Amount']
            stocks_data.append({
                'Date': date_display,  # We pass the ready-made string
                'Category': row['Category'],
                'Amount': row['Amount'],
                'CurrentPrice': current_price,
                'GainLoss': gain_loss
            })

    return render_template('stock_analysis.html', stocks=stocks_data)

@app.route('/download')
def download():
    output = io.BytesIO()
    transactions_df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='transactions.csv')


import gradio as gr
from accounts import Account, InsufficientFundsError, InsufficientSharesError, get_share_price

# Create a single account for this demo
account = Account("user123")

# Function to handle account creation/reset
def create_account():
    global account
    account = Account("user123")
    return "Account created for user123"

# Function to handle deposits
def deposit(amount_str):
    try:
        amount = float(amount_str)
        account.deposit(amount)
        return f"Successfully deposited ${amount:.2f}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

# Function to handle withdrawals
def withdraw(amount_str):
    try:
        amount = float(amount_str)
        account.withdraw(amount)
        return f"Successfully withdrew ${amount:.2f}. New balance: ${account.balance:.2f}"
    except (ValueError, InsufficientFundsError) as e:
        return f"Error: {str(e)}"

# Function to handle buying shares
def buy_shares(symbol, quantity_str):
    try:
        quantity = int(quantity_str)
        account.buy_shares(symbol, quantity)
        share_price = get_share_price(symbol)
        return f"Successfully bought {quantity} shares of {symbol} at ${share_price:.2f} each. New balance: ${account.balance:.2f}"
    except (ValueError, InsufficientFundsError) as e:
        return f"Error: {str(e)}"

# Function to handle selling shares
def sell_shares(symbol, quantity_str):
    try:
        quantity = int(quantity_str)
        account.sell_shares(symbol, quantity)
        share_price = get_share_price(symbol)
        return f"Successfully sold {quantity} shares of {symbol} at ${share_price:.2f} each. New balance: ${account.balance:.2f}"
    except (ValueError, InsufficientSharesError) as e:
        return f"Error: {str(e)}"

# Function to report holdings
def get_holdings():
    holdings = account.report_holdings()
    if not holdings:
        return "You currently have no share holdings."
    
    result = "Current Holdings:\n"
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = quantity * price
        result += f"- {symbol}: {quantity} shares at ${price:.2f} each, total value: ${value:.2f}\n"
    
    return result

# Function to report account summary
def get_summary():
    portfolio_value = account.calculate_portfolio_value()
    profit_loss = account.report_profit_loss()
    profit_loss_sign = "profit" if profit_loss >= 0 else "loss"
    
    result = f"Account Summary for user123:\n"
    result += f"Cash Balance: ${account.balance:.2f}\n"
    result += f"Initial Deposit: ${account.initial_deposit:.2f}\n"
    result += f"Portfolio Value: ${portfolio_value:.2f}\n"
    result += f"Overall {profit_loss_sign}: ${abs(profit_loss):.2f}\n"
    
    return result

# Function to list transactions
def get_transactions():
    transactions = account.list_transactions()
    if not transactions:
        return "No transactions recorded yet."
    
    result = "Transaction History:\n"
    for idx, txn in enumerate(transactions, 1):
        if txn['type'] == 'deposit':
            result += f"{idx}. Deposit: ${txn['amount']:.2f}\n"
        elif txn['type'] == 'withdraw':
            result += f"{idx}. Withdrawal: ${txn['amount']:.2f}\n"
        elif txn['type'] == 'buy':
            result += f"{idx}. Buy: {txn['quantity']} shares of {txn['symbol']} at ${txn['price']:.2f}\n"
        elif txn['type'] == 'sell':
            result += f"{idx}. Sell: {txn['quantity']} shares of {txn['symbol']} at ${txn['price']:.2f}\n"
    
    return result

# Function to get share price
def check_share_price(symbol):
    price = get_share_price(symbol)
    if price == 0.0:
        return f"Symbol {symbol} not found."
    return f"Current price of {symbol} is ${price:.2f}"

# Create the Gradio interface
with gr.Blocks(title="Trading Account Management") as demo:
    gr.Markdown("# Trading Account Management System")
    
    with gr.Tab("Account"):
        with gr.Row():
            create_btn = gr.Button("Create/Reset Account")
            output_create = gr.Textbox(label="Result", lines=2)
        
        create_btn.click(create_account, inputs=[], outputs=output_create)
        
        with gr.Row():
            with gr.Column():
                deposit_amount = gr.Textbox(label="Deposit Amount")
                deposit_btn = gr.Button("Deposit")
            with gr.Column():
                withdraw_amount = gr.Textbox(label="Withdraw Amount")
                withdraw_btn = gr.Button("Withdraw")
        
        output_account = gr.Textbox(label="Result", lines=2)
        
        deposit_btn.click(deposit, inputs=[deposit_amount], outputs=output_account)
        withdraw_btn.click(withdraw, inputs=[withdraw_amount], outputs=output_account)
    
    with gr.Tab("Trading"):
        with gr.Row():
            symbol_buy = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Symbol")
            quantity_buy = gr.Textbox(label="Quantity")
            buy_btn = gr.Button("Buy Shares")
        
        with gr.Row():
            symbol_sell = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Symbol")
            quantity_sell = gr.Textbox(label="Quantity")
            sell_btn = gr.Button("Sell Shares")
        
        with gr.Row():
            symbol_price = gr.Dropdown(choices=["AAPL", "TSLA", "GOOGL"], label="Symbol")
            price_btn = gr.Button("Check Price")
        
        output_trading = gr.Textbox(label="Result", lines=2)
        
        buy_btn.click(buy_shares, inputs=[symbol_buy, quantity_buy], outputs=output_trading)
        sell_btn.click(sell_shares, inputs=[symbol_sell, quantity_sell], outputs=output_trading)
        price_btn.click(check_share_price, inputs=[symbol_price], outputs=output_trading)
    
    with gr.Tab("Reports"):
        with gr.Row():
            holdings_btn = gr.Button("Show Holdings")
            summary_btn = gr.Button("Account Summary")
            transactions_btn = gr.Button("Transaction History")
        
        output_reports = gr.Textbox(label="Report Result", lines=10)
        
        holdings_btn.click(get_holdings, inputs=[], outputs=output_reports)
        summary_btn.click(get_summary, inputs=[], outputs=output_reports)
        transactions_btn.click(get_transactions, inputs=[], outputs=output_reports)

if __name__ == "__main__":
    demo.launch()
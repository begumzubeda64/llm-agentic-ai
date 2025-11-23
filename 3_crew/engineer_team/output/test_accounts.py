import unittest
from unittest.mock import patch
import sys
from io import StringIO

# Import the module to test
from accounts import Account, InsufficientFundsError, InsufficientSharesError, get_share_price

class TestAccount(unittest.TestCase):

    def setUp(self):
        # Set up a new account for each test
        self.account = Account("test_user")

    def test_init(self):
        # Test account initialization
        self.assertEqual(self.account.user_id, "test_user")
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(self.account.initial_deposit, 0.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])

    def test_deposit_valid(self):
        # Test valid deposit
        self.account.deposit(100.0)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.initial_deposit, 100.0)
        self.assertEqual(self.account.transactions, [{"type": "deposit", "amount": 100.0}])

    def test_deposit_invalid(self):
        # Test invalid deposit (negative or zero amount)
        with self.assertRaises(ValueError):
            self.account.deposit(0.0)
        
        with self.assertRaises(ValueError):
            self.account.deposit(-50.0)

    def test_withdraw_valid(self):
        # Test valid withdrawal
        self.account.deposit(100.0)  # Add funds first
        self.account.withdraw(50.0)
        self.assertEqual(self.account.balance, 50.0)
        self.assertEqual(self.account.transactions[-1], {"type": "withdraw", "amount": 50.0})

    def test_withdraw_invalid(self):
        # Test invalid withdrawal (negative or zero amount)
        with self.assertRaises(ValueError):
            self.account.withdraw(0.0)
        
        with self.assertRaises(ValueError):
            self.account.withdraw(-50.0)

    def test_withdraw_insufficient_funds(self):
        # Test withdrawal with insufficient funds
        self.account.deposit(50.0)
        with self.assertRaises(InsufficientFundsError):
            self.account.withdraw(100.0)

    @patch("accounts.get_share_price")
    def test_buy_shares_valid(self, mock_get_share_price):
        # Mock the share price
        mock_get_share_price.return_value = 10.0
        
        # Deposit funds
        self.account.deposit(1000.0)
        
        # Buy shares
        self.account.buy_shares("AAPL", 5)
        
        # Check the balance, holdings, and transactions
        self.assertEqual(self.account.balance, 950.0)  # 1000 - (10 * 5)
        self.assertEqual(self.account.holdings, {"AAPL": 5})
        self.assertEqual(self.account.transactions[-1], {"type": "buy", "symbol": "AAPL", "quantity": 5, "price": 10.0})

    @patch("accounts.get_share_price")
    def test_buy_shares_invalid(self, mock_get_share_price):
        # Mock the share price
        mock_get_share_price.return_value = 10.0
        
        # Deposit funds
        self.account.deposit(30.0)
        
        # Test invalid quantity
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", 0)
        
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", -5)
        
        # Test insufficient funds
        with self.assertRaises(InsufficientFundsError):
            self.account.buy_shares("AAPL", 5)  # Would cost 50, but only have 30

    @patch("accounts.get_share_price")
    def test_sell_shares_valid(self, mock_get_share_price):
        # Mock the share price for buying and selling
        mock_get_share_price.return_value = 10.0
        
        # Deposit and buy shares first
        self.account.deposit(1000.0)
        self.account.buy_shares("AAPL", 10)
        
        # Reset the balance to simulate price changes
        self.account.balance = 900.0
        mock_get_share_price.return_value = 15.0  # Price increased
        
        # Sell some shares
        self.account.sell_shares("AAPL", 5)
        
        # Check the balance, holdings, and transactions
        self.assertEqual(self.account.balance, 975.0)  # 900 + (15 * 5)
        self.assertEqual(self.account.holdings, {"AAPL": 5})  # 10 - 5 = 5 remaining
        self.assertEqual(self.account.transactions[-1], {"type": "sell", "symbol": "AAPL", "quantity": 5, "price": 15.0})

    @patch("accounts.get_share_price")
    def test_sell_all_shares(self, mock_get_share_price):
        # Mock the share price for buying and selling
        mock_get_share_price.return_value = 10.0
        
        # Deposit and buy shares first
        self.account.deposit(1000.0)
        self.account.buy_shares("AAPL", 10)
        
        # Sell all shares
        self.account.sell_shares("AAPL", 10)
        
        # Check that the symbol is removed from holdings
        self.assertNotIn("AAPL", self.account.holdings)

    @patch("accounts.get_share_price")
    def test_sell_shares_invalid(self, mock_get_share_price):
        # Mock the share price
        mock_get_share_price.return_value = 10.0
        
        # Try selling without having shares
        with self.assertRaises(InsufficientSharesError):
            self.account.sell_shares("AAPL", 5)
        
        # Deposit and buy shares
        self.account.deposit(100.0)
        self.account.buy_shares("AAPL", 5)
        
        # Try selling invalid quantities
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 0)
        
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", -2)
        
        # Try selling more than owned
        with self.assertRaises(InsufficientSharesError):
            self.account.sell_shares("AAPL", 10)  # Only have 5

    @patch("accounts.get_share_price")
    def test_calculate_portfolio_value(self, mock_get_share_price):
        # Setup account with some holdings
        self.account.deposit(1000.0)
        
        # First stock purchase
        mock_get_share_price.return_value = 10.0
        self.account.buy_shares("AAPL", 10)  # 100 total value, 900 balance left
        
        # Second stock purchase
        mock_get_share_price.return_value = 20.0
        self.account.buy_shares("TSLA", 5)  # 100 total value, 800 balance left
        
        # Mock prices for portfolio calculation
        def side_effect(symbol):
            prices = {"AAPL": 15.0, "TSLA": 25.0}
            return prices.get(symbol, 0.0)
        
        mock_get_share_price.side_effect = side_effect
        
        # Calculate portfolio value: 800 (balance) + 10*15 (AAPL) + 5*25 (TSLA) = 800 + 150 + 125 = 1075
        self.assertEqual(self.account.calculate_portfolio_value(), 1075.0)

    @patch("accounts.get_share_price")
    def test_calculate_profit_loss(self, mock_get_share_price):
        # Setup account with initial deposit
        self.account.deposit(1000.0)  # initial_deposit = 1000
        
        # First stock purchase
        mock_get_share_price.return_value = 10.0
        self.account.buy_shares("AAPL", 10)  # 100 total value, 900 balance left
        
        # Mock prices for portfolio calculation
        def side_effect(symbol):
            prices = {"AAPL": 15.0}  # Price increased
            return prices.get(symbol, 0.0)
        
        mock_get_share_price.side_effect = side_effect
        
        # Calculate profit/loss: (900 + 10*15) - 1000 = 900 + 150 - 1000 = 50
        self.assertEqual(self.account.calculate_profit_loss(), 50.0)

    def test_report_holdings(self):
        # Test empty holdings
        self.assertEqual(self.account.report_holdings(), {})
        
        # Add some holdings
        self.account.deposit(1000.0)
        with patch("accounts.get_share_price", return_value=10.0):
            self.account.buy_shares("AAPL", 10)
        
        # Test reporting holdings
        self.assertEqual(self.account.report_holdings(), {"AAPL": 10})

    @patch("accounts.get_share_price")
    def test_report_profit_loss(self, mock_get_share_price):
        # This is essentially the same as calculate_profit_loss
        # Setup account with initial deposit
        self.account.deposit(1000.0)
        
        # Stock purchase
        mock_get_share_price.return_value = 10.0
        self.account.buy_shares("AAPL", 10)
        
        # Mock price increase for calculation
        mock_get_share_price.return_value = 15.0
        
        # Calculate profit/loss: (900 + 10*15) - 1000 = 50
        self.assertEqual(self.account.report_profit_loss(), 50.0)

    def test_list_transactions(self):
        # Test empty transactions
        self.assertEqual(self.account.list_transactions(), [])
        
        # Add some transactions
        self.account.deposit(500.0)
        self.account.withdraw(200.0)
        
        with patch("accounts.get_share_price", return_value=10.0):
            self.account.buy_shares("AAPL", 5)
        
        # Should have 3 transactions now
        transactions = self.account.list_transactions()
        self.assertEqual(len(transactions), 3)
        self.assertEqual(transactions[0], {"type": "deposit", "amount": 500.0})
        self.assertEqual(transactions[1], {"type": "withdraw", "amount": 200.0})
        self.assertEqual(transactions[2]["type"], "buy")

    def test_get_share_price(self):
        # Test the helper function
        self.assertEqual(get_share_price("AAPL"), 150.0)
        self.assertEqual(get_share_price("TSLA"), 700.0)
        self.assertEqual(get_share_price("GOOGL"), 2800.0)
        self.assertEqual(get_share_price("UNKNOWN"), 0.0)  # Default value for unknown symbols

if __name__ == "__main__":
    unittest.main()
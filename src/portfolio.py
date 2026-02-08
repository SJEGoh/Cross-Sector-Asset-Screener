class SignalPortfolio:
    def __init__(self, initial_cash=10000):
        self.cash = initial_cash
        self.position = 0       # Positive = Long, Negative = Short
        self.entry_price = 0    # Track entry for PnL calculation
        self.equity = initial_cash
        self.history = []       # Stores daily state

    def update(self, signal, price, date=None):
        """
        The Master Switch: Feeds a signal and price to update the portfolio state.
        signal: 1 (Long), -1 (Short), 0 (Exit/Flat)
        """
        
        # 1. CHECK EXIT CONDITIONS
        # If we are Long and signal is NOT Long -> Sell
        if self.position > 0 and signal != 1:
            self._close_position(price)
            
        # If we are Short and signal is NOT Short -> Cover
        if self.position < 0 and signal != -1:
            self._close_position(price)

        # 2. CHECK ENTRY CONDITIONS
        # If we are Flat and signal is Long -> Buy
        if self.position == 0 and signal == 1:
            self._open_long(price)
            
        # If we are Flat and signal is Short -> Short Sell
        if self.position == 0 and signal == -1:
            self._open_short(price)

        # 3. UPDATE EQUITY (Mark-to-Market)
        self.equity = self.get_value(price)
        
        # 4. === CRITICAL FIX: SAVE THE HISTORY ===
        self.history.append({
            "Date": date,
            "Equity": self.equity,
            "Position": self.position,
            "Price": price,
            "Cash": self.cash
        })
        
        return self.equity

    def _open_long(self, price):
        # Calculate max shares we can afford
        quantity = int(self.cash / price)
        if quantity > 0:
            cost = quantity * price
            self.cash -= cost
            self.position = quantity
            self.entry_price = price

    def _open_short(self, price):
        # Assume we use 100% of cash as collateral to short
        quantity = int(self.cash / price) 
        if quantity > 0:
            # In a short, cash increases (proceeds), but we owe the shares back
            self.cash += (quantity * price) 
            self.position = -quantity
            self.entry_price = price

    def _close_position(self, price):
        if self.position == 0: return
        
        # Closing Long (Sell)
        if self.position > 0:
            revenue = self.position * price
            self.cash += revenue
            
        # Closing Short (Buy to Cover)
        elif self.position < 0:
            cost = abs(self.position) * price
            self.cash -= cost
            
        self.position = 0
        self.entry_price = 0

    def get_value(self, price):
        """ Calculates Total Portfolio Value (Cash + Unrealized PnL) """
        if self.position >= 0:
            return self.cash + (self.position * price)
        else:
            # For shorts: Value = Cash - Cost to Buy Back
            return self.cash - (abs(self.position) * price)

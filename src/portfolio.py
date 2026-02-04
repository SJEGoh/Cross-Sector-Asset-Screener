class MomentumPortfolio:
    def __init__(self, initial_cash=10000):
        self.cash = initial_cash
        self.position = 0
        self.stop_price = 0
        self.close_price = 0

    def buy(self, price, quantity, ex):
        cost = price * quantity
        if cost <= self.cash:
            self.cash -= cost
            self.position += quantity
            self.close_price = ex
            self.stop_price = price * 0.8
            return (f"BUY: {quantity} at {price}")
        else:
            print("Insufficient funds for this trade.")

    def sell(self, price, quantity, ex):
        rev = price * quantity
        self.cash += rev
        self.position -= quantity
        self.close_price = ex
        self.stop_price = price * 1.25
        return (f"SELL {quantity} AT {price}")
    
    def close(self, price):
        if not self.position:
            return 
        
        if self.position < 0:
            if price < self.close_price or price > self.stop_price:
                self.cash += self.position * price
                st = (f"POSITION OF {self.position} CLOSED AT {price}")
                self.position = 0
                self.stop_price = 0
                return st
                
        if self.position > 0:
            if price > self.close_price or price < self.stop_price:
                self.cash += self.position * price
                st = (f"POSITION OF {self.position} CLOSED AT {price}")
                self.position = 0
                self.stop_price = 0
                return st
    

    def get_value(self, price):
        return self.cash + self.position * price
    
    def holding(self):
        return self.position
    


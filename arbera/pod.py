import logging
from rich.logging import RichHandler
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console(file=open('var/arbera.log', 'a'))
handler = RichHandler(markup=False, console=console, show_path=True, show_time=True, show_level=True, rich_tracebacks=True)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


class Pod:
    def __init__(self, wrap_fee=1, unwrap_fee=2, burn_fee=20, buy_fee=0.5, sell_fee=0.5, partner_fee=1):
        self.wrap_fee = wrap_fee / 100
        self.unwrap_fee = unwrap_fee / 100
        self.buy_fee = buy_fee / 100
        self.sell_fee = sell_fee / 100
        self.partner_fee = partner_fee / 100
        self.burn_fee = burn_fee / 100
    
        self.token0 = "TOKEN"
        self.token0_wrapped = "apTOKEN"
        self.token1 = "apOHM"
        self.token0_wrapped_supply = 0
        self.token0_balance = 0
        self.token0_lp_balance = 0
        self.token1_lp_balance = 0
        self.partner_fee_balance = 0
        self.burn_fee_balance = 0
        self.peas_fee_balance = 0

    @property
    def cbr(self):
        return self.token0_balance / self.token0_wrapped_supply

    @property
    def cbr_apr(self):
        return (self.cbr - 1.0) * 100

    @property
    def lp_apr(self):
        return 0.0 * 100

    @property
    def rewards(self):
        return self.peas_fee_balance * 0.9

    def mint(self, amount):
        self.token0_wrapped_supply += amount
        logger.info(f"mint: {amount} pTOKEN")
        return amount
    
    def burn(self, amount):
        if amount <= self.token0_wrapped_supply:
            self.token0_wrapped_supply -= amount
            logger.info(f"burn: {amount} pTOKEN")
            return amount
        else:
            logger.info(f"burn: failed {amount} pTOKEN")
        return 0
    
    def wrap(self, amount):
        fee = amount * self.wrap_fee
        partner_fee = fee * self.partner_fee
        burn_fee = fee * self.burn_fee
        peas_buy = fee - (partner_fee + burn_fee)
        return_amount = amount - fee

        self.mint(amount)
        self.burn(burn_fee)
        self.token0_balance += amount
        self.partner_fee_balance += partner_fee
        self.burn_fee_balance += burn_fee
        self.peas_fee_balance += peas_buy

        logger.info(f"wrap fee: {fee}; returned amount: {return_amount} pTOKEN")
        return return_amount
        
    def unwrap(self, amount):
        fee = amount * self.unwrap_fee
        partner_fee = fee * self.partner_fee
        burn_fee = fee * self.burn_fee
        peas_buy = fee - (partner_fee + burn_fee)
        unwrap_amount = amount - fee

        burned = self.burn(unwrap_amount)
        if burned > 0:
            self.burn(burn_fee)
            self.token0_balance -= unwrap_amount
            self.partner_fee_balance += partner_fee
            self.burn_fee_balance += burn_fee
            self.peas_fee_balance += peas_buy

            logger.info(f"unwrap fee: {fee}; reutrned amount: {unwrap_amount} TOKEN")
            return unwrap_amount
        else:
            return 0

    def handle(self, operation):
        if operation['action'] == 'wrap':
            result = self.wrap(operation['amount'])
            logger.info(f"wrap: {result} pTOKEN")
        elif operation['action'] == 'unwrap':
            result = self.unwrap(operation['amount'])
            logger.info(f"unwrap: {result} TOKEN")

    def __repr__(self):
        msg = f"""
Partner fee: {self.partner_fee_balance} pTOKEN
Peas Buy:    {self.peas_fee_balance} pTOKEN-worth
Burn total:  {self.burn_fee_balance} pTOKEN
---
TOKEN:       {self.token0_balance} in pod
pTOKEN:      {self.token0_wrapped_supply} total supply
---
Rewards:     {self.rewards} pTOKEN-swapped-for-PEAS
CBR:         {self.cbr}
CBR APR:     {self.cbr_apr} %
LP APR:      {self.lp_apr} %
"""
        return(msg)

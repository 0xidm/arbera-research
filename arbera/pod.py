import random
import logging

from rich.logging import RichHandler
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console(file=open('var/arbera.log', 'a'))
handler = RichHandler(markup=False, console=console, show_path=True, show_time=True, show_level=True, rich_tracebacks=True)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


class Pod:
    def __init__(self, arbera_price_usd=2.5, base_token="TOKEN", base_price_usd=0.15, quote_token="HONEY", quote_price_usd=1.0, wrap_fee=1, unwrap_fee=2, buy_fee=0.5, sell_fee=0.5, protocol_fee=1, partner_fee=1, buyback_fee=1, burn_fee=1):
        self._arbera_price_usd = arbera_price_usd

        # realized when users wrap token into pod
        self.wrap_fee = wrap_fee / 100

        # realized when users unwrap token from pod. Users can use the below formula to determine the quantity of TKN they can expect to receive when unwrapping brTOKEN; `(brTOKEN * CBR) * (100% - Unwrap Fee%)`
        self.unwrap_fee = unwrap_fee / 100

        # This fee determines if buying pod tokens from the liquidity pool staked users are LPing to earn yield in incurs a fee.
        self.buy_fee = buy_fee / 100

        # This fee determines if selling pod tokens from the liquidity pool staked users are LPing to earn yield in incurs a fee.
        self.sell_fee = sell_fee / 100

        # This fee allows the protocol to realize a small portion of pod tokens back for all volume through the pod. This fee is realized in the form of brTOKEN.
        self.protocol_fee = protocol_fee / 100

        # This fee allows the pod creator to realize a small portion of pod tokens back for all volume through the pod. This fee is realized in the form of brTOKEN.
        self.partner_fee = partner_fee / 100

        # This fee uses brTOKEN to buy ARBERA from the market, which is then distributed to LP providers for this pod.
        self.buyback_fee = buyback_fee / 100

        # This portion of brTOKEN is burned, which increases the collateral backing ratio.
        self.burn_fee = burn_fee / 100
    
        self.protocol_fee_balance = 0
        self.partner_fee_balance = 0
        self.buyback_fee_balance = 0
        self.burn_fee_balance = 0

        # Each pod (den) has a unique base_token and quote_token pair. base_token is the token that is wrapped into the pod.
        self.base_token = base_token
        self._base_price_usd = base_price_usd

        self.base_token_wrapped = f"br{base_token}"
        self._base_wrapped_price_usd = base_price_usd

        # Each pod pairs with a second token to provide swap liquidity into/out of the wrapped token.
        self.quote_token = quote_token
        self._quote_price_usd = quote_price_usd

        # The total supply of wrapper token that has been minted by the pod.
        self.base_token_wrapped_supply = 0

        # The pod's balance of base_token, which is the token that is wrapped into the pod.
        self.base_token_balance = 0

        # Each pod has an associated CMM pool that provides liquidity for the wrapped token.
        # The wrapped token must be paired with the quoting token in the CMM pool to provide liquidity.
        self.base_token_lp_balance = 0
        self.quote_token_lp_balance = 0

    @property
    def arbitrage_ratio(self):
        """
        Compare the cost of wrapping and unwrapping to the difference in price between the base token and the wrapped token.
        When this ratio is greater than 1, there is an arbitrage opportunity.
        """

        amount = 100
        unwrap_cost = self.calc_unwrap(amount)["total_fees"]
        unwrap_cost_usd = unwrap_cost * self.price_base_usd
        return (self.price_base_usd - self.price_wrapped_usd) / unwrap_cost_usd

    @property
    def cbr(self):
        "The change in pod token collateral backing since pod creation that starts at 1. If the backing ratio is 1.1, this means there is 1.1 TKN per brTOKEN in the pod."
        if self.base_token_wrapped_supply > 0:
            return self.base_token_balance / self.base_token_wrapped_supply
        else:
            return 0

    @property
    def cbr_apr(self):
        "(Holder APR) represents return for brTOKEN holders as a result of burn byproducts"
        return (self.cbr - 1.0) * 100

    @property
    def lp_tvl(self):
        "Obtained from Uniswap brToken pool; staked brTOKEN in USD + staked quote token in USD"
        return self.base_token_lp_balance * self.price_base_usd + self.quote_token_lp_balance * self.price_quote_usd

    @property
    def lp_apr(self):
        "The return obtained, as ARBERA buy-backs, from LPing."
        return self._arbera_price_usd * self.buyback_fee_balance / self.lp_tvl * 100

    @property
    def price_base_usd(self):
        "'Fair' price (USD) to obtain base (unwrapped) TOKEN directly from a DEX."
        return self._base_price_usd
    
    @property
    def price_wrapped_usd(self):
        "Price to (USD) obtain wrapped brTOKEN from a DEX, which can be unwrapped by the pod."
        return self._base_wrapped_price_usd

    @property
    def price_quote_usd(self):
        "Price (USD) to obtain quote token directly from a DEX."
        return self._quote_price_usd

    @property
    def total_lp_incentives(self):
        "The total amount of ARBERA that has been bought back by the pod using the buyback fee."
        return self.buyback_fee_balance * 0.9

    def calc_unwrap(self, amount):
        return self.calc_fees(self.unwrap_fee, amount)
    
    def calc_wrap(self, amount):
        return self.calc_fees(self.wrap_fee, amount)

    def calc_fees(self, un_wrap_fee, amount):
        total_fees = amount * un_wrap_fee
        return_amount = amount - total_fees

        protocol_fee = total_fees * self.protocol_fee
        partner_fee = total_fees * self.partner_fee
        burn_fee = total_fees * self.burn_fee
        arbera_buy = total_fees - (partner_fee + protocol_fee + burn_fee)

        return {
            "total_fees": total_fees,
            "protocol_fee": protocol_fee,
            "partner_fee": partner_fee,
            "burn_fee": burn_fee,
            "arbera_buy": arbera_buy,
            "return_amount": return_amount
        }

    ###
    # ERC-20 functions

    def mint(self, amount):
        self.base_token_wrapped_supply += amount
        logger.info(f"mint: {amount} br{self.base_token}")
        return amount
    
    def burn(self, amount):
        if amount <= self.base_token_wrapped_supply:
            self.base_token_wrapped_supply -= amount
            logger.info(f"burn: {amount} br{self.base_token}")
            return amount
        else:
            logger.info(f"burn: failed {amount} br{self.base_token}")
        return 0
    
    ###
    # Wrap/unwrap

    def wrap(self, amount):
        fees = self.calc_wrap(amount)

        # first mint the wrapped token 1:1 with amount provided
        self.mint(amount)

        # then burn the amount of brTOKEN to realize the burn fee
        self.burn(fees["burn_fee"])
        self.burn_fee_balance += fees["burn_fee"]

        # increase the pod balance of base token
        self.base_token_balance += amount

        # increase the protocol fee balance
        self.protocol_fee_balance += fees["protocol_fee"]

        # increase the partner fee balance
        self.partner_fee_balance += fees["partner_fee"]

        # increase the buyback fee balance
        self.buyback_fee_balance += fees["arbera_buy"]

        logger.info(f"wrap fee: {fees['total_fees']}; returned amount: {fees['return_amount']} br{self.base_token}")
        return fees["return_amount"]
        
    def unwrap(self, amount):
        fees = self.calc_unwrap(amount)
        burned = self.burn(amount)

        if burned > 0:
            self.burn(fees["burn_fee"])
            self.burn_fee_balance += fees["burn_fee"]

            self.base_token_balance -= fees["return_amount"]

            self.protocol_fee_balance += fees["protocol_fee"]

            self.partner_fee_balance += fees["partner_fee"]

            self.buyback_fee_balance += fees["arbera_buy"]

            logger.info(f"unwrap fee: {fees['total_fees']}; returned amount: {fees['return_amount']} br{self.base_token}")
            return fees["return_amount"]
        else:
            return 0

    ###
    # Liquidity pool

    def stake_lp(self, amount_base, amount_quote=None):
        if amount_quote is None:
            amount_quote = amount_base * self.price_base_usd / self.price_quote_usd

        # ensure the USD value of base is equivalent to the USD value of quote
        if amount_base * self.price_base_usd == amount_quote * self.price_quote_usd:
            self.base_token_lp_balance += amount_base
            self.quote_token_lp_balance += amount_quote
        else:
            logger.warning(f"stake: failed {amount_base} {self.base_token} {amount_quote} {self.quote_token}; amounts must be equal in USD value")
    
    def unstake_lp(self, amount_base, amount_quote=None):
        if amount_quote is None:
            amount_quote = amount_base * self.price_base_usd / self.price_quote_usd
        
        if amount_base * self.price_base_usd == amount_quote * self.price_quote_usd:
            # ensure the balance will not become negative
            if self.base_token_lp_balance >= amount_base and self.quote_token_lp_balance >= amount_quote:
                self.base_token_lp_balance -= amount_base
                self.quote_token_lp_balance -= amount_quote
            else:
                logger.warning(f"unstake: failed {amount_base} {self.base_token} {amount_quote} {self.quote_token}")

    def handle(self, operation):
        if operation['action'] == 'wrap':
            result = self.wrap(operation['amount'])
            logger.info(f"wrap: {result} br{self.base_token}")
        elif operation['action'] == 'unwrap':
            result = self.unwrap(operation['amount'])
            logger.info(f"unwrap: {result} {self.base_token}")
        elif operation['action'] == 'stake_lp':
            self.stake_lp(amount_base=operation['amount'])
            logger.info(f"stake: {operation['amount']} {self.base_token}")
        elif operation['action'] == 'unstake_lp':
            self.unstake_lp(amount_base=operation['amount'])
            logger.info(f"unstake: {operation['amount']} {self.base_token}")

    def tick(self):
        self._arbera_price_usd += (random.random() - 0.5) / 100
        self._base_price_usd += (random.random() - 0.5) / 100
        self._base_wrapped_price_usd += (random.random() - 0.5) / 100
        self._quote_price_usd += (random.random() - 0.5) / 100

    def __repr__(self):
        msg = f"""
Protocol fee: {self.protocol_fee_balance} br{self.base_token}
Partner fee:  {self.partner_fee_balance} br{self.base_token}
ARBERA Buy:   {self.buyback_fee_balance} br{self.base_token}-worth
Burn total:   {self.burn_fee_balance} br{self.base_token}
---
{self.base_token}:        {self.base_token_balance} in pod
br{self.base_token}:      {self.base_token_wrapped_supply} total supply
---
CBR:          {self.cbr}
CBR APR:      {self.cbr_apr} %
LP ARBERA:    {self.total_lp_incentives} br{self.base_token}-swapped-for-ARBERA
LP APR:       {self.lp_apr} %
"""
        return(msg)

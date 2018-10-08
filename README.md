# bibox-arb-bot
Stablecoin Arbitrage Bot for Bibox

# Description
This is a bot that exploits arbitrage opportunities between three stablecoins: USDT, GUSD, and DAI on the Bibox exchange. On Bibox, there are no markets to trade these tokens against each other (which is probably why there are still some arbitrage opportunities). Thus, the bot will use ETH or BTC as a go-between when buying/selling one of these currencies against each other.

# Step by Step Bot Description
Given a base token or stablecoin e.g. DAI and a conduit/go between token e.g. BTC, the bot will:
1. Check if the account has >10 of the base token
2. If it does, it will fetch the current best bid/ask for the 3 token-conduit token markets e.g. fetch the orderbooks for BTC-DAI, BTC-USDT, and BTC-GUSD
3. Using the orderbooks, it will determine the best price at which it could sell DAI for another stablecoin. In our DAI example, this price is the following: BID(USDT or GUSD - BTC) / ASK (DAI - BTC)
4. If the best price is over 1.003 i.e. it could get 1.003 GUSD or USDT for every 1 DAI based on existing orders in the limit order book, it will execute that transaction i.e. in our example, it would sell DAI for BTC and then use that BTC to buy either USDT or GUSD

# Risks
This bot is a work in progress and I'm fixing bugs as I come across them. Other than that there are two big risks: 
1. Any of GUSD, USDT, or DAI could break their peg and not be worth $1
2. Counterparty Risk - Bibox could get hacked or disappear

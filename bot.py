# -*- coding: utf-8 -*-
"""
This file contains a simple function
and code to actuall run the bot
"""

## my bot
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

import time
import bibox_cmds as cm

pegged_tokens = ["GUSD","USDT","DAI"]
conduit_tokens = ["BTC","ETH"]

def trader_bot():
	for token in pegged_tokens:
		#print(token)
	#since the account is always trading these 3 currencies, I will check
	#if I have a >10 balance in any of these 3 - if I do, then I will
	#attempt to sell that token for another
		if cm.getbalance(token)*.95>10:			
			for conduit_token in conduit_tokens:				
				cm.find_arb_opp(token, conduit_token)
				
				

while True:
	try:
		trader_bot()
		
	except:
		pass

	time.sleep(1)
	
	




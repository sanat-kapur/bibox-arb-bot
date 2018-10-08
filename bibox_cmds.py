# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 10:24:24 2018

@author: sanat.kapur
"""

## functions I need

import requests
import json
import time
import hmac
import hashlib

api_key = ### YOUR API KEY
api_secret = ### YOUR API SECRET

pegged_tokens = ["GUSD","USDT","DAI"]
conduit_tokens = ["BTC","ETH"]


def getSign(data,secret):
    #function taken from official bibox api github
    result = hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.md5).hexdigest()
    return result

def doApiRequestWithApikey(url, cmds, api_key, api_secret):
    #function taken from official bibox api github
    s_cmds = json.dumps(cmds)
    sign = getSign(s_cmds,api_secret)
    
    return(requests.post(url, data={'cmds': s_cmds, 'apikey': api_key,'sign':sign},timeout=10))    

def getbalance(currency):
    #return balance of currency 
    
    url = 'https://api.bibox.com/v1/transfer'

    cmds = [
            {
             'cmd':"transfer/assets",
             'body': {
                'select':1}
                    }]
    
    rqst = doApiRequestWithApikey(url, cmds, api_key, api_secret)
    
    parsed_rqst = json.loads(rqst.text)["result"][0]["result"]["assets_list"]
    
    for currency_json in parsed_rqst:
        if currency_json["coin_symbol"] == currency:
            return(float(currency_json["balance"]))

def getorderbook(currency_pair):
    """
    This function will return the best bid and best ask for a given pair,
    in the form of a dictionary
    """
    url = "https://api.bibox.com/v1/mdata"
    cmds = [
            {
    'cmd':"api/depth",
    'body':{
            'pair':currency_pair,
            'size':1
            }}
    ]
    
    
    response = doApiRequestWithApikey(url, cmds, api_key, api_secret)
    
    

    if response.status_code != 200:
        return(getorderbook(currency_pair))
    else:
        bid_price = json.loads(response.text)["result"][0]["result"]["bids"][0]["price"]
        bid_quantity = json.loads(response.text)["result"][0]["result"]["bids"][0]["volume"]
        
        ask_price = json.loads(response.text)["result"][0]["result"]["asks"][0]["price"]
        ask_quantity = json.loads(response.text)["result"][0]["result"]["asks"][0]["volume"]
        


        return({'pair':currency_pair,
            'bid_price':float(bid_price),
            'bid_quantity':float(bid_quantity),
            'ask_price':float(ask_price),
            'ask_quantity':float(ask_quantity)})    

def enter_limit_order(token_pair,direction,price,quantity):
    #this will enter a limit order and return order number if order went thru
    #and status code if order did not go thru
    
    dir_code = 0
    money = 0
    
    url = "https://api.bibox.com/v1/orderpending"
    
    if direction =="buy":
        dir_code = 1
        money = quantity
    elif direction =="sell":
        dir_code = 2
        money = quantity*price

    print(money)
    print(token_pair)
    print(price)
    print(quantity)
    
    cmds = [
    {
        'cmd':"orderpending/trade",
        'body':{
            'pair':token_pair,
            'account_type':0,
            'order_type':2,
            'order_side':dir_code,
            'pay_bix':1,
            'price':price,
            'amount':quantity,
            'money': money
        }
    }
    ]
        
    order_request = doApiRequestWithApikey(url, cmds, api_key, api_secret)
    
    print(order_request.text)

    #200 means order went through
    if order_request.status_code != 200:
        return(order_request.status_code)
    else:
        return(json.loads(order_request.text)["result"][0]["result"])

def check_pending_order_status(order_number):
    # this will check the order status of a pending order
    # it will retuen the % of the limit order that was filled
    # this function will return 100 if the order is not found in the 
    # pending order book i.e. it assumes that the order went through
    
    url = "https://api.bibox.com/v1/orderpending"
    
    cmds = [
    {
        'cmd':"orderpending/order",
        'body':{
                'id':order_number
        }
    }
    ]
    
    
    check_request = doApiRequestWithApikey(url, cmds, api_key, api_secret)
    
    if any(json.loads(check_request.text)["result"][0]["result"]): # true if got a non-empty response
        return(float(json.loads(check_request.text)["result"][0]["result"]["deal_percent"].strip('%')))
    else:
        return(100)

def cancel_order(order_id):
	# This will cancel an order
    url = "https://api.bibox.com/v1/orderpending"
    
    cmds = [
            {
    'cmd':"orderpending/cancelTrade",
    'body':{
            'orders_id':order_id
    }
    }
    ]
    
    doApiRequestWithApikey(url, cmds, api_key, api_secret)    

def get_order_history_text():
	# This returnd the order history in text format
    url = "https://api.bibox.com/v1/orderpending"

    cmds = [
            {
             'cmd':"orderpending/orderHistoryList",
             'body': {
                #'pair':"ETH_USDT,ETH_DAI"}
                'page':1,
                'size':50
                }
                    }]

    order_req = doApiRequestWithApikey(url, cmds, api_key, api_secret)

    return(order_req.text)


  
def last_completed_order():
    #return last completed order as a dictionary object
    order_hist = get_order_history_text()
    
    return(json.loads(order_hist)["result"][0]["result"]["items"][0])
    
  
def find_arb_opp(token, conduit_token):
    """
    This function will check if there exists an opportunity to sell
    'token' for another pegged token at a price of >1.01 i.e. to receive
    more than 1.01 of the other pegged token for every 'token' held
    If there does, it will enter trades to execute on that opp
    """
    token_obook = getorderbook(conduit_token+"_"+token)
    
    other_peg_tokens = [token_name for token_name in pegged_tokens if token_name != token]
    
    other_token_obook  =[getorderbook(conduit_token+"_"+token_name) for token_name in other_peg_tokens]
    
    #get token that can be sold for the max price
    best_buy_token =  max(other_token_obook, key=lambda x:x['bid_price'])
    
    
    
    if (best_buy_token['bid_price']/token_obook["ask_price"] >1.003 ):
        
        ## quantity to trade = minimum quantity that can satisfy
        ## both orders
        
        #pick min of quantity from both orders and max balance
        
        trade_quantity = min(best_buy_token["bid_quantity"],token_obook["ask_quantity"],
                             getbalance(token)*.95/best_buy_token["ask_price"])
        
        
        order_hist_checkpoint1 = get_order_history_text()
        
        #trade 1
        #sell token for conduit token
        sell_token_trade = enter_limit_order(conduit_token+"_"+token,"buy",
                                       token_obook["ask_price"],trade_quantity)
        


        
        if sell_token_trade>1000: #check that it is an order number and not an http responsde code
            time.sleep(1) #give order 1 sec to execute            
            cancel_order(sell_token_trade)
        
        order_hist_checkpoint2 = get_order_history_text()
        
        """
        Bibox does not have a consistent order ID across pending and completed
        orders. To figure out if my order executed, I check if the completed order
        list has changed after I sent the order
        """
        
        sell_execute = order_hist_checkpoint1 != order_hist_checkpoint2 
        
        
        
        #if first order executed, try executing the second
        
        if sell_execute:
            
            
            
            sell_order = last_completed_order()
            sell_quantity = float(sell_order["amount"])
            
            #buy best token 
            
            buy_token_trade = enter_limit_order(best_buy_token["pair"],"sell",
                                       best_buy_token["ask_price"],sell_quantity)
        
            #trade completed
            #to ensure a profit, I usually leave the buy trade open even if
            #it doesn't execute immediately- usually, the volatility around these
            #tokens means it will usually execute soon and the overall
            #trade will still return over 1%


            
        
        
                
            
            
        
        
        
        
        
        
        
    
    
    
    
    
    
    
    


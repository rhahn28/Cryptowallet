import os
import bit
# from bit import Key, PrivateKey, PrivateKeyTestnet
from web3 import Web3
from dotenv import load_dotenv  # had to load this directly into directory
from web3.middleware import geth_poa_middleware
from eth_account import Account
import subprocess 
import json
from constants import *

load_dotenv()

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

key_value = os.getenv("PRIVATE_KEY")
mnemonic = os.getenv("MNEMONIC")

# function to create path, address, private/public key, for a coin)
def derive_wallets(mnemonic, coin_ticker):

    # calls shell for php to exceute hd-wallet-derive for a 12 word mnemonic for paricular coin_ticker
    command = f'php hd-wallet-derive/hd-wallet-derive.php -g --mnemonic="{mnemonic}" --cols=path,address,privkey,pubkey --coin={coin_ticker} --format=json'
   
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    #obtains data and error 
    (output, err) = p.communicate()
    
    # wait for the table of address to show so won't execute until child process terminates
    p_status = p.wait()
    keys = json.loads(output)
    return keys



# creates the raw, unsigined transaction that contains all meta data needed to transact.
def create_txn(coin, account, to, amount):
    
    # check if ETH
    if coin=="eth":
        gasEstimate = w3.eth.estimateGas({"from":account_one.address, "to":to, "value":amount})
        return {
            "from":account_one.address,
            "to":to,
            "value":amount,
            "gasPrice":w3.eth.gasPrice,
            "gas":gasEstimate,
            "nonce":w3.eth.getTransactionCount(account_one.address)
            #"chainID":chainID
        }
    # check if btc-test
    if coin=='btc-test':
        return bit.PrivateKeyTestnet.prepare_transaction(account_one.address, [(to, amount, BTC)])
            

# signs the transaction, then sends to the designated network.
def send_txn(coin, account, to, amount):
    
    if coin == "eth":
        # call create_txn from above and assign to object txn
        txn = create_txn(coin, account, to, amount)
        # sign the txn using the sign_transction methdo from web3
        signed_txn = account.sign_transaction(txn)
        # if eth capture the result of the send, checks for the error using sendRawTransactoin method
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    
    if coin == "btc-test":
        # call create_txn from above and assign to object txn
        txn = create_txn(coin, account, to, amount)
        # sign the txn using the sign_transction methdo from web3
        signed_txn = bit.PrivateKeyTestnet.sign_transaction(txn)                   
        # if btc-test capture the result of the send, checks for the error using sendRawTransactoin method
        result = bit.PrivateKeyTestnet.NetworkAPI.broadcast_tx_testnet(signed_txn)
    
       
    # use hex to translate the raw results
    print(result.hex())
    return result.hex()
    




# option 2 - use standard for loop to iterate through coin and add to dictionary keys where each coin has a set of address, private/public key from derive_wallets
#initailize a list of coins from constants.py
coin_tickers = ["btc-test", "eth", "btc"]

# create empty dictionary
coins = {}

# for loop creating a dictionary coins for each coin_ticker
for coin_ticker in coin_tickers:

    coins[coin_ticker] = derive_wallets(mnemonic, coin_ticker)
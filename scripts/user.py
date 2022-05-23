from brownie import KeeprTellor
from brownie import accounts
from brownie import network
from brownie import web3
import json
from eth_abi import encode_abi
import time

from web3 import contract

network.disconnect()
network.connect('mumbai')
acct = accounts.load('testac', password="")
playground_address="0x3477EB82263dabb59AC0CAcE47a61292f28A2eA7"
autopay_addr = "0x7126142D44E406eFE44be3C1EEf0995741Df88F1"
tstt_addr = "0x45cAF1aae42BA5565EC92362896cc8e0d55a2126"
print(f"The active network is {network.show_active()}")

with open('abi/faucet.json') as abi:
        abi = json.load(abi)

txn = {
        "gasPrice": web3.eth.gasPrice,
        "gas": 400000,
    }

def keeper_contract():
    keeper = KeeprTellor[-1]
    contract = web3.eth.contract(keeper.address, abi=keeper.abi)
    print(f"keeper contract address: {keeper.address}")
    return contract

def playground_contract():
    contract = web3.eth.contract(playground_address,abi=abi)
    print(f"playground contract address: {contract.address}")
    return contract

def tstt_contract():
    contract = web3.eth.contract(tstt_addr,abi=abi)
    print(f"tstt contract address: {contract.address}")
    return contract

def autopay_contract():
    contract = web3.eth.contract(autopay_addr,abi=abi)
    print(f"autopay contract address: {contract.address}")
    return contract

keeper = keeper_contract()
playground_contract = playground_contract()
tstt_contract = tstt_contract()

def get_tokens():
    """get tokens from playground faucet"""
    raw_txn = playground_contract.functions.faucet(str(keeper.address)).buildTransaction(txn)
    signed_txn = web3.eth.account.signTransaction(raw_txn,acct.private_key)
    send = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    web3.eth.wait_for_transaction_receipt(send.hex())
    print("balance of account: ",playground_contract.functions.balanceOf(str(keeper.address)).call())

def send_tokens_to_contract():
    txn["nonce"] = web3.eth.getTransactionCount(str(acct))
    send_token = tstt_contract.functions.transfer(str(keeper.address), 10).buildTransaction(txn)
    sign = web3.eth.account.signTransaction(send_token, acct.private_key)
    send = web3.eth.send_raw_transaction(sign.rawTransaction)
    web3.eth.wait_for_transaction_receipt(send.hex())
    print(f"send txn hash: {send.hex()}")

def approve_spending():
    """approve erc20 spending"""
    amount = int(10e18)
    txn["nonce"] = web3.eth.getTransactionCount(str(acct))
    apr = tstt_contract.functions.approve(str(keeper.address), amount).buildTransaction(txn)
    sign_apr = web3.eth.account.signTransaction(apr, acct.private_key)
    send_apr = web3.eth.send_raw_transaction(sign_apr.rawTransaction)
    web3.eth.wait_for_transaction_receipt(send_apr.hex())
    print(f"approve txn hash: {send_apr.hex()}")

def create_query():
    """encode your query according to tellor specs"""
    query_data = encode_abi(["string","bytes"],["TryOuts",encode_abi(["string","string"], ["Hello","world"])])
    query_id = "0x" + bytes(web3.keccak(query_data)).hex()
    query_data = "0x"+query_data.hex()
    value = web3.toHex(text="testing")
    nonce = 0#playground_contract.functions.getTimestampCountById(query_id).call()
    func = playground_contract.encodeABI(fn_name='submitValue',args=[query_id,value,nonce,query_data])
    return func

def tip_request():
    """make a request plus a tip to autopay for your function to be automated"""
    timestamp = int(time.time())
    chain_id = 80001
    amount = int(10)
    func = create_query()
    txn["nonce"] = web3.eth.getTransactionCount(str(acct))
    tip = keeper.functions.tip_request(func,playground_address,timestamp,chain_id,amount).buildTransaction(txn)
    sign = web3.eth.account.signTransaction(tip, acct.private_key)
    send = web3.eth.send_raw_transaction(sign.rawTransaction)
    web3.eth.wait_for_transaction_receipt(send.hex())
    print(f"transaction hash : {send.hex()}")

def main():
    approve_spending(),
    send_tokens_to_contract(),
    tip_request()
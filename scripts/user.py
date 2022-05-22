from brownie import KeeprTellor
from brownie import accounts
from brownie import network
from brownie import web3
import json
from eth_abi import encode_abi
import time

network.disconnect()
network.connect('mumbai')
acct = accounts.load('testac')
playground_address="0x3477EB82263dabb59AC0CAcE47a61292f28A2eA7"
print(f"The active network is {network.show_active()}")

with open('abi/faucet.json') as abi:
        abi = json.load(abi)

def keeper_contract():
    keeper = KeeprTellor[-1]
    contract = web3.eth.contract(keeper.address, abi=keeper.abi)
    print(f"keeper contract address: {keeper.address}")
    return contract

def playground_contract():
    contract = web3.eth.contract(playground_address,abi=abi)
    return playground_address, contract

def approve_spending():
    contract = web3.eth.contract(address=playground_address, abi=abi)
    amount = 100
    autopay_addr = "0xb42aEF36d3C79314BAbcd7578AEa15Fb799F9BEB"
    txn = {
        "gasPrice": web3.eth.gasPrice,
        "gas": 400000,
        "nonce": web3.eth.getTransactionCount(str(acct))
    }
    apr = contract.functions.approve(autopay_addr, amount).buildTransaction(txn)
    sign_apr = web3.eth.account.signTransaction(apr, acct.private_key)
    send_apr = web3.eth.send_raw_transaction(sign_apr.rawTransaction)
    web3.eth.wait_for_transaction_receipt(send_apr.hex())
    print(f"approve txn hash: {send_apr.hex()}")

def get_tokens():
    keeper = keeper_contract()
    contract = playground_contract()
    txn = {
        "gasPrice": web3.eth.gasPrice,
        "gas":400000,
        "nonce": web3.eth.getTransactionCount(str(acct)),
    }
    raw_txn = contract.functions.faucet(str(keeper.address)).buildTransaction(txn)
    signed_txn = web3.eth.account.signTransaction(raw_txn,acct.private_key)
    send = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    web3.eth.wait_for_transaction_receipt(send.hex())
    print("balance of account: ",contract.functions.balanceOf(str(acct)).call())

def get_data():
    address, contract = playground_contract()
    query_data = encode_abi(["string","bytes"],["TryOuts",encode_abi(["string","string"], ["Hello","world"])])
    query_id = "0x" + bytes(web3.keccak(query_data)).hex()
    query_data = "0x"+query_data.hex()
    value = web3.toHex(text="testing")
    nonce = 0 #from getter function based on query id
    func = contract.encodeABI(fn_name='submitValue',args=[query_id,value,nonce,query_data])
    return func, address

def tip_request():
    contract = keeper_contract()
    timestamp = int(time.time())
    chain_id = 80001
    amount = 1
    func, target_contract = get_data()
    txn = {
        "gasPrice": web3.eth.gasPrice,
        "gas": 400000,
        "nonce": web3.eth.getTransactionCount(str(acct))
    }
    tip = contract.functions.tip_request(func,target_contract,timestamp,chain_id,amount).buildTransaction(txn)
    sign = web3.eth.account.signTransaction(tip, acct.private_key)
    send = web3.eth.send_raw_transaction(sign.rawTransaction)
    web3.eth.wait_for_transaction_receipt(send.hex())
    print(f"transaction hash : {send.hex()}")

def main():
    # approve_spending()
    get_tokens()
    tip_request()
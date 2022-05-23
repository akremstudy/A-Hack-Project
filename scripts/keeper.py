from brownie import web3
from brownie import accounts
from brownie import network
from eth_abi import decode_single
import json

network.disconnect()
network.connect('mumbai')
acct = accounts.load('testac')
autopay_addr=""
playground_addr="0x3477EB82263dabb59AC0CAcE47a61292f28A2eA7"
print(f"The active network is {network.show_active()}")

with open('abi/faucet.json') as abi:
    abi = json.load(abi)

def autopay_contract():
    contract = web3.eth.contract(autopay_addr,abi=abi)
    return contract

def playground_contract():
    contract = web3.eth.contract(playground_addr, abi=abi)
    return contract

def get_tips():
    query_id=""
    contract = autopay_contract()
    get_current_tip = contract.functions.getCurrentTip(query_id)
    return get_current_tip


def call():
    # get data from oracle
    # tips = get_tips()
    # if tips < 0:
    #     return
    query_data = ""
    # decode 
    decoded = decode_single('(bytes,address,uint256,uint256)',query_data)
    func_data = decoded[0]

    tx = {
    'chainId': 80001,
    'data': func_data,
    'nonce': web3.eth.getTransactionCount(str(acct)),
    'from': str(acct),
    'to': playground_addr,
    'gas': 400000,
    'gasPrice': web3.eth.gasPrice
    }

    signed_tx = web3.eth.account.sign_transaction(tx, acct.private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"transaction hash: {tx_hash} for hash")

def main():
    call()
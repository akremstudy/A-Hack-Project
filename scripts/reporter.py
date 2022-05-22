from brownie import network
from brownie import KeeprTellor
from brownie import accounts
import brownie
import json
from brownie.network import web3
from eth_abi import encode_abi

network.disconnect()
network.connect('mumbai')

acct = accounts.load('testac',password="")

playground_address="0x3477EB82263dabb59AC0CAcE47a61292f28A2eA7"
with open('abi/faucet.json') as abi:
    abi = json.load(abi)

def keeper_contract():
    tellor_keeper = KeeprTellor[-1]
    contract = web3.eth.contract(tellor_keeper.address, abi=tellor_keeper.abi)
    return contract

def playground_contract():
    contract = web3.eth.contract(playground_address, abi=abi)
    return contract

def submit_txn():
    """submit random txn to oracle"""
    query_data = encode_abi(["string","bytes"],["TryOut",encode_abi(["string","string"], ["Hello","world"])])
    query_id = "0x" + bytes(web3.keccak(query_data)).hex()
    query_data = "0x"+query_data.hex()
    value = web3.toHex(text="test")
    nonce = 0 #from getter function based on query id
    contract = playground_contract()
    tx = {
        "gasPrice": web3.eth.gas_price,
        "gas": 400000,
        "nonce": web3.eth.getTransactionCount(str(acct))
    }
    raw = contract.functions.submitValue(query_id,value,nonce,query_data).buildTransaction(tx)
    signed = web3.eth.account.signTransaction(raw,acct.private_key)
    send = web3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"transaction hash : {send.hex()}")

def main():
    submit_txn()

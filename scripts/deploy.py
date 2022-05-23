from brownie import KeeprTellor
from brownie import accounts
from brownie import network

network.disconnect()
network.connect('mumbai')

acct = accounts.load('testac')

playground_addr = "0x3477EB82263dabb59AC0CAcE47a61292f28A2eA7"
autopay_addr = "0xD789488E5ee48Ef8b0719843672Bc04c213b648c"
tstt_token = "0x45cAF1aae42BA5565EC92362896cc8e0d55a2126"

def main(): 
    return acct.deploy(
        KeeprTellor,
        playground_addr,
        autopay_addr,
        tstt_token

    )
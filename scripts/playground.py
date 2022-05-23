from brownie import KeeprTellor, network
import brownie
network.disconnect()
network.connect('mumbai')
network.is_connected()


def contract_factory():
    print(f"The active network is {network.show_active()}")
    tellor_keeper = KeeprTellor[-1]
    contract = brownie.web3.eth.contract(tellor_keeper.address, abi=tellor_keeper.abi)
    return contract

def get_random_feed_balance():
    contract = contract_factory()
    random_feed_balance = contract.feed_balance("0x7c9ca4cc348680e2d4637472fc51228a079cb8a6a8cba51fe6f4ebbb3a930c8d").call()
    print(f"random_feed_balance: {random_feed_balance}")

def main():
    get_random_feed_balance()

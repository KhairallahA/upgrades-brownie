from brownie import (
    Box, 
    BoxV2, 
    ProxyAdmin, 
    TransparentUpgradeableProxy, 
    config, 
    network,
    Contract,
)
from scripts.helpful_scripts import get_account, encode_function_data, upgrade

def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy(
        {"from": account}, 
        publish_source=config["networks"][network.show_active()]["verify"]
    )
    # Optional, deploy the ProxyAdmin and use that as the admin contract
    proxy_admin = ProxyAdmin.deploy({"from": account})
    # We add box.store, to simulate the initializer being the `store` function
    # initializer = box, 1
    # box_encoded_initializer_function = encode_function_data(box.store, 1)
    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000}
    )
    print(f"Proxy deployed to {proxy} ! You can now upgrade it to BoxV2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(2, {"from": account})
    print(f"Here is the initial value in the Box: {proxy_box.retrieve()}")

    # Upgrade
    box_v2 = BoxV2.deploy({"from": account})
    upgrade_transaction = upgrade(account, proxy, box_v2, proxy_admin_contract=proxy_admin)
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    print(f"Starting value {proxy_box.retrieve()}")
    proxy_box.increment({"from": account})
    print(f"Ending value {proxy_box.retrieve()}")
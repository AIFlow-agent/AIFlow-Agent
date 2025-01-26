from web3 import Web3
import time

# Configuration
RPC_URL = "https://bsc-testnet.publicnode.com"
ORACLE_ADDRESS = "0x2E21A40EC3EED82d27ACeBb928A36193Bebb55D6"

# Oracle ABI - just the events we need
ORACLE_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "queryId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "requestS3",
                "type": "string"
            }
        ],
        "name": "QueryCreated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "uint256",
                "name": "queryId",
                "type": "uint256"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "responseS3",
                "type": "string"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "consumedToken",
                "type": "uint256"
            }
        ],
        "name": "QueryFulfilled",
        "type": "event"
    }
]

class QueryMonitor:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not self.w3.is_connected():
            raise Exception("Failed to connect to BSC testnet")
        print("Successfully connected to BSC testnet")
        
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(ORACLE_ADDRESS),
            abi=ORACLE_ABI
        )
        self.last_block = self.w3.eth.block_number

    def monitor_events(self):
        print("Starting to monitor for new queries...")
        print(f"Starting from block {self.last_block}")

        while True:
            try:
                current_block = self.w3.eth.block_number
                if current_block > self.last_block:
                    print(f"\nChecking block {self.last_block + 1}")
                    
                    # Get logs directly
                    logs = self.w3.eth.get_logs({
                        'fromBlock': self.last_block + 1,
                        'toBlock': current_block,
                        'address': self.contract.address
                    })

                    # Process logs
                    for log in logs:
                        try:
                            # Try to decode as QueryCreated
                            event = self.contract.events.QueryCreated().process_log(log)
                            self.print_created_event(event)
                        except:
                            try:
                                # Try to decode as QueryFulfilled
                                event = self.contract.events.QueryFulfilled().process_log(log)
                                self.print_fulfilled_event(event)
                            except:
                                pass
                    
                    self.last_block = current_block
                
                time.sleep(2)  # Poll every 2 seconds
                
            except KeyboardInterrupt:
                print("\nStopping monitor...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(2)
                continue

    def print_created_event(self, event):
        print("\nNew Query Created:")
        print(f"Query ID: {event.args.queryId}")
        print(f"Request S3: {event.args.requestS3}")
        print(f"Block: {event.blockNumber}")
        print(f"Tx Hash: {event.transactionHash.hex()}")
        print("-" * 50)

    def print_fulfilled_event(self, event):
        print("\nQuery Fulfilled:")
        print(f"Query ID: {event.args.queryId}")
        print(f"Response S3: {event.args.responseS3}")
        print(f"Consumed Token: {event.args.consumedToken}")
        print(f"Block: {event.blockNumber}")
        print(f"Tx Hash: {event.transactionHash.hex()}")
        print("-" * 50)

def main():
    monitor = QueryMonitor()
    monitor.monitor_events()

if __name__ == "__main__":
    main() 
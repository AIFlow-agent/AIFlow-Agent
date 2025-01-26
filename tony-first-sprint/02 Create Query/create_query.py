from web3 import Web3
from eth_account import Account
from eth_utils import to_checksum_address
from eth_account.signers.local import LocalAccount
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the directory path of the current script
current_dir = Path(__file__).parent
# Load environment variables from .env file one folder higher
load_dotenv(current_dir.parent / '.env')

# Connect to BSC testnet
web3 = Web3(Web3.HTTPProvider("https://bsc-testnet.publicnode.com"))

# Check connection
if not web3.is_connected():
    print("Failed to connect to BNB testnet")
    exit()
else:
    print("Successfully connected to BSC testnet")

# Contract addresses from environment variables
ORACLE_CONTRACT_ADDRESS = to_checksum_address(os.getenv('ORACLE_CONTRACT_ADDRESS'))
AGENT_CONTRACT_ADDRESS = to_checksum_address("0x97DC31b7749FcCF2E5cA93DDC7E6B14b764a801e")

# Load contract ABI
def load_contract_abi(filename):
    with open(filename) as f:
        contract_abi = json.load(f)
        return contract_abi['abi']

oracle_abi = load_contract_abi('../../../contracts/2025.01/AIFlowOracle.sol/AIFlowOracle.json')

# Initialize contract
oracle_contract = web3.eth.contract(
    address=ORACLE_CONTRACT_ADDRESS,
    abi=oracle_abi
)

def create_query(agent_id: int, request_s3: str, private_key: str):
    """
    Create a query for an AI agent
    """
    try:
        # Get account from private key
        account: LocalAccount = web3.eth.account.from_key(private_key)
        
        print(f"\nBuilding transaction for agent ID: {agent_id}")
        print(f"Request S3: {request_s3}")
        
        # Build transaction
        transaction = oracle_contract.functions.createQuery(
            agent_id,
            request_s3
        ).build_transaction({
            'from': account.address,
            'gas': 200000,  # Increased gas limit
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(account.address),
            'chainId': 97  # BSC testnet chain ID
        })
        
        print("\nTransaction built successfully")
        
        # Sign transaction
        signed_txn = account.sign_transaction(transaction)
        print("Transaction signed successfully")
        
        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"\nTransaction hash: {web3.to_hex(tx_hash)}")
        print("Waiting for confirmation...")
        
        # Wait for transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print("\nTransaction receipt received:")
        print(f"Status: {'Success' if tx_receipt['status'] == 1 else 'Failed'}")
        print(f"Gas used: {tx_receipt['gasUsed']}")
        print(f"Block number: {tx_receipt['blockNumber']}")
        
        # Get QueryCreated event
        query_created_event = oracle_contract.events.QueryCreated().process_receipt(tx_receipt)
        print(f"\nEvents found: {len(query_created_event)}")
        
        if tx_receipt['status'] == 1:
            if query_created_event:
                query_id = query_created_event[0]['args']['queryId']
                print("\n✅ Query created successfully!")
                print(f"Query ID: {query_id}")
                return query_id
            else:
                print("\n⚠️ Transaction successful but no QueryCreated event found")
                # Try to get revert reason
                try:
                    tx = web3.eth.get_transaction(tx_hash)
                    result = web3.eth.call(dict(tx), tx_receipt.blockNumber)
                    print(f"Transaction call result: {result.hex()}")
                except Exception as call_error:
                    print(f"Error getting revert reason: {str(call_error)}")
                raise Exception("Transaction succeeded but no event emitted")
        else:
            raise Exception(f"Transaction failed with status {tx_receipt['status']}")
            
    except Exception as e:
        print(f"\n❌ Detailed error: {str(e)}")
        raise Exception("Query creation failed") from e

def main():
    # Use environment variables for private key and addresses
    private_key = os.getenv('ORACLE_PRIVATE_KEY')
    sender_address = os.getenv('RECIPIENT_ADDRESS_1')
    
    print("\n=== CREATING QUERY ===")
    print(f"From: {sender_address}")
    print(f"Oracle Contract: {ORACLE_CONTRACT_ADDRESS}")
    
    # Example usage with agent ID 0 (first minted agent)
    agent_id = 12  # Changed to 0 since NFT IDs typically start at 0
    
    # Use a valid S3 URL from your bucket
    request_s3 = "s3://aiflow-data/requests/example-request-1.json"  # Update this with your actual S3 bucket
    
    try:
        query_id = create_query(agent_id, request_s3, private_key)
        print(f"\nCreated query with ID: {query_id}")
    except Exception as e:
        print(f"\n❌ Error creating query: {str(e)}")

if __name__ == "__main__":
    main() 
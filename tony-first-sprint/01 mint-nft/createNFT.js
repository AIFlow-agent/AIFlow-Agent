import { ethers } from "ethers";
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Get the directory path of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from the correct path (one directory up)
dotenv.config({ path: join(__dirname, '../.env') });

// Debug logging
console.log("Environment variables loaded:");
console.log("ORACLE_PRIVATE_KEY:", process.env.ORACLE_PRIVATE_KEY ? '[PRESENT]' : '[MISSING]');
console.log("ORACLE_CONTRACT_ADDRESS:", process.env.ORACLE_CONTRACT_ADDRESS ? '[PRESENT]' : '[MISSING]');

// Connect to BSC testnet
const provider = new ethers.JsonRpcProvider("https://bsc-testnet.publicnode.com");

// Wait for provider to be ready
try {
  await provider.ready;
  console.log("Successfully connected to BSC testnet");
} catch (error) {
  console.error("Failed to connect to BSC testnet:", error);
  process.exit(1);
}

// Load wallet from environment variable
const wallet = new ethers.Wallet(process.env.ORACLE_PRIVATE_KEY, provider);

// AIFlowOracle contract address from environment variable
const oracleAddress = process.env.ORACLE_CONTRACT_ADDRESS;

// AIFlowOracle contract ABI (just the createAgent function)
const oracleABI = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "string",
        "name": "tokenUri",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "tokenName",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "tokenSymbol",
        "type": "string"
      }
    ],
    "name": "createAgent",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "agentId",
        "type": "uint256"
      }
    ],
    "name": "agentToken",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint256",
            "name": "agentId",
            "type": "uint256"
          },
          {
            "internalType": "address",
            "name": "tokenContract",
            "type": "address"
          }
        ],
        "internalType": "struct AIFlowOracle.AgentToken",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "agentId",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "mintToken",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "uint256",
        "name": "tokenId",
        "type": "uint256"
      }
    ],
    "name": "Transfer",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "name": "agents",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "agentId",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "nftId",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "tokenContract",
        "type": "address"
      },
      {
        "internalType": "bool",
        "name": "isActive",
        "type": "bool"
      },
      {
        "internalType": "uint256",
        "name": "createdAt",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "name",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "symbol",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
];

const contract = new ethers.Contract(oracleAddress, oracleABI, wallet);

// Add this to the oracleABI array:
const tokenABI = [
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "balanceOf",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "Transfer",
    "type": "event"
  }
];

async function main() {
  console.log("\n🚀 STARTING AI AGENT DEPLOYMENT");
  console.log("================================================");
  console.log("Network: BSC Testnet");
  console.log("Oracle Contract:", oracleAddress);
  console.log("Wallet Address:", wallet.address);

  try {
    // Step 1: Create NFT Agent
    const recipientAddress = wallet.address;
    const tokenUri = "https://raw.githubusercontent.com/your-repo/metadata/nft1.json";
    const tokenName = "AI Assistant Agent";
    const tokenSymbol = "AIAA";

    console.log("\n=== CREATING AI AGENT NFT ===");
    console.log("Owner:", recipientAddress);
    console.log("Token Name:", tokenName);
    console.log("Token Symbol:", tokenSymbol);
    console.log("Metadata URI:", tokenUri);

    const agentId = await createAgent(recipientAddress, tokenUri, tokenName, tokenSymbol);
    console.log("\n✅ Agent created successfully with ID:", agentId);

    // Step 2: Set up token distribution
    const address1 = process.env.RECIPIENT_ADDRESS_1;
    const address2 = process.env.RECIPIENT_ADDRESS_2;
    const totalSupply = ethers.parseEther("1000000"); // 1 million tokens
    const halfSupply = totalSupply / 2n;

    console.log("\n=== TOKEN DISTRIBUTION PLAN ===");
    console.log(`Total Supply: ${ethers.formatEther(totalSupply)} tokens`);
    console.log(`First Recipient (${address1}): ${ethers.formatEther(halfSupply)} tokens`);
    console.log(`Second Recipient (${address2}): ${ethers.formatEther(halfSupply)} tokens`);

    // Step 3: Distribute tokens
    console.log("\n=== DISTRIBUTING TOKENS ===");
    
    // First distribution
    console.log("\nSending first distribution...");
    const tx1 = await contract.mintToken(agentId, address1, halfSupply);
    console.log("Transaction hash:", tx1.hash);
    await tx1.wait();
    console.log("✅ First distribution complete");

    // Second distribution
    console.log("\nSending second distribution...");
    const tx2 = await contract.mintToken(agentId, address2, halfSupply);
    console.log("Transaction hash:", tx2.hash);
    await tx2.wait();
    console.log("✅ Second distribution complete");

    console.log("\n=== PROCESS COMPLETE ===");
    console.log("Agent ID:", agentId);
    console.log("Total Supply:", ethers.formatEther(totalSupply), "tokens");
    console.log(`Distributed ${ethers.formatEther(halfSupply)} tokens each to:`);
    console.log(`- ${address1}`);
    console.log(`- ${address2}`);
    console.log("================================================");

  } catch (error) {
    console.error("\n❌ Deployment failed:");
    console.error(error);
    process.exit(1);
  }
}

// Helper function to create agent and return agent ID
async function createAgent(to, tokenUri, tokenName, tokenSymbol) {
  const tx = await contract.createAgent(to, tokenUri, tokenName, tokenSymbol);
  console.log("Transaction hash:", tx.hash);
  
  const receipt = await tx.wait();
  
  // Find the Transfer event to get the agent ID
  for (const log of receipt.logs) {
    if (log.topics.length === 4 && 
        log.topics[0] === '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef') {
      return BigInt(log.topics[3]).toString();
    }
  }
  throw new Error("Could not find Transfer event in transaction logs");
}

// Execute main function
main().catch((error) => {
  console.error(error);
  process.exit(1);
});

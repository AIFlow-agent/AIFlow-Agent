# AI Flow Smart Contracts Documentation

## Deployment Information

### BNB Testnet Addresses
- **AIFlowAgent (NFT, ERC721)**: `0x97DC31b7749FcCF2E5cA93DDC7E6B14b764a801e`
- **AIFlowOracle**: `0x2E21A40EC3EED82d27ACeBb928A36193Bebb55D6`
- **AIFlowAgentToken**: Dynamically created during createAgent

### Contract Owner Information
- **AIFlowOracle Owner Private Key (BNB testnet)**: `584c100dee430e60c4c0a0a4c76341a01fe536df0d4ccefaa8851eda467d36d2`

## AIFlowAgent Contract

The AIFlowAgent contract is an ERC-721 NFT contract that represents AI agents in the system.

### Key Features:
- Implements ERC-721 standard for non-fungible tokens
- Each token represents a unique AI agent
- Includes standard NFT functionality like transfers and approvals
- Owned by a single owner address that can mint new tokens
- Tokens have associated metadata URIs

### Main Functions:
- safeMint(address to, string uri): Mints a new agent NFT to the specified address with metadata URI
- tokenURI(uint256 tokenId): Gets the metadata URI for a specific token
- ownerOf(uint256 tokenId): Gets the current owner of a token
- transferFrom/safeTransferFrom: Standard NFT transfer functions
- approve/setApprovalForAll: Standard NFT approval functions

## AIFlowAgentToken Contract 

The AIFlowAgentToken contract is an ERC-20 token contract that represents utility tokens for AI agents.

### Key Features:
- Implements ERC-20 standard for fungible tokens
- Configurable name and symbol
- Owned by a single owner address that can mint new tokens
- Includes burn functionality to destroy tokens
- Standard token transfer and approval functionality

### Main Functions:
- mint(address to, uint256 amount): Mints new tokens to an address
- burn(uint256 value): Burns tokens from sender's balance
- burnFrom(address account, uint256 value): Burns tokens from an approved account
- transfer/transferFrom: Standard token transfer functions
- approve: Standard token approval function
- balanceOf: Gets token balance of an address

## AIFlowOracle Contract

The AIFlowOracle contract manages the interaction between AI agents and queries.

### Key Features:
- Creates and manages AI agents
- Handles query creation and fulfillment
- Manages token minting for agents
- Tracks query status and responses
- Emits events for query lifecycle

### Main Functions:
- createAgent(address to, string tokenUri, string tokenName, string tokenSymbol): Creates a new AI agent
- createQuery(uint256 agentId, string requestS3): Creates a new query for an agent
- fullfillQuery(uint256 agentId, uint256 queryId, string responseS3, uint256 consumedToken): Fulfills a query with response
- mintToken(uint256 agentId, address to, uint256 amount): Mints utility tokens for an agent
- getQuery(uint256 queryId): Gets details of a specific query
- tokenOf(address tokenAddress): Gets agent ID associated with a token address

### Events:
- QueryCreated: Emitted when a new query is created
- QueryFulfilled: Emitted when a query is fulfilled with response

The contracts work together to create a system where:
1. AI agents are represented as NFTs (AIFlowAgent)
2. Each agent has associated utility tokens (AIFlowAgentToken)
3. Users can create queries for agents and receive responses (AIFlowOracle)

The system uses a combination of NFTs and utility tokens to manage AI agent ownership and usage.

/**
 *  Utilities for common tasks involving hashing. Also see
 *  [cryptographic hashing](about-crypto-hashing).
 *
 *  @_section: api/hashing:Hashing Utilities  [about-hashing]
 */
export { id } from "../../src.ts/hash/id.js";
export { ensNormalize, isValidName, namehash, dnsEncode } from "../../src.ts/hash/namehash.js";
export { hashMessage, verifyMessage } from "../../src.ts/hash/message.js";
export { solidityPacked, solidityPackedKeccak256, solidityPackedSha256 } from "../../src.ts/hash/solidity.js";
export { TypedDataEncoder, verifyTypedData } from "../../src.ts/hash/typed-data.js";
export type { TypedDataDomain, TypedDataField } from "../../src.ts/hash/typed-data.js";
//# sourceMappingURL=index.d.ts.map
/**
 *  A fundamental building block of Ethereum is the underlying
 *  cryptographic primitives.
 *
 *  @_section: api/crypto:Cryptographic Functions   [about-crypto]
 */
import { computeHmac } from "../../src.ts/crypto/hmac.js";
import { keccak256 } from "../../src.ts/crypto/keccak.js";
import { ripemd160 } from "../../src.ts/crypto/ripemd160.js";
import { pbkdf2 } from "../../src.ts/crypto/pbkdf2.js";
import { randomBytes } from "../../src.ts/crypto/random.js";
import { scrypt, scryptSync } from "../../src.ts/crypto/scrypt.js";
import { sha256, sha512 } from "../../src.ts/crypto/sha2.js";
export { computeHmac, randomBytes, keccak256, ripemd160, sha256, sha512, pbkdf2, scrypt, scryptSync };
export { SigningKey } from "../../src.ts/crypto/signing-key.js";
export { Signature } from "../../src.ts/crypto/signature.js";
/**
 *  Once called, prevents any future change to the underlying cryptographic
 *  primitives using the ``.register`` feature for hooks.
 */
declare function lock(): void;
export { lock };
export type { ProgressCallback } from "../../src.ts/crypto/scrypt.js";
export type { SignatureLike } from "../../src.ts/crypto/signature.js";
//# sourceMappingURL=index.d.ts.map
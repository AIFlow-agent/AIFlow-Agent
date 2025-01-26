import { SigningKey } from "../../src.ts/crypto/index.js";
import type { SignatureLike } from "../../src.ts/crypto/index.js";
import type { BytesLike } from "../../src.ts/utils/index.js";
/**
 *  Returns the address for the %%key%%.
 *
 *  The key may be any standard form of public key or a private key.
 */
export declare function computeAddress(key: string | SigningKey): string;
/**
 *  Returns the recovered address for the private key that was
 *  used to sign %%digest%% that resulted in %%signature%%.
 */
export declare function recoverAddress(digest: BytesLike, signature: SignatureLike): string;
//# sourceMappingURL=address.d.ts.map
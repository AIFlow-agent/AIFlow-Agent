/**
 *  When interacting with Ethereum, it is necessary to use a private
 *  key authenticate actions by signing a payload.
 *
 *  Wallets are the simplest way to expose the concept of an
 *  //Externally Owner Account// (EOA) as it wraps a private key
 *  and supports high-level methods to sign common types of interaction
 *  and send transactions.
 *
 *  The class most developers will want to use is [[Wallet]], which
 *  can load a private key directly or from any common wallet format.
 *
 *  The [[HDNodeWallet]] can be used when it is necessary to access
 *  low-level details of how an HD wallets are derived, exported
 *  or imported.
 *
 *  @_section: api/wallet:Wallets  [about-wallets]
 */
export { BaseWallet } from "../../src.ts/wallet/base-wallet.js";
export { defaultPath, getAccountPath, getIndexedAccountPath, HDNodeWallet, HDNodeVoidWallet, } from "../../src.ts/wallet/hdwallet.js";
export { isCrowdsaleJson, decryptCrowdsaleJson } from "../../src.ts/wallet/json-crowdsale.js";
export { isKeystoreJson, decryptKeystoreJsonSync, decryptKeystoreJson, encryptKeystoreJson, encryptKeystoreJsonSync } from "../../src.ts/wallet/json-keystore.js";
export { Mnemonic } from "../../src.ts/wallet/mnemonic.js";
export { Wallet } from "../../src.ts/wallet/wallet.js";
export type { CrowdsaleAccount } from "../../src.ts/wallet/json-crowdsale.js";
export type { KeystoreAccount, EncryptOptions } from "../../src.ts/wallet/json-keystore.js";
//# sourceMappingURL=index.d.ts.map
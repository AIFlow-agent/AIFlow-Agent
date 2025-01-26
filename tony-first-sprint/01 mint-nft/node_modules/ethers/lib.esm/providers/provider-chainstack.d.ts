/**
 *  [[link-chainstack]] provides a third-party service for connecting to
 *  various blockchains over JSON-RPC.
 *
 *  **Supported Networks**
 *
 *  - Ethereum Mainnet (``mainnet``)
 *  - Arbitrum (``arbitrum``)
 *  - BNB Smart Chain Mainnet (``bnb``)
 *  - Polygon (``matic``)
 *
 *  @_subsection: api/providers/thirdparty:Chainstack  [providers-chainstack]
 */
import { FetchRequest } from "../../src.ts/utils/index.js";
import { Network } from "../../src.ts/providers/network.js";
import { JsonRpcProvider } from "../../src.ts/providers/provider-jsonrpc.js";
import type { AbstractProvider } from "../../src.ts/providers/abstract-provider.js";
import type { CommunityResourcable } from "../../src.ts/providers/community.js";
import type { Networkish } from "../../src.ts/providers/network.js";
/**
 *  The **ChainstackProvider** connects to the [[link-chainstack]]
 *  JSON-RPC end-points.
 *
 *  By default, a highly-throttled API key is used, which is
 *  appropriate for quick prototypes and simple scripts. To
 *  gain access to an increased rate-limit, it is highly
 *  recommended to [sign up here](link-chainstack).
 */
export declare class ChainstackProvider extends JsonRpcProvider implements CommunityResourcable {
    /**
     *  The API key for the Chainstack connection.
     */
    readonly apiKey: string;
    /**
     *  Creates a new **ChainstackProvider**.
     */
    constructor(_network?: Networkish, apiKey?: null | string);
    _getProvider(chainId: number): AbstractProvider;
    isCommunityResource(): boolean;
    /**
     *  Returns a prepared request for connecting to %%network%%
     *  with %%apiKey%% and %%projectSecret%%.
     */
    static getRequest(network: Network, apiKey?: null | string): FetchRequest;
}
//# sourceMappingURL=provider-chainstack.d.ts.map
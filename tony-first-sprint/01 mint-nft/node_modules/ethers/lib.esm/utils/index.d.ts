/**
 *  There are many simple utilities required to interact with
 *  Ethereum and to simplify the library, without increasing
 *  the library dependencies for simple functions.
 *
 *  @_section api/utils:Utilities  [about-utils]
 */
export { decodeBase58, encodeBase58 } from "../../src.ts/utils/base58.js";
export { decodeBase64, encodeBase64 } from "../../src.ts/utils/base64.js";
export { getBytes, getBytesCopy, isHexString, isBytesLike, hexlify, concat, dataLength, dataSlice, stripZerosLeft, zeroPadValue, zeroPadBytes } from "../../src.ts/utils/data.js";
export { isCallException, isError, assert, assertArgument, assertArgumentCount, assertPrivate, assertNormalize, makeError } from "../../src.ts/utils/errors.js";
export { EventPayload } from "../../src.ts/utils/events.js";
export { FetchRequest, FetchResponse, FetchCancelSignal, } from "../../src.ts/utils/fetch.js";
export { FixedNumber } from "../../src.ts/utils/fixednumber.js";
export { fromTwos, toTwos, mask, getBigInt, getNumber, getUint, toBigInt, toNumber, toBeHex, toBeArray, toQuantity } from "../../src.ts/utils/maths.js";
export { resolveProperties, defineProperties } from "../../src.ts/utils/properties.js";
export { decodeRlp } from "../../src.ts/utils/rlp-decode.js";
export { encodeRlp } from "../../src.ts/utils/rlp-encode.js";
export { formatEther, parseEther, formatUnits, parseUnits } from "../../src.ts/utils/units.js";
export { toUtf8Bytes, toUtf8CodePoints, toUtf8String, Utf8ErrorFuncs, } from "../../src.ts/utils/utf8.js";
export { uuidV4 } from "../../src.ts/utils/uuid.js";
export type { BytesLike } from "../../src.ts/utils/data.js";
export type { ErrorCode, EthersError, UnknownError, NotImplementedError, UnsupportedOperationError, NetworkError, ServerError, TimeoutError, BadDataError, CancelledError, BufferOverrunError, NumericFaultError, InvalidArgumentError, MissingArgumentError, UnexpectedArgumentError, CallExceptionError, InsufficientFundsError, NonceExpiredError, OffchainFaultError, ReplacementUnderpricedError, TransactionReplacedError, UnconfiguredNameError, ActionRejectedError, CallExceptionAction, CallExceptionTransaction, CodedEthersError } from "../../src.ts/utils/errors.js";
export type { EventEmitterable, Listener } from "../../src.ts/utils/events.js";
export type { GetUrlResponse, FetchPreflightFunc, FetchProcessFunc, FetchRetryFunc, FetchGatewayFunc, FetchGetUrlFunc } from "../../src.ts/utils/fetch.js";
export type { FixedFormat } from "../../src.ts/utils/fixednumber.js";
export type { BigNumberish, Numeric } from "../../src.ts/utils/maths.js";
export type { RlpStructuredData, RlpStructuredDataish } from "../../src.ts/utils/rlp.js";
export type { Utf8ErrorFunc, UnicodeNormalizationForm, Utf8ErrorReason } from "../../src.ts/utils/utf8.js";
//# sourceMappingURL=index.d.ts.map
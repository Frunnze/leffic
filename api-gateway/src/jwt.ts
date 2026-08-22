import crypto from 'crypto';

const VALID = 'ok';
const INVALID = 'invalid';
const BEARER_PREFIX = 'bearer ';
const MILLISECONDS_PER_SECOND = 1000;
const SIGNING_ALGORITHM = 'sha256';

type SignedToken = {
    signingInput: string;
    signature: string;
    encodedClaims: string;
};

function bearerToken(header: string | undefined): string | null {
    if (header === undefined) return null;
    if (!header.toLowerCase().startsWith(BEARER_PREFIX)) return null;

    return header.slice(BEARER_PREFIX.length);
}

function signedToken(token: string): SignedToken | null {
    const firstDot = token.indexOf('.');
    const lastDot = token.lastIndexOf('.');

    if (firstDot <= 0) return null;

    return {
        signingInput: token.slice(0, lastDot),
        signature: token.slice(lastDot + 1),
        encodedClaims: token.slice(firstDot + 1, lastDot),
    };
}

function equalsInConstantTime(left: string, right: string): boolean {
    if (left.length !== right.length) return false;

    let difference = 0;
    let index = 0;

    for (const character of left) {
        difference |= character.charCodeAt(0) ^ right.charCodeAt(index);
        index += 1;
    }

    return difference === 0;
}

function signatureMatches(signed: SignedToken, secret: string): boolean {
    const expected = crypto
        .createHmac(SIGNING_ALGORITHM, secret)
        .update(signed.signingInput)
        .digest('base64url');

    return equalsInConstantTime(expected, signed.signature);
}

function hasExpired(encodedClaims: string): boolean {
    let claims: { exp?: unknown };

    try {
        claims = JSON.parse(
            Buffer.from(encodedClaims, 'base64url').toString()
        ) as { exp?: unknown };
    } catch {
        return true;
    }

    if (typeof claims.exp !== 'number') return false;

    return Date.now() / MILLISECONDS_PER_SECOND >= claims.exp;
}

function status(request: NginxHTTPRequest): string {
    const secret = process.env['JWT_SECRET_KEY'];

    if (secret === undefined || secret.length === 0) {
        request.error('JWT_SECRET_KEY is not set');
        return INVALID;
    }

    const token = bearerToken(request.headersIn.Authorization);

    if (token === null) return INVALID;

    const signed = signedToken(token);

    if (signed === null) return INVALID;
    if (!signatureMatches(signed, secret)) return INVALID;
    if (hasExpired(signed.encodedClaims)) return INVALID;

    return VALID;
}

export default { status };

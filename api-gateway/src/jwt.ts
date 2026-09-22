import crypto from 'crypto';

const BEARER_PREFIX = 'bearer ';
const MILLISECONDS_PER_SECOND = 1000;
const SIGNING_ALGORITHM = 'sha256';
const PREFLIGHT_METHOD = 'OPTIONS';
const PREFLIGHT_STATUS = 204;
const REFUSED_TOKEN_STATUS = 401;

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

function hasVerifiedToken(request: NginxHTTPRequest): boolean {
    const secret = process.env['JWT_SECRET_KEY'];

    if (secret === undefined || secret.length === 0) {
        request.error('JWT_SECRET_KEY is not set');
        return false;
    }

    const token = bearerToken(request.headersIn.Authorization);

    if (token === null) return false;

    const signed = signedToken(token);

    if (signed === null) return false;
    if (!signatureMatches(signed, secret)) return false;

    return !hasExpired(signed.encodedClaims);
}

function guardPublicRoute(request: NginxHTTPRequest): void {
    if (request.method === PREFLIGHT_METHOD) {
        request.return(PREFLIGHT_STATUS);
    }
}

function guardProtectedRoute(request: NginxHTTPRequest): void {
    if (request.method === PREFLIGHT_METHOD) {
        request.return(PREFLIGHT_STATUS);
        return;
    }

    if (!hasVerifiedToken(request)) {
        request.return(REFUSED_TOKEN_STATUS);
    }
}

export default { guardPublicRoute, guardProtectedRoute };

import crypto from 'crypto';

const VALID = 'ok';
const INVALID = 'invalid';
const BEARER_SCHEME = 'bearer';
const BEARER_PARTS = 2;
const TOKEN_PARTS = 3;
const MILLISECONDS_PER_SECOND = 1000;
const SIGNING_ALGORITHM = 'sha256';

class JwtGate {
    static status(request: NginxHTTPRequest): string {
        const secret = process.env['JWT_SECRET_KEY'];

        if (secret === undefined || secret.length === 0) {
            request.error('JWT_SECRET_KEY is not set');
            return INVALID;
        }

        const token = JwtGate.bearerToken(request.headersIn['Authorization']);

        if (token === null) return INVALID;

        const parts = token.split('.');

        if (parts.length !== TOKEN_PARTS) return INVALID;
        if (!JwtGate.signatureMatches(parts, secret)) return INVALID;
        if (JwtGate.hasExpired(parts[1])) return INVALID;

        return VALID;
    }

    static signatureMatches(parts: string[], secret: string): boolean {
        const signingInput = parts[0] + '.' + parts[1];
        const expected = crypto
            .createHmac(SIGNING_ALGORITHM, secret)
            .update(signingInput)
            .digest('base64url');

        return JwtGate.equalsInConstantTime(expected, parts[2]);
    }

    static bearerToken(header: string | undefined): string | null {
        if (header === undefined) return null;

        const parts = header.split(' ');

        if (parts.length !== BEARER_PARTS) return null;
        if (parts[0].toLowerCase() !== BEARER_SCHEME) return null;

        return parts[1];
    }

    static hasExpired(encodedClaims: string): boolean {
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

    static equalsInConstantTime(left: string, right: string): boolean {
        if (left.length !== right.length) return false;

        let difference = 0;

        for (let index = 0; index < left.length; index += 1) {
            difference |= left.charCodeAt(index) ^ right.charCodeAt(index);
        }

        return difference === 0;
    }
}

export default { status: JwtGate.status };

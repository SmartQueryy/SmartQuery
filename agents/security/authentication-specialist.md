# Authentication Specialist

## Role

Authentication and identity management specialist focused on implementing secure, user-friendly authentication systems for SaaS applications including SSO, MFA, and session management.

## Context

Use this agent when implementing authentication flows, integrating identity providers, setting up SSO, configuring MFA, managing sessions, or troubleshooting auth issues in SaaS applications.

## Core Responsibilities

- Design authentication architectures
- Implement OAuth 2.0 / OIDC flows
- Configure SSO integrations
- Set up multi-factor authentication
- Manage session security
- Handle identity federation

## Authentication Architecture

### SaaS Auth Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Request                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               Authentication Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐    │
│  │   Email/    │ │   Social    │ │  Enterprise     │    │
│  │  Password   │ │   OAuth     │ │    SSO          │    │
│  └─────────────┘ └─────────────┘ └─────────────────┘    │
│                        │                                 │
│                        ▼                                 │
│              ┌─────────────────┐                        │
│              │   MFA Layer     │                        │
│              │ (TOTP/SMS/Keys) │                        │
│              └─────────────────┘                        │
│                        │                                 │
│                        ▼                                 │
│              ┌─────────────────┐                        │
│              │ Session Manager │                        │
│              └─────────────────┘                        │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Authorization Layer (RBAC)                  │
└─────────────────────────────────────────────────────────┘
```

### Auth Provider Comparison

```
┌────────────────┬──────────┬──────────┬─────────┬──────────┐
│ Provider       │ Best For │ Pricing  │ SSO     │ MFA      │
├────────────────┼──────────┼──────────┼─────────┼──────────┤
│ Clerk          │ Quick    │ Free tier│ Yes     │ Yes      │
│                │ setup    │ + usage  │         │          │
├────────────────┼──────────┼──────────┼─────────┼──────────┤
│ Auth0          │ Enterprise│ MAU     │ Yes     │ Yes      │
│                │ features │ based    │         │          │
├────────────────┼──────────┼──────────┼─────────┼──────────┤
│ Supabase Auth  │ Full     │ Included │ Limited │ Yes      │
│                │ stack    │ w/ DB    │         │          │
├────────────────┼──────────┼──────────┼─────────┼──────────┤
│ NextAuth.js    │ Custom   │ Free     │ Manual  │ Manual   │
│                │ control  │          │         │          │
├────────────────┼──────────┼──────────┼─────────┼──────────┤
│ WorkOS         │ Enterprise│ Per SSO │ Yes     │ Yes      │
│                │ SSO      │ connection│        │          │
└────────────────┴──────────┴──────────┴─────────┴──────────┘
```

## OAuth 2.0 / OIDC Implementation

### Authorization Code Flow (Recommended)

```typescript
// OAuth 2.0 Authorization Code Flow with PKCE
import crypto from "crypto";

// Step 1: Generate PKCE values
function generatePKCE() {
  const codeVerifier = crypto.randomBytes(32).toString("base64url");

  const codeChallenge = crypto
    .createHash("sha256")
    .update(codeVerifier)
    .digest("base64url");

  return { codeVerifier, codeChallenge };
}

// Step 2: Build authorization URL
function buildAuthUrl(provider: "google" | "github", state: string) {
  const { codeVerifier, codeChallenge } = generatePKCE();

  // Store codeVerifier in session for later
  storeInSession("pkce_verifier", codeVerifier);
  storeInSession("oauth_state", state);

  const params = new URLSearchParams({
    client_id: process.env[`${provider.toUpperCase()}_CLIENT_ID`]!,
    redirect_uri: `${process.env.APP_URL}/auth/callback/${provider}`,
    response_type: "code",
    scope: provider === "google" ? "openid email profile" : "read:user user:email",
    state,
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
  });

  const baseUrl =
    provider === "google"
      ? "https://accounts.google.com/o/oauth2/v2/auth"
      : "https://github.com/login/oauth/authorize";

  return `${baseUrl}?${params.toString()}`;
}

// Step 3: Handle callback
async function handleOAuthCallback(
  provider: string,
  code: string,
  state: string
) {
  // Verify state
  const storedState = getFromSession("oauth_state");
  if (state !== storedState) {
    throw new Error("Invalid state parameter");
  }

  // Exchange code for tokens
  const codeVerifier = getFromSession("pkce_verifier");

  const tokenResponse = await fetch(getTokenUrl(provider), {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: `${process.env.APP_URL}/auth/callback/${provider}`,
      client_id: process.env[`${provider.toUpperCase()}_CLIENT_ID`]!,
      client_secret: process.env[`${provider.toUpperCase()}_CLIENT_SECRET`]!,
      code_verifier: codeVerifier,
    }),
  });

  const tokens = await tokenResponse.json();

  // Verify ID token and get user info
  const userInfo = await getUserInfo(provider, tokens.access_token);

  return { tokens, userInfo };
}
```

### JWT Token Management

```typescript
import jwt from "jsonwebtoken";

interface TokenPayload {
  sub: string; // User ID
  email: string;
  orgId: string;
  role: string;
  permissions: string[];
}

class TokenService {
  private accessSecret = process.env.JWT_ACCESS_SECRET!;
  private refreshSecret = process.env.JWT_REFRESH_SECRET!;

  // Short-lived access token (15 min)
  createAccessToken(payload: TokenPayload): string {
    return jwt.sign(payload, this.accessSecret, {
      expiresIn: "15m",
      issuer: "your-app",
      audience: "your-app-api",
    });
  }

  // Long-lived refresh token (7 days)
  createRefreshToken(userId: string): string {
    const tokenId = crypto.randomUUID();

    // Store token ID in database for revocation
    this.storeRefreshToken(userId, tokenId);

    return jwt.sign({ sub: userId, jti: tokenId }, this.refreshSecret, {
      expiresIn: "7d",
    });
  }

  // Verify access token
  verifyAccessToken(token: string): TokenPayload {
    return jwt.verify(token, this.accessSecret, {
      issuer: "your-app",
      audience: "your-app-api",
    }) as TokenPayload;
  }

  // Refresh tokens
  async refreshTokens(refreshToken: string) {
    const decoded = jwt.verify(refreshToken, this.refreshSecret) as {
      sub: string;
      jti: string;
    };

    // Check if refresh token is still valid (not revoked)
    const isValid = await this.isRefreshTokenValid(decoded.sub, decoded.jti);
    if (!isValid) {
      throw new Error("Refresh token revoked");
    }

    // Rotate refresh token
    await this.revokeRefreshToken(decoded.sub, decoded.jti);

    // Get fresh user data
    const user = await this.getUser(decoded.sub);

    return {
      accessToken: this.createAccessToken({
        sub: user.id,
        email: user.email,
        orgId: user.organizationId,
        role: user.role,
        permissions: user.permissions,
      }),
      refreshToken: this.createRefreshToken(user.id),
    };
  }

  // Revoke all tokens for user (logout everywhere)
  async revokeAllTokens(userId: string) {
    await db.refreshToken.deleteMany({ where: { userId } });
  }
}
```

## SSO Implementation

### SAML SSO with WorkOS

```typescript
import WorkOS from "@workos-inc/node";

const workos = new WorkOS(process.env.WORKOS_API_KEY);

// Get SSO authorization URL
async function getSSOUrl(organizationId: string) {
  const authorizationURL = workos.sso.getAuthorizationURL({
    organization: organizationId,
    redirectURI: `${process.env.APP_URL}/auth/sso/callback`,
    state: generateSecureState(),
  });

  return authorizationURL;
}

// Handle SSO callback
async function handleSSOCallback(code: string) {
  const { profile } = await workos.sso.getProfileAndToken({
    code,
    clientID: process.env.WORKOS_CLIENT_ID!,
  });

  // Find or create user
  let user = await db.user.findUnique({
    where: { email: profile.email },
  });

  if (!user) {
    user = await db.user.create({
      data: {
        email: profile.email,
        name: profile.first_name
          ? `${profile.first_name} ${profile.last_name}`
          : profile.email,
        ssoProviderId: profile.connection_id,
        organizationId: profile.organization_id,
      },
    });
  }

  return user;
}

// Admin: Create SSO connection
async function createSSOConnection(
  organizationId: string,
  domain: string,
  provider: "okta" | "azure" | "google"
) {
  const connection = await workos.sso.createConnection({
    organizationId,
    type: provider,
  });

  // Return setup instructions for customer IT admin
  return {
    connectionId: connection.id,
    acsUrl: connection.saml?.acsUrl,
    entityId: connection.saml?.entityId,
    certificate: connection.saml?.certificate,
  };
}
```

### OIDC SSO Implementation

```typescript
// Generic OIDC SSO provider
interface OIDCConfig {
  issuer: string;
  clientId: string;
  clientSecret: string;
  redirectUri: string;
}

class OIDCSSOProvider {
  private config: OIDCConfig;
  private discoveryDocument: any;

  constructor(config: OIDCConfig) {
    this.config = config;
  }

  async initialize() {
    // Fetch OIDC discovery document
    const response = await fetch(
      `${this.config.issuer}/.well-known/openid-configuration`
    );
    this.discoveryDocument = await response.json();
  }

  getAuthorizationUrl(state: string, nonce: string) {
    const params = new URLSearchParams({
      client_id: this.config.clientId,
      redirect_uri: this.config.redirectUri,
      response_type: "code",
      scope: "openid email profile",
      state,
      nonce,
    });

    return `${this.discoveryDocument.authorization_endpoint}?${params}`;
  }

  async exchangeCode(code: string) {
    const response = await fetch(this.discoveryDocument.token_endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code,
        redirect_uri: this.config.redirectUri,
        client_id: this.config.clientId,
        client_secret: this.config.clientSecret,
      }),
    });

    return response.json();
  }

  async verifyIdToken(idToken: string, nonce: string) {
    // Fetch JWKS
    const jwksResponse = await fetch(this.discoveryDocument.jwks_uri);
    const jwks = await jwksResponse.json();

    // Verify token signature and claims
    const decoded = jwt.verify(idToken, jwks, {
      issuer: this.config.issuer,
      audience: this.config.clientId,
    });

    // Verify nonce
    if (decoded.nonce !== nonce) {
      throw new Error("Invalid nonce");
    }

    return decoded;
  }
}
```

## Multi-Factor Authentication

### TOTP Implementation

```typescript
import * as OTPAuth from "otpauth";
import QRCode from "qrcode";

class MFAService {
  // Generate TOTP secret for user
  async setupTOTP(userId: string, email: string) {
    const secret = new OTPAuth.Secret({ size: 20 });

    const totp = new OTPAuth.TOTP({
      issuer: "YourApp",
      label: email,
      algorithm: "SHA1",
      digits: 6,
      period: 30,
      secret,
    });

    // Store secret (encrypted) for user
    await db.mfaSecret.create({
      data: {
        userId,
        secret: encrypt(secret.base32),
        type: "totp",
        verified: false,
      },
    });

    // Generate QR code
    const qrCode = await QRCode.toDataURL(totp.toString());

    return {
      secret: secret.base32, // Show once for manual entry
      qrCode,
    };
  }

  // Verify TOTP code and enable MFA
  async verifyAndEnableTOTP(userId: string, code: string) {
    const mfaRecord = await db.mfaSecret.findFirst({
      where: { userId, type: "totp", verified: false },
    });

    if (!mfaRecord) {
      throw new Error("No pending MFA setup");
    }

    const secret = decrypt(mfaRecord.secret);

    const totp = new OTPAuth.TOTP({
      algorithm: "SHA1",
      digits: 6,
      period: 30,
      secret: OTPAuth.Secret.fromBase32(secret),
    });

    const delta = totp.validate({ token: code, window: 1 });

    if (delta === null) {
      throw new Error("Invalid code");
    }

    // Generate recovery codes
    const recoveryCodes = this.generateRecoveryCodes();

    // Save recovery codes (hashed)
    await db.recoveryCode.createMany({
      data: recoveryCodes.map((code) => ({
        userId,
        codeHash: hashCode(code),
      })),
    });

    // Mark MFA as verified
    await db.mfaSecret.update({
      where: { id: mfaRecord.id },
      data: { verified: true },
    });

    await db.user.update({
      where: { id: userId },
      data: { mfaEnabled: true },
    });

    return { recoveryCodes };
  }

  // Verify TOTP during login
  async verifyTOTP(userId: string, code: string) {
    const mfaRecord = await db.mfaSecret.findFirst({
      where: { userId, type: "totp", verified: true },
    });

    if (!mfaRecord) {
      throw new Error("MFA not configured");
    }

    const secret = decrypt(mfaRecord.secret);

    const totp = new OTPAuth.TOTP({
      algorithm: "SHA1",
      digits: 6,
      period: 30,
      secret: OTPAuth.Secret.fromBase32(secret),
    });

    const delta = totp.validate({ token: code, window: 1 });

    if (delta === null) {
      // Check recovery codes
      return this.verifyRecoveryCode(userId, code);
    }

    return true;
  }

  // Generate recovery codes
  private generateRecoveryCodes(count = 10): string[] {
    return Array.from({ length: count }, () =>
      crypto.randomBytes(4).toString("hex").toUpperCase()
    );
  }

  // Use recovery code (one-time use)
  private async verifyRecoveryCode(
    userId: string,
    code: string
  ): Promise<boolean> {
    const codeHash = hashCode(code);

    const recoveryCode = await db.recoveryCode.findFirst({
      where: { userId, codeHash, usedAt: null },
    });

    if (!recoveryCode) {
      return false;
    }

    // Mark as used
    await db.recoveryCode.update({
      where: { id: recoveryCode.id },
      data: { usedAt: new Date() },
    });

    return true;
  }
}
```

### WebAuthn / Passkeys

```typescript
import {
  generateRegistrationOptions,
  verifyRegistrationResponse,
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
} from "@simplewebauthn/server";

const rpName = "Your App";
const rpID = "yourapp.com";
const origin = `https://${rpID}`;

class PasskeyService {
  // Start passkey registration
  async startRegistration(user: { id: string; email: string }) {
    const existingCredentials = await db.passkey.findMany({
      where: { userId: user.id },
    });

    const options = await generateRegistrationOptions({
      rpName,
      rpID,
      userID: user.id,
      userName: user.email,
      attestationType: "none",
      excludeCredentials: existingCredentials.map((cred) => ({
        id: cred.credentialId,
        type: "public-key",
      })),
      authenticatorSelection: {
        residentKey: "preferred",
        userVerification: "preferred",
      },
    });

    // Store challenge for verification
    await storeChallenge(user.id, options.challenge);

    return options;
  }

  // Complete passkey registration
  async finishRegistration(userId: string, response: any) {
    const expectedChallenge = await getChallenge(userId);

    const verification = await verifyRegistrationResponse({
      response,
      expectedChallenge,
      expectedOrigin: origin,
      expectedRPID: rpID,
    });

    if (!verification.verified || !verification.registrationInfo) {
      throw new Error("Verification failed");
    }

    const { credentialPublicKey, credentialID, counter } =
      verification.registrationInfo;

    // Store passkey
    await db.passkey.create({
      data: {
        userId,
        credentialId: Buffer.from(credentialID),
        publicKey: Buffer.from(credentialPublicKey),
        counter,
        deviceType: verification.registrationInfo.credentialDeviceType,
        backedUp: verification.registrationInfo.credentialBackedUp,
      },
    });

    return { verified: true };
  }

  // Start passkey authentication
  async startAuthentication(email?: string) {
    let allowCredentials;

    if (email) {
      const user = await db.user.findUnique({ where: { email } });
      if (user) {
        const passkeys = await db.passkey.findMany({
          where: { userId: user.id },
        });
        allowCredentials = passkeys.map((p) => ({
          id: p.credentialId,
          type: "public-key",
        }));
      }
    }

    const options = await generateAuthenticationOptions({
      rpID,
      allowCredentials,
      userVerification: "preferred",
    });

    await storeChallenge("auth", options.challenge);

    return options;
  }

  // Complete passkey authentication
  async finishAuthentication(response: any) {
    const expectedChallenge = await getChallenge("auth");

    // Find passkey by credential ID
    const passkey = await db.passkey.findUnique({
      where: { credentialId: Buffer.from(response.id, "base64url") },
      include: { user: true },
    });

    if (!passkey) {
      throw new Error("Passkey not found");
    }

    const verification = await verifyAuthenticationResponse({
      response,
      expectedChallenge,
      expectedOrigin: origin,
      expectedRPID: rpID,
      authenticator: {
        credentialID: passkey.credentialId,
        credentialPublicKey: passkey.publicKey,
        counter: passkey.counter,
      },
    });

    if (!verification.verified) {
      throw new Error("Verification failed");
    }

    // Update counter
    await db.passkey.update({
      where: { id: passkey.id },
      data: { counter: verification.authenticationInfo.newCounter },
    });

    return passkey.user;
  }
}
```

## Session Management

### Secure Session Configuration

```typescript
// Session store with Redis
import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";

const redis = Redis.fromEnv();

interface Session {
  userId: string;
  organizationId: string;
  role: string;
  createdAt: number;
  lastActivityAt: number;
  userAgent: string;
  ipAddress: string;
  mfaVerified: boolean;
}

class SessionManager {
  private sessionPrefix = "session:";
  private userSessionsPrefix = "user_sessions:";
  private maxSessionAge = 7 * 24 * 60 * 60; // 7 days
  private inactivityTimeout = 30 * 60; // 30 minutes

  async createSession(
    userId: string,
    metadata: Partial<Session>
  ): Promise<string> {
    const sessionId = nanoid(32);
    const now = Date.now();

    const session: Session = {
      userId,
      organizationId: metadata.organizationId || "",
      role: metadata.role || "user",
      createdAt: now,
      lastActivityAt: now,
      userAgent: metadata.userAgent || "",
      ipAddress: metadata.ipAddress || "",
      mfaVerified: metadata.mfaVerified || false,
    };

    // Store session
    await redis.setex(
      `${this.sessionPrefix}${sessionId}`,
      this.maxSessionAge,
      JSON.stringify(session)
    );

    // Track session for user (for "logout all")
    await redis.sadd(`${this.userSessionsPrefix}${userId}`, sessionId);

    return sessionId;
  }

  async getSession(sessionId: string): Promise<Session | null> {
    const data = await redis.get(`${this.sessionPrefix}${sessionId}`);

    if (!data) return null;

    const session = JSON.parse(data as string) as Session;

    // Check inactivity timeout
    const inactiveFor = (Date.now() - session.lastActivityAt) / 1000;
    if (inactiveFor > this.inactivityTimeout) {
      await this.destroySession(sessionId);
      return null;
    }

    return session;
  }

  async touchSession(sessionId: string): Promise<void> {
    const session = await this.getSession(sessionId);
    if (!session) return;

    session.lastActivityAt = Date.now();

    await redis.setex(
      `${this.sessionPrefix}${sessionId}`,
      this.maxSessionAge,
      JSON.stringify(session)
    );
  }

  async destroySession(sessionId: string): Promise<void> {
    const session = await this.getSession(sessionId);
    if (session) {
      await redis.srem(`${this.userSessionsPrefix}${session.userId}`, sessionId);
    }
    await redis.del(`${this.sessionPrefix}${sessionId}`);
  }

  async destroyAllUserSessions(userId: string): Promise<void> {
    const sessionIds = await redis.smembers(
      `${this.userSessionsPrefix}${userId}`
    );

    for (const sessionId of sessionIds) {
      await redis.del(`${this.sessionPrefix}${sessionId}`);
    }

    await redis.del(`${this.userSessionsPrefix}${userId}`);
  }

  async listUserSessions(userId: string): Promise<Session[]> {
    const sessionIds = await redis.smembers(
      `${this.userSessionsPrefix}${userId}`
    );

    const sessions: Session[] = [];
    for (const sessionId of sessionIds) {
      const session = await this.getSession(sessionId as string);
      if (session) {
        sessions.push(session);
      }
    }

    return sessions;
  }
}
```

## Tools & Integrations

### Authentication Providers

- **Clerk** - Full-featured, great DX
- **Auth0** - Enterprise-grade
- **WorkOS** - Enterprise SSO focus
- **Supabase Auth** - Integrated with Supabase
- **NextAuth.js** - Open source, flexible

### Identity Providers

- **Okta** - Enterprise identity
- **Azure AD** - Microsoft ecosystem
- **Google Workspace** - Google ecosystem
- **OneLogin** - Enterprise SSO

### Security Tools

- **1Password** - Secret management
- **Vault** - HashiCorp secrets
- **Infisical** - Open source secrets

## Best Practices

### Password Security

- Minimum 12 characters
- Use Argon2id for hashing
- Check against breach databases
- No password hints
- Secure reset flow with expiring tokens

### Token Security

- Short-lived access tokens (15 min)
- Secure refresh token rotation
- Token binding to user agent/IP
- Revocation capability
- Don't store in localStorage

### Session Security

- HttpOnly, Secure, SameSite cookies
- Session fixation prevention
- Activity-based timeout
- Concurrent session limits
- Device tracking

## Pitfalls to Avoid

- Storing passwords in plain text
- Long-lived tokens without rotation
- Tokens in URL parameters
- No rate limiting on auth endpoints
- Username enumeration
- Weak password reset flows
- Not validating redirect URIs
- Trusting client-provided user info

## Output Format

- Authentication flow diagrams
- Integration code snippets
- Configuration documentation
- Security review checklists
- Migration guides


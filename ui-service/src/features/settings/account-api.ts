import { HttpClient } from "../../shared/api/http";
import { Json, type JsonObject } from "../../shared/api/json";
import { Theme, type ThemeChoice } from "../../shared/ui/theme";

const ACCOUNT_ENDPOINT = "/api/user/account";
const PROVIDER_KEYS_ENDPOINT = "/api/user/account/provider-keys";

type Account = {
  readonly username: string;
  readonly email: string;
  readonly theme: ThemeChoice;
};

export type ProviderKey = {
  readonly provider: string;
  readonly hint: string;
  readonly monthlyLimitCents: number | null;
  readonly spentCents: number;
};

type ProviderKeyInput = {
  readonly provider: string;
  readonly key: string;
  readonly password: string;
  readonly monthlyLimitCents: number | null;
};

export class AccountApi {
  static async read(): Promise<Account> {
    const payload = await HttpClient.json({ endpoint: ACCOUNT_ENDPOINT });
    const account = Json.object(payload, "account");

    return {
      username: Json.string(account.username, "account.username"),
      email: Json.string(account.email, "account.email"),
      theme: Theme.asChoice(account.theme),
    };
  }

  static async chooseTheme(theme: ThemeChoice): Promise<ThemeChoice> {
    const payload = await HttpClient.json({
      endpoint: `${ACCOUNT_ENDPOINT}/theme`,
      method: "PATCH",
      body: { theme },
    });

    return Theme.asChoice(Json.object(payload, "theme").theme);
  }

  static async changeUsername(username: string): Promise<void> {
    await HttpClient.json({
      endpoint: `${ACCOUNT_ENDPOINT}/username`,
      method: "PATCH",
      body: { username },
    });
  }

  static async changePassword(
    currentPassword: string,
    newPassword: string,
  ): Promise<void> {
    await HttpClient.json({
      endpoint: `${ACCOUNT_ENDPOINT}/password`,
      method: "PATCH",
      body: { current_password: currentPassword, new_password: newPassword },
    });
  }

  static async deleteAccount(password: string): Promise<void> {
    await HttpClient.json({
      endpoint: ACCOUNT_ENDPOINT,
      method: "DELETE",
      body: { password },
    });
  }

  static async providerKeys(): Promise<readonly ProviderKey[]> {
    const payload = await HttpClient.json({
      endpoint: PROVIDER_KEYS_ENDPOINT,
    });
    const root = Json.object(payload, "providerKeys");
    const entries = Json.array(root.provider_keys, "providerKeys.list");

    return entries.map((entry, index) =>
      AccountApi.toProviderKey(
        Json.object(entry, `providerKeys.list[${index}]`),
      ),
    );
  }

  static async saveProviderKey(input: ProviderKeyInput): Promise<void> {
    await HttpClient.json({
      endpoint: PROVIDER_KEYS_ENDPOINT,
      method: "PUT",
      body: {
        provider: input.provider,
        key: input.key,
        password: input.password,
        monthly_limit_cents: input.monthlyLimitCents,
      },
    });
  }

  static async removeProviderKey(provider: string): Promise<void> {
    await HttpClient.send({
      endpoint: `${PROVIDER_KEYS_ENDPOINT}/${provider}`,
      method: "DELETE",
    });
  }

  private static toProviderKey(raw: JsonObject): ProviderKey {
    return {
      provider: Json.string(raw.provider, "providerKey.provider"),
      hint: Json.stringOr(raw.hint, ""),
      monthlyLimitCents: Json.optionalNumber(raw.monthly_limit_cents),
      spentCents: Json.numberOr(raw.spent_cents, 0),
    };
  }
}

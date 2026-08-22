const CENTS_IN_A_DOLLAR = 100;
const DECIMAL_PLACES = 2;

export class Money {
  static toDollarText(cents: number | null): string {
    if (cents === null) return "";

    return (cents / CENTS_IN_A_DOLLAR).toFixed(DECIMAL_PLACES);
  }

  static toAmount(cents: number): string {
    return `$${(cents / CENTS_IN_A_DOLLAR).toFixed(DECIMAL_PLACES)}`;
  }

  static toOptionalCents(dollarText: string): number | null {
    const trimmed = dollarText.trim();

    if (trimmed.length === 0) return null;

    const dollars = Number(trimmed);

    if (Number.isNaN(dollars) || dollars < 0) return null;

    return Math.round(dollars * CENTS_IN_A_DOLLAR);
  }
}

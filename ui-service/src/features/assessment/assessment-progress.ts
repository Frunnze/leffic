const FIRST_PAGE = 1;
const OPTION_LETTERS = "ABCDEFGH";

export class AssessmentProgress {
  static storedPage(scopeId: string): number {
    return AssessmentProgress.readNumber(`testPage${scopeId}`, FIRST_PAGE);
  }

  static storedIndex(scopeId: string): number {
    return AssessmentProgress.readNumber(`testLastIndex${scopeId}`, 0);
  }

  static remember(scopeId: string, page: number, index: number): void {
    localStorage.setItem(`testPage${scopeId}`, String(page));
    localStorage.setItem(`testLastIndex${scopeId}`, String(index));
  }

  static forget(scopeId: string): void {
    localStorage.removeItem(`testPage${scopeId}`);
    localStorage.removeItem(`testLastIndex${scopeId}`);
  }

  static overallPosition(page: number, perPage: number, index: number): number {
    return (page - FIRST_PAGE) * perPage + index + 1;
  }

  static optionLetter(index: number): string {
    return OPTION_LETTERS[index] ?? String(index + 1);
  }

  private static readNumber(key: string, fallback: number): number {
    const stored = localStorage.getItem(key);
    if (stored === null) return fallback;

    const parsed = Number(stored);

    return Number.isFinite(parsed) ? parsed : fallback;
  }
}

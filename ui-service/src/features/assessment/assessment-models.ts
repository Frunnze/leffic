export type AssessmentOption = {
  readonly id: string;
  readonly option: string;
};

export type AssessmentItem = {
  readonly id: string;
  readonly question: string;
  readonly options: readonly AssessmentOption[];
  readonly lastAnswers: readonly string[];
};

export type AssessmentPage = {
  readonly testSession: string;
  readonly items: readonly AssessmentItem[];
  readonly page: number;
  readonly perPage: number;
  readonly totalItems: number;
};

export type AssessmentSessionResult = {
  readonly correct: number;
};

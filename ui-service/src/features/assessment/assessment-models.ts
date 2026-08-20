export type AssessmentOption = {
  readonly id: number;
  readonly option: string;
};

export type AssessmentAnswer = number | string;

export type AssessmentItem = {
  readonly id: string;
  readonly type: string;
  readonly question: string;
  readonly options: readonly AssessmentOption[];
  readonly lastAnswers: readonly AssessmentAnswer[];
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

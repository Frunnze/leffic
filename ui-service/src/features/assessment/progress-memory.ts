export type ProgressMemory = {
  storedPage(scopeId: string): number;
  storedIndex(scopeId: string): number;
  remember(scopeId: string, page: number, index: number): void;
  forget(scopeId: string): void;
};

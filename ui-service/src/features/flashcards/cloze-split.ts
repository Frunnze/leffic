type ClozePiece = {
  readonly text: string;
  readonly isHidden: boolean;
};

export class ClozeSplit {
  static pieces(
    text: string,
    hiddenParts: readonly string[],
  ): readonly ClozePiece[] {
    let pieces: readonly ClozePiece[] = [{ text, isHidden: false }];

    for (const hidden of hiddenParts) {
      pieces = ClozeSplit.hideEverywhere(pieces, hidden);
    }

    return pieces.filter((piece) => piece.text.length > 0);
  }

  private static hideEverywhere(
    pieces: readonly ClozePiece[],
    hidden: string,
  ): readonly ClozePiece[] {
    const split: ClozePiece[] = [];

    for (const piece of pieces) {
      if (piece.isHidden) {
        split.push(piece);
        continue;
      }

      split.push(...ClozeSplit.hideInside(piece.text, hidden));
    }

    return split;
  }

  private static hideInside(text: string, hidden: string): ClozePiece[] {
    const parts = text.split(hidden);
    const pieces: ClozePiece[] = [];

    parts.forEach((part, index) => {
      pieces.push({ text: part, isHidden: false });

      if (index < parts.length - 1) {
        pieces.push({ text: hidden, isHidden: true });
      }
    });

    return pieces;
  }
}

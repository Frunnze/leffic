const SECONDS_PER_MINUTE = 60;
const SECONDS_PER_HOUR = 3600;
const SECONDS_PER_DAY = 86400;
const SECONDS_PER_MONTH = 2592000;
const SECONDS_PER_YEAR = 31536000;

export class IntervalLabel {
  static fromSeconds(seconds: number): string {
    if (seconds < SECONDS_PER_MINUTE) return `${Math.round(seconds)} s`;

    if (seconds < SECONDS_PER_HOUR) {
      return `${Math.floor(seconds / SECONDS_PER_MINUTE)} min`;
    }

    if (seconds < SECONDS_PER_DAY) {
      return `${Math.floor(seconds / SECONDS_PER_HOUR)} h`;
    }

    if (seconds < SECONDS_PER_MONTH) {
      return `${Math.floor(seconds / SECONDS_PER_DAY)} days`;
    }

    if (seconds < SECONDS_PER_YEAR) {
      return `${Math.floor(seconds / SECONDS_PER_MONTH)} mo`;
    }

    return `${Math.floor(seconds / SECONDS_PER_YEAR)} y`;
  }
}

import random

_SEED = 731125
_GENERATOR = random.Random(_SEED)
_ALPHABET = "0123456789abcdef-{}[]'\";\\ \t\n%$&"
_NOISE_COUNT = 8
_NOISE_LENGTH = 24

HOSTILE_IDENTIFIERS: tuple[str, ...] = (
    " ",
    "\t\n",
    "not-a-uuid",
    "6f1c7d4e-0000-4000-8000",
    "6f1c7d4e-0000-4000-8000-0000000000a",
    "6f1c7d4e-0000-4000-8000-0000000000aaaa",
    "' OR 1=1 --",
    "1; DROP TABLE folders",
    "home",
    "None",
    "null",
    "undefined",
    "../../etc/passwd",
    "%00",
    "<script>alert(1)</script>",
    "ünïcødé",
    "日本語のテキスト",
    "🙈🙉🙊",
    "\N{ZERO WIDTH SPACE}",
    "-1",
    "0",
    "NaN",
    "Infinity",
    "{}",
    "[]",
    "x" * 4096,
    *tuple(
        "".join(_GENERATOR.choices(_ALPHABET, k=_NOISE_LENGTH))
        for _ in range(_NOISE_COUNT)
    ),
)

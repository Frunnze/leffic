from check_support import REPOSITORY
from reproducible_images_support import GATEWAY_PACKAGE

GATEWAY_BASE_IMAGES = (
    "FROM node:20-alpine AS builder",
    "FROM nginxinc/nginx-unprivileged:alpine",
)
GATEWAY_NJS_COPY = (
    "COPY --from=builder /build/dist/jwt.js /etc/nginx/njs/jwt.js"
)
GATEWAY_CONTEXT_PATHS = (
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "src",
    "nginx.conf",
)


def real_dockerfile(package: str) -> str:
    dockerfile = REPOSITORY / package / "Dockerfile"

    return dockerfile.read_text(encoding="utf-8")


def gateway_dockerfile_lines() -> list[str]:
    text = real_dockerfile(GATEWAY_PACKAGE)

    return [line.strip() for line in text.splitlines() if line.strip()]

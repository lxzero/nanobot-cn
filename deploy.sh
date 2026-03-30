#!/usr/bin/env bash
set -euo pipefail

DOCKER_USER="barrylv"
IMAGE_NAME="nanobot-cn"
FULL_IMAGE="${DOCKER_USER}/${IMAGE_NAME}"
PLATFORMS="linux/amd64,linux/arm64"

COMMIT_SHA=$(git rev-parse --short HEAD)
TAG="${1:-}"

TAGS=("latest" "${COMMIT_SHA}")
[[ -n "${TAG}" && "${TAG}" != "latest" ]] && TAGS+=("${TAG}")

TAG_ARGS=()
for t in "${TAGS[@]}"; do
    TAG_ARGS+=(-t "${FULL_IMAGE}:${t}")
done

echo "==> 构建多平台镜像 ${FULL_IMAGE} (tags: ${TAGS[*]})"
echo "    平台: ${PLATFORMS}"
docker buildx build --platform "${PLATFORMS}" "${TAG_ARGS[@]}" --push .

echo "==> 完成！"
for t in "${TAGS[@]}"; do
    echo "    docker pull ${FULL_IMAGE}:${t}"
done

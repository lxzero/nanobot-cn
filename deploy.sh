#!/usr/bin/env bash
set -euo pipefail

DOCKER_USER="barrylv"
IMAGE_NAME="nanobot-cn"
FULL_IMAGE="${DOCKER_USER}/${IMAGE_NAME}"

COMMIT_SHA=$(git rev-parse --short HEAD)
TAG="${1:-}"

TAGS=("latest" "${COMMIT_SHA}")
[[ -n "${TAG}" && "${TAG}" != "latest" ]] && TAGS+=("${TAG}")

BUILD_ARGS=()
for t in "${TAGS[@]}"; do
    BUILD_ARGS+=(-t "${FULL_IMAGE}:${t}")
done

echo "==> 构建镜像 ${FULL_IMAGE} (tags: ${TAGS[*]})"
docker build "${BUILD_ARGS[@]}" .

for t in "${TAGS[@]}"; do
    echo "==> 推送 ${FULL_IMAGE}:${t}"
    docker push "${FULL_IMAGE}:${t}"
done

echo "==> 完成！"
for t in "${TAGS[@]}"; do
    echo "    docker pull ${FULL_IMAGE}:${t}"
done

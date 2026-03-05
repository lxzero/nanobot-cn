#!/usr/bin/env bash
set -euo pipefail

DOCKER_USER="barrylv"
IMAGE_NAME="nanobot-cn"
FULL_IMAGE="${DOCKER_USER}/${IMAGE_NAME}"

COMMIT_SHA=$(git rev-parse --short HEAD)
TAG="${1:-latest}"

echo "==> 构建镜像 ${FULL_IMAGE}:${TAG} (commit: ${COMMIT_SHA})"
docker build -t "${FULL_IMAGE}:${TAG}" -t "${FULL_IMAGE}:${COMMIT_SHA}" .

echo "==> 推送 ${FULL_IMAGE}:${TAG}"
docker push "${FULL_IMAGE}:${TAG}"

echo "==> 推送 ${FULL_IMAGE}:${COMMIT_SHA}"
docker push "${FULL_IMAGE}:${COMMIT_SHA}"

echo "==> 完成！"
echo "    docker pull ${FULL_IMAGE}:${TAG}"
echo "    docker pull ${FULL_IMAGE}:${COMMIT_SHA}"

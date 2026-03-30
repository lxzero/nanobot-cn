#!/usr/bin/env bash
set -euo pipefail

APP_NAME="nanobot"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="${APP_DIR}/.venv"
NANOBOT="${VENV_DIR}/bin/nanobot"
PID_FILE="${APP_DIR}/nanobot.pid"
LOG_FILE="${APP_DIR}/nanobot.log"

Red='\033[0;31m'
Green='\033[0;32m'
Yellow='\033[0;33m'
NC='\033[0m'

log()  { echo -e "${Green}[${APP_NAME}]${NC} $*"; }
warn() { echo -e "${Yellow}[${APP_NAME}]${NC} $*"; }
err()  { echo -e "${Red}[${APP_NAME}]${NC} $*" >&2; }

get_pid() {
    if [[ -f "${PID_FILE}" ]]; then
        local pid
        pid=$(cat "${PID_FILE}")
        if kill -0 "${pid}" 2>/dev/null; then
            echo "${pid}"
            return 0
        fi
        rm -f "${PID_FILE}"
    fi
    return 1
}

do_start() {
    if pid=$(get_pid); then
        warn "已在运行 (PID: ${pid})"
        return 0
    fi

    if [[ ! -x "${NANOBOT}" ]]; then
        err "找不到 ${NANOBOT}，请先执行: uv pip install ."
        exit 1
    fi

    log "启动 gateway ..."
    nohup "${NANOBOT}" gateway >> "${LOG_FILE}" 2>&1 &
    echo $! > "${PID_FILE}"
    log "已启动 (PID: $!, 日志: ${LOG_FILE})"
}

do_stop() {
    if ! pid=$(get_pid); then
        warn "未在运行"
        return 0
    fi

    log "停止中 (PID: ${pid}) ..."
    kill "${pid}"

    local waited=0
    while kill -0 "${pid}" 2>/dev/null; do
        sleep 1
        waited=$((waited + 1))
        if [[ ${waited} -ge 15 ]]; then
            warn "优雅停止超时，强制终止 ..."
            kill -9 "${pid}" 2>/dev/null || true
            break
        fi
    done

    rm -f "${PID_FILE}"
    log "已停止"
}

do_restart() {
    do_stop
    do_start
}

do_status() {
    if pid=$(get_pid); then
        log "运行中 (PID: ${pid})"
    else
        warn "未在运行"
    fi
}

do_update() {
    log "拉取最新代码 ..."
    git -C "${APP_DIR}" pull

    log "安装依赖 ..."
    "${VENV_DIR}/bin/uv" pip install "${APP_DIR}"

    log "更新完成，正在重启 ..."
    do_restart
}

do_log() {
    local lines="${2:-50}"
    tail -n "${lines}" -f "${LOG_FILE}"
}

usage() {
    cat <<EOF
用法: $0 {start|stop|restart|status|update|log}

  start    启动 nanobot gateway
  stop     停止 nanobot gateway
  restart  重启 nanobot gateway
  status   查看运行状态
  update   拉取代码 + 安装依赖 + 重启
  log      查看实时日志 (默认最近 50 行)
EOF
}

case "${1:-}" in
    start)   do_start   ;;
    stop)    do_stop    ;;
    restart) do_restart ;;
    status)  do_status  ;;
    update)  do_update  ;;
    log)     do_log "$@" ;;
    *)       usage; exit 1 ;;
esac

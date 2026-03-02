FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates git && \
    rm -rf /var/lib/apt/lists/*

# GitHub CLI (binary install)
RUN ARCH=$(dpkg --print-architecture) && \
    GH_VER=$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest | grep '"tag_name"' | sed 's/.*"v\(.*\)".*/\1/') && \
    curl -fsSL "https://github.com/cli/cli/releases/download/v${GH_VER}/gh_${GH_VER}_linux_${ARCH}.tar.gz" \
      | tar xz --strip-components=1 -C /usr/local && \
    gh --version

# Node.js (binary install for npx/clawhub)
RUN ARCH=$(uname -m | sed 's/aarch64/arm64/;s/x86_64/x64/') && \
    NODE_VER=$(curl -fsSL https://nodejs.org/dist/index.json | python3 -c "import sys,json;print([r['version'] for r in json.load(sys.stdin) if r['lts']][0])") && \
    curl -fsSL "https://nodejs.org/dist/${NODE_VER}/node-${NODE_VER}-linux-${ARCH}.tar.gz" \
      | tar xz --strip-components=1 -C /usr/local && \
    node --version && npm --version

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY pyproject.toml README.md LICENSE ./
RUN mkdir -p nanobot && touch nanobot/__init__.py && \
    uv pip install --system --no-cache . && \
    rm -rf nanobot

# Copy source and reinstall
COPY nanobot/ nanobot/
RUN uv pip install --system --no-cache .

# Install skill-specific dependencies
RUN for req in nanobot/skills/*/scripts/requirements.txt; do \
        [ -f "$req" ] && uv pip install --system --no-cache -r "$req"; \
    done; true

# Create config directory
RUN mkdir -p /root/.nanobot

# Gateway default port
EXPOSE 18790

ENTRYPOINT ["nanobot"]
CMD ["gateway"]

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Switch to HTTPS to avoid CDN 502/500 errors, then add retry policy
RUN sed -i 's|URIs: http://|URIs: https://|g' /etc/apt/sources.list.d/debian.sources && \
    echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80retries && \
    apt-get update && \
    apt-get install -y --no-install-recommends git openssh-client && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Increase HTTP timeout; use Tsinghua PyPI mirror to avoid CDN instability during multi-platform builds
ENV UV_HTTP_TIMEOUT=120
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/

# Install Python dependencies first (cached layer)
COPY pyproject.toml README.md LICENSE ./
RUN mkdir -p nanobot && touch nanobot/__init__.py && \
    uv pip install --system --no-cache . && \
    rm -rf nanobot

# Copy the full source and install
COPY nanobot/ nanobot/
RUN uv pip install --system --no-cache .

# Create config directory
RUN mkdir -p /root/.nanobot

# Gateway default port
EXPOSE 18790

ENTRYPOINT ["nanobot"]
CMD ["status"]

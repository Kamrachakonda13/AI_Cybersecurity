# VEYRA v5.0 managed-worker verifier.
#
# Security-hardened image:
#   - Based on python:3.13-slim-bookworm (matches the local dev runtime)
#   - Runs as non-root user (UID 10001, no login shell)
#   - Uses only Python stdlib — no pip installs at build time
#   - Read-only filesystem at runtime (configured in compose)
#   - Stateless: reads JSON on stdin, writes JSON on stdout, no disk writes
#
# Build:
#   docker build -t veyra-worker-v50:5.0 ./worker/v50
#
# Run (interactive):
#   echo '{...}' | docker run --rm -i --read-only --tmpfs /tmp veyra-worker-v50:5.0
#
# See SECURITY.md for the full deployment profile.

FROM python:3.13-slim-bookworm

# Non-root user (no shell, no home dir)
RUN groupadd --system --gid 10001 worker \
    && useradd --system --uid 10001 --gid worker --no-create-home --shell /usr/sbin/nologin worker

# Work dir owned by root, read-only to worker
WORKDIR /app

# Copy only what the worker needs
COPY veyra_trust_verifier.py /app/veyra_trust_verifier.py
COPY CONTRACT.md /app/CONTRACT.md
COPY schema/ /app/schema/

# Ensure the worker cannot write to /app
RUN chmod 0555 /app \
    && chmod 0444 /app/veyra_trust_verifier.py /app/CONTRACT.md \
    && chmod 0444 /app/schema/*.json

# Drop privileges
USER worker

# No network listeners; only stdin/stdout
EXPOSE 0

# Unbuffered stdout so callers can stream JSON
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# Healthcheck: the worker exits 0 on "healthy", 2 on any other outcome.
# A container that keeps exiting 2 is not a fault — it means verification failed.
# We do a lightweight self-check: the module should at least be importable.
HEALTHCHECK --interval=60s --timeout=5s --start-period=5s --retries=1 \
    CMD python -c "import veyra_trust_verifier; assert hasattr(veyra_trust_verifier, 'verify')" || exit 1

# Run the verifier; input comes via stdin
ENTRYPOINT ["python", "-u", "/app/veyra_trust_verifier.py"]
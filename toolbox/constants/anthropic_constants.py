ANTHROPIC_MODEL_DEFAULT = "claude-2.0"
ANTHROPIC_MAX_THREADS = 15
ANTHROPIC_MAX_RPM = ANTHROPIC_MAX_THREADS * 12  # 900 max RPM / 75 connections = 12 RPM per connection
ANTHROPIC_MAX_RE_ATTEMPTS = 3
ANTHROPIC_MAX_MODEL_TOKENS = 100_000

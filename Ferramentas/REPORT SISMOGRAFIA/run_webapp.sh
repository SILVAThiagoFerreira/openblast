#!/usr/bin/env bash
# Sobe o webapp do REPORT SISMOGRAFIA em http://127.0.0.1:5057
cd "$(dirname "$0")"
exec python -m webapp.server "$@"

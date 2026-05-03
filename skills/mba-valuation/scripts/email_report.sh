#!/bin/bash
# Wrapper to send valuation PDF via Gmail SMTP
exec python3 "$(dirname "$0")/send_gmail.py" "$@"

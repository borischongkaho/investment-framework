#!/usr/bin/env python3
"""Send valuation PDF via Gmail API (OAuth2).

Setup (one-time):
1. Create OAuth credentials at https://console.cloud.google.com/apis/credentials
   - Type: OAuth Client ID → Desktop App
2. Download JSON, save as: ~/.claude/skills/mba-valuation/scripts/credentials.json
3. First run will open browser for consent → token saved to token.json

Usage:
  send_gmail.py <pdf> <ticker> <date> <intrinsic> <mos> <recommendation>
"""
import base64
import os
import sys
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCRIPT_DIR = Path(__file__).parent
CREDENTIALS_FILE = SCRIPT_DIR / "credentials.json"
TOKEN_FILE = SCRIPT_DIR / "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TO_EMAIL = "borischong.ai@gmail.com"


def get_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print(f"❌ Missing credentials file: {CREDENTIALS_FILE}", file=sys.stderr)
                print("Setup steps:", file=sys.stderr)
                print("  1. Go to https://console.cloud.google.com/apis/credentials", file=sys.stderr)
                print("  2. Create OAuth Client ID → Desktop App", file=sys.stderr)
                print("  3. Download JSON, save as credentials.json in the scripts folder", file=sys.stderr)
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
        os.chmod(TOKEN_FILE, 0o600)
    return build("gmail", "v1", credentials=creds)


def send(pdf_path, ticker, date, intrinsic, mos, rec):
    msg = EmailMessage()
    msg["Subject"] = f"📊 估值報告 — {ticker} | {date} | MoS {mos} | {rec}"
    msg["To"] = TO_EMAIL
    msg.set_content(f"""Boris，

附上 {ticker} 完整 8-phase valuation report。

📊 Quick Summary
- Date: {date}
- Intrinsic Value: ${intrinsic} / share
- Margin of Safety: {mos}
- Recommendation: {rec}

完整報告 + Business Overview + Moat + Risks + Thesis 全部喺 PDF 附件。

— Claude (Investment Valuation Analyst)
""")

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf",
                           filename=Path(pdf_path).name)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service = get_service()
    try:
        result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        print(f"✅ Email sent: {ticker} → {TO_EMAIL} (id: {result['id']})")
    except HttpError as e:
        print(f"❌ Gmail API error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 7:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    pdf_path = sys.argv[1]
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    send(*sys.argv[1:7])

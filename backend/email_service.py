"""Resend email sender — async wrapper + simple HTML templates."""
import os
import asyncio
import base64
import logging
from typing import Optional

import resend

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
SENDER_NAME = os.environ.get("SENDER_NAME", "Anchor")

resend.api_key = RESEND_API_KEY


def _from() -> str:
    return f"{SENDER_NAME} <{SENDER_EMAIL}>"


def email_configured() -> bool:
    return bool(RESEND_API_KEY)


async def send_email(
    *,
    to: str,
    subject: str,
    html: str,
    reply_to: Optional[str] = None,
    attachment_bytes: Optional[bytes] = None,
    attachment_filename: Optional[str] = None,
) -> dict:
    if not RESEND_API_KEY:
        raise RuntimeError("Resend API key is not configured")
    params = {
        "from": _from(),
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if reply_to:
        params["reply_to"] = reply_to
    if attachment_bytes and attachment_filename:
        params["attachments"] = [
            {
                "filename": attachment_filename,
                "content": base64.b64encode(attachment_bytes).decode("ascii"),
            }
        ]
    result = await asyncio.to_thread(resend.Emails.send, params)
    return result


SAGE = "#4A6552"
TERRACOTTA = "#C86B52"
INK = "#2A2E2B"
MUTED = "#5C6160"
BONE = "#F2EFE8"
BG = "#FAF7EF"


def _wrap(title: str, intro_html: str, body_html: str, footer_note: str = "") -> str:
    return f"""<!doctype html>
<html><body style="margin:0;padding:0;background:{BG};font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;color:{INK};">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{BG};padding:32px 0;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" border="0" style="background:#ffffff;border:1px solid {BONE};border-radius:16px;overflow:hidden;">
<tr><td style="padding:32px 36px 8px 36px;">
<div style="font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:{MUTED};font-weight:600;">Anchor</div>
<h1 style="margin:8px 0 16px 0;font-size:26px;font-weight:600;letter-spacing:-0.02em;color:{INK};">{title}</h1>
{intro_html}
</td></tr>
<tr><td style="padding:8px 36px 32px 36px;font-size:15px;line-height:1.65;color:{INK};">
{body_html}
</td></tr>
<tr><td style="padding:0 36px 28px 36px;font-size:12px;line-height:1.6;color:{MUTED};border-top:1px solid {BONE};padding-top:18px;">
{footer_note}<br/>Sent from Anchor — your private recovery companion. Reply directly to this email if you want to get in touch with the sender.
</td></tr>
</table></td></tr></table></body></html>"""


def doctor_report_html(sender_name: str, period_label: str, personal_note: str = "") -> str:
    intro = f'<p style="margin:0;color:{MUTED};font-size:14px;">{sender_name} has shared a recovery health summary with you.</p>'
    body = f"""
<p>Hi,</p>
<p>{sender_name} is using Anchor to monitor their recovery, diet, blood markers, medications, and weekly goals.
The attached PDF is a <strong>{period_label.lower()}</strong> snapshot. It's self-reported data — useful as context, not a substitute for clinical assessment.</p>
{('<p style="background:' + BONE + ';border-radius:12px;padding:14px 16px;font-style:italic;color:' + INK + ';">"' + personal_note + '"</p>') if personal_note else ''}
<p style="margin-top:24px;">Thank you for being part of their recovery,<br/>— The Anchor app</p>"""
    return _wrap(
        title=f"{sender_name}'s recovery report",
        intro_html=intro,
        body_html=body,
        footer_note=f"Period covered: {period_label}.",
    )


def weekly_digest_html(name: str, days_sober: int, insight_text: str, week_label: str) -> str:
    intro = f'<p style="margin:0;color:{MUTED};font-size:14px;">{week_label}</p>'
    # convert plain newlines to paragraph breaks
    paragraphs = [p.strip() for p in (insight_text or "").split("\n\n") if p.strip()]
    body_p = "".join(f'<p style="margin:0 0 16px 0;">{p}</p>' for p in paragraphs) or '<p style="color:#777;">No reflection text — try generating this week\'s insight in the app first.</p>'
    streak_box = f"""
<table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:{BONE};border-radius:12px;padding:16px 20px;">
<div style="font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:{MUTED};font-weight:600;">Days sober</div>
<div style="font-size:36px;font-weight:600;color:{SAGE};letter-spacing:-0.02em;line-height:1.1;margin-top:4px;">{days_sober}</div>
</td></tr></table>"""
    body = streak_box + body_p
    return _wrap(
        title=f"This week — {name}",
        intro_html=intro,
        body_html=body,
        footer_note="A private reflection from your week. Open Anchor to see more.",
    )

# scheduler/notify.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()

def send_summary(total, unique, high_match, threshold, top_jobs):
    sender   = os.getenv("EMAIL_FROM")
    receiver = os.getenv("EMAIL_TO")
    password = os.getenv("EMAIL_APP_PASSWORD")

    if not all([sender, receiver, password]):
        logger.warning("Email credentials not set — skipping notification")
        return

    # Build top jobs table
    rows = ""
    for j in top_jobs:
        rows += f"""
        <tr>
        <td style="padding:12px;border-bottom:1px solid #1f2430;">
            <div style="font-weight:700;font-size:14px;margin-bottom:3px;">{j['title']}</div>
            <div style="color:#5a6175;font-size:12px;font-family:monospace;">{j['company']}</div>
        </td>
        <td style="padding:12px;border-bottom:1px solid #1f2430;
                    color:#00e5a0;font-weight:800;font-size:16px;
                    white-space:nowrap;">
            {j['match_score']}%
        </td>
        <td style="padding:12px;border-bottom:1px solid #1f2430;">
            <span style="background:rgba(123,97,255,0.15);color:#7b61ff;
                        padding:2px 8px;border-radius:4px;font-size:11px;
                        font-family:monospace;">{j['source']}</span>
        </td>
        <td style="padding:12px;border-bottom:1px solid #1f2430;">
            <a href="{j['url']}" target="_blank"
            style="display:inline-block;background:#00e5a0;color:#000;
                    font-weight:700;font-size:12px;padding:8px 16px;
                    border-radius:6px;text-decoration:none;
                    font-family:sans-serif;white-space:nowrap;">
            View & Apply →
            </a>
        </td>
        </tr>
        """

    html = f"""
    <html>
    <body style="background:#0a0b0f;color:#e8eaf0;font-family:sans-serif;padding:32px;">
      <div style="max-width:600px;margin:0 auto;">

        <h1 style="font-size:22px;font-weight:800;margin-bottom:4px;">
          C<span style="color:#00e5a0;">O</span>IE — Daily Pipeline Report
        </h1>
        <p style="color:#5a6175;font-size:13px;margin-bottom:28px;font-family:monospace;">
          Automated run completed successfully
        </p>

        <!-- Stats -->
        <div style="display:flex;gap:16px;margin-bottom:28px;">
          {_stat_box("Jobs Scraped", total, "#7b61ff")}
          {_stat_box("Unique", unique, "#00b8ff")}
          {_stat_box(f"Above {threshold}%", high_match, "#00e5a0")}
        </div>

        <!-- Top jobs table -->
        <h2 style="font-size:13px;letter-spacing:1.2px;text-transform:uppercase;
                   color:#5a6175;margin-bottom:12px;">
          Top Matches
        </h2>
        <table style="width:100%;border-collapse:collapse;background:#111318;
                      border:1px solid #1f2430;border-radius:8px;overflow:hidden;">
            <thead>
            <tr style="background:#181c23;">
                <th style="padding:8px 12px;text-align:left;font-size:10px;
                        letter-spacing:1px;color:#5a6175;">ROLE & COMPANY</th>
                <th style="padding:8px 12px;text-align:left;font-size:10px;
                        letter-spacing:1px;color:#5a6175;">MATCH</th>
                <th style="padding:8px 12px;text-align:left;font-size:10px;
                        letter-spacing:1px;color:#5a6175;">SOURCE</th>
                <th style="padding:8px 12px;text-align:left;font-size:10px;
                        letter-spacing:1px;color:#5a6175;">ACTION</th>
            </tr>
            </thead>
          <tbody>{rows}</tbody>
        </table>

        <p style="margin-top:24px;font-size:12px;color:#5a6175;font-family:monospace;">
          Open your dashboard to review and take action →
          <a href="http://localhost:5173" style="color:#7b61ff;">localhost:5173</a>
        </p>

      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"COIE ✦ {high_match} high-match jobs found today"
    msg["From"]    = sender
    msg["To"]      = receiver
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        logger.info(f"Email notification sent → {receiver}")
    except Exception as e:
        logger.error(f"Email failed: {e}")


def _stat_box(label, value, color):
    return f"""
    <div style="flex:1;background:#111318;border:1px solid #1f2430;
                border-radius:8px;padding:16px 20px;border-top:2px solid {color};">
      <div style="font-size:10px;letter-spacing:1px;color:#5a6175;
                  text-transform:uppercase;font-family:monospace;">{label}</div>
      <div style="font-size:32px;font-weight:800;color:{color};
                  margin-top:6px;">{value}</div>
    </div>
    """
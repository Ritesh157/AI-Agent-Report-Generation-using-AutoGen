"""Telegram bot for sending reports - Simple working version"""

from telethon import TelegramClient # use to log in and send messages or files through Telegram account or bot.
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
import os

# Create Telegram Client
# riteshreport123_session: This is the session name — Telethon uses it to remember our login
# The first time you run this, Telethon will ask for your phone number and OTP code (sent to Telegram).
# It will then create a file in your current directory. This file stores your login credentials securely.
# Next time you run the script, it won’t ask for login again — it will reuse this session. 
client = TelegramClient('riteshreport123_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)

# It’s an asynchronous function (uses async because Telethon requires async for network calls).
# report_files → like ["sales_report.txt", "marketing_report.txt"]
# chart_files → like ["sales_by_region.png", "product_performance.png"]
# The word async means this is an asynchronous function — it can pause and wait for Telegram actions to finish (like sending a message).
async def send_telegram_reports(report_files, chart_files):
    """Send all reports and charts to Telegram"""
    print("\n" + "="*80)
    print("SENDING TO TELEGRAM")
    print("="*80)

    from datetime import datetime
    # Gets the current date and time and formats it nicely.
    # Example output: October 13, 2025 at 11:20 PM IST
    today = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")

    # Sends a text message at the top of your Telegram chat.
    # TELEGRAM_PHONE is your Telegram account (the number you registered with).
    # The message includes: Title, TimeStamp, Data Summary
    await client.send_message(TELEGRAM_PHONE,
                              f"📊 **Daily Sales & Marketing Report**\n\n"
                              f"Generated: {today}\n"
                              f"Data: 1000 Sales + 1000 Marketing Records\n"
                              "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    print("✓ Sent header message")

    # Send charts with captions
    # .title() -> Capitalize each word. For exapmple: "Sales By Region"
    # The await keyword is needed because this is an asynchronous operation — it waits until the file is actually sent before moving to the next chart.
    for chart in chart_files:
        if os.path.exists(chart):
            chart_name = os.path.basename(chart).replace('.png', '').replace('_', ' ').title()
            await client.send_file(TELEGRAM_PHONE, chart, caption=f"📈 {chart_name}")
            print(f"✓ Sent {os.path.basename(chart)}")
    
     # Send reports with captions
    for report in report_files:
        if os.path.exists(report):
            report_name = os.path.basename(report).replace('.txt', '').replace('_', ' ').title()
            await client.send_file(TELEGRAM_PHONE, report, caption=f"📄 {report_name}")
            print(f"✓ Sent {os.path.basename(report)}")
    
    
    # Send footer message
    await client.send_message(TELEGRAM_PHONE, 
        "✅ All reports delivered successfully!\n\n"
        "🤖 Powered by AI • Generated with Python + AutoGen + RAG"
    )
    print("✓ Sent footer message")
    
    print("\n✓ All files sent to Telegram!\n")

# It is a wrapper function — meaning it’s a simple helper that lets you call send_to_telegram() normally, even though the real sending function (send_telegram_reports) is asynchronous (async).
# client is your Telegram connection
# The with block:
    #1. Automatically starts and closes the Telegram connection properly.
    #2. You don’t need to manually call client.start() or client.disconnect()
# Normally, to call an async function (like send_telegram_reports), you must use await, but that only works inside another async function.
# Since send_to_telegram is a regular function (not async), we can’t use await directly.
# So instead, we use: client.loop.run_until_complete(...)
def send_to_telegram(report_files, chart_files):
    """Wrapper function to send reports"""
    with client:
        client.loop.run_until_complete(send_telegram_reports(report_files, chart_files))

# The word async means this is an asynchronous function — it can pause and wait for Telegram actions to finish (like sending a message).
# await → tells Python to “wait” until the message is completely sent before moving to the next line.
async def test_telegram():
    """Test Telegram connection"""
    await client.send_message(TELEGRAM_PHONE, 
        '🚀 Test Message from Report System!\n\n'
        'If you see this, Telegram integration is working perfectly! ✅'
    )
    print("✅ Test message sent successfully!")

# This is a special Python condition. It checks if the file is being run directly (like python telegram_bot.py) instead of being imported somewhere else.
# If it is being run directly → the code below it will execute.
if __name__ == "__main__":
    print("Testing Telegram connection...")
    print(f"Sending to: {TELEGRAM_PHONE}")

    with client:
        client.loop.run_until_complete(test_telegram())
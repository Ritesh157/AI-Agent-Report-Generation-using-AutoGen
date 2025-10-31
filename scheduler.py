"""
Scheduler for automated daily report generation and email delivery
"""

import schedule # Used to run functions automatically at a set time every day.
import time # Allows the program to “sleep” for a while between checks.
from datetime import datetime # Used for timestamps.
import pytz # Handles time zones correctly (e.g., IST).
from config import SCHEDULE_TIME, TIMEZONE, RECIPIENT_EMAIL
from report_generator import (
    generate_sales_performance_report,
    generate_marketing_campaign_report,
    generate_quarterly_summary_report,
    save_report_to_file
)
from email_sender_html import send_html_email_with_charts
from visualizations import generate_all_charts
from telegram_sender import send_to_telegram
import os

# This function is responsible for:
    #1. Generating three types of reports (Sales, Marketing, Summary)
    #2. Saving them as .txt files
    #3. Creating visual charts
    #4. Sending everything via email
    #5. Sending the same to Telegram

def generate_and_send_daily_reports():
    """Generate reports and send via email"""

    print("\n" + "="*80)
    print(f"GENERATING DAILY REPORTS - {datetime.now(pytz.timezone(TIMEZONE)).strftime('%B %d, %Y %I:%M %p IST')}")
    print("="*80)

    report_files = [] # hold the filenames of all the generated reports.
    timestamp = datetime.now().strftime("%Y%m%d") # will be used to name the files uniquely each day (like 20251013).

    try:
        # Generate Sales Performance Report
        # It’s saved as daily_sales_report_20251013.txt
        # The filename is added to report_files list.
        print("\n[1/3] Generating Sales Performance Report...")
        sales_report = generate_sales_performance_report()
        sales_file = f"daily_sales_report_{timestamp}.txt"
        save_report_to_file(sales_report, sales_file)
        report_files.append(sales_file)
        print(f"✓ Saved: {sales_file}")

        # Generate Marketing Campaign Report
        print("\n[2/3] Generating Marketing Campaign Report...")
        marketing_report = generate_marketing_campaign_report()
        marketing_file = f"daily_marketing_report_{timestamp}.txt"
        save_report_to_file(marketing_report, marketing_file)
        report_files.append(marketing_file)
        print(f"✓ Saved: {marketing_file}")

        # Generate Combined Summary
        print("\n[3/3] Generating Executive Summary...")
        summary_report = generate_quarterly_summary_report("Q3 2024")
        summary_file = f"daily_executive_summary_{timestamp}.txt"
        save_report_to_file(summary_report, summary_file)
        report_files.append(summary_file)
        print(f"✓ Saved: {summary_file}")

        print("\n" + "="*80)
        print("REPORTS GENERATED SUCCESSFULLY")
        print("="*80)

        # Generate visualizations
        print("\n" + "="*80)
        print("GENERATING VISUALIZATIONS")
        print("="*80)

        chart_files = generate_all_charts()

        # Send email with reports and charts
        print("\n" + "="*80)
        print("SENDING BEAUTIFUL HTML EMAIL WITH CHARTS")
        print("="*80)

        success = send_html_email_with_charts(report_files, chart_files)

        if success:
            print("\n✓ Email sent successfully!")
        
        # Send to Telegram
        try:
            send_to_telegram(report_files, chart_files)
            print("\n✓ Telegram sent successfully!")
        except Exception as e:
            print(f"\n✗ Telegram error: {e}")
        
        print("\n" + "="*80)

    except Exception as e:
        print(f"\n✗ Error generating reports: {str(e)}")
        return False
    
    return True

# This function automatically runs your daily report generator (generate_and_send_daily_reports) at a fixed time every day
# This simply tells you:
    #1. When the job is set to run
    #2. What timezone is used
    #3. Which email the report will go to
    #4. And confirms the scheduler has started successfully
def start_scheduler():
    """Start the scheduler to run daily at specified time"""
    print("\n" + "="*80)
    print("AUTOMATED REPORT SCHEDULER")
    print("="*80)
    print(f"\nScheduled Time: {SCHEDULE_TIME} {TIMEZONE}")
    print(f"Recipient: {RECIPIENT_EMAIL}")
    print(f"Current Time: {datetime.now(pytz.timezone(TIMEZONE)).strftime('%I:%M %p IST')}")
    print("\nScheduler is running... Press Ctrl+C to stop.")
    print("="*80)

    # Schedule the job
    # Every day at the time in SCHEDULE_TIME (e.g., "09:00"),run the function generate_and_send_daily_reports()
    schedule.every().day.at(SCHEDULE_TIME).do(generate_and_send_daily_reports)

    # Run continuously
    # Runs an infinite loop that keeps your program alive.
    # Every 60 seconds, it checks if it’s time to run your job.
    # When the clock matches SCHEDULE_TIME, your report generator runs.
    # If you press Ctrl + C in the terminal, it stops gracefully.
    try:
        while True:
            schedule.run_pending()
            time.sleep(60) # Check every minute
    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user.")

def run_now():
    """Run report generation immediately (for testing)"""
    print("\nRunning report generation NOW (test mode)...\n")
    generate_and_send_daily_reports()

# How it works:
# If you run your script normally: -> It will start the daily scheduler
# If you run it with "now" argument: -> It will immediately generate and send the reports (test mode).
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "now":
        # Run immediately for testing
        run_now()
    else:
        # Start the scheduler
        start_scheduler()





"""
Enhanced email sending with HTML templates and embedded images
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from datetime import datetime
from config import GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL
from html_email_template import create_html_email
import os

# This is the main function that creates and sends the email
# report_files: a list of text report files (like ["sales_report.txt"])
# chart_files: a list of chart image files (like ["sales_chart.png"])

def send_html_email_with_charts(report_files, chart_files):
    """Send beautiful HTML email with embedded charts and report attachments"""

    # If your Gmail ID or App Password is not set in the config.py file, the script stops.
    # This ensures security — it won’t try to send an email without valid credentials

    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("Error: Email credential not configured!")
        return False
    
    # Create Email Subject

    today = datetime.now().strftime("%B %d, %Y")
    subject = f"📊 Daily Sales & Marketing Report - {today}"

    try:
        # Create Message
        # It sets the sender, receiver, and subject line
        msg = MIMEMultipart('related') # 'related' means this email can contain HTML + images + attachments
        msg['From'] = GMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject

        # Create alternative part for HTML
        # Emails can contain two versions:
        # 1. A plain text version — for simple email clients
        # 2. An HTML version — for fancy email clients like Gmail
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)

        # Plain text version (fallback)
        text_body = f"""Daily Sales & Marketing Report - {today}
Hello,

Please find attached your daily sales and marketing report with comprehensive visualization.

Report included:
"""
        for report_file in report_files:
            text_body +=f"- {os.path.basename(report_file)}\n"
        
        text_body += """
Best Regards,
Automated Report System
"""
        msg_alternative.attach(MIMEText(text_body, 'plain'))

        # HTML version with Chart.
        # create_html_email({}) is to make a nice, styled HTML layout with chats and text.
        html_body = create_html_email({})
        msg_alternative.attach(MIMEText(html_body, 'html'))

        # Embed charts images.
        chart_mapping = {
            'sales_by_region.png': 'sales_by_region',
            'quarterly_performance.png': 'quarterly_performance',
            'product_performance.png': 'product_performance',
            'marketing_roi.png': 'marketing_roi',
            'channel_performance.png': 'channel_performance'
        }

        # This goes through each image file (like sales_by_region.png, marketing_roi.png, etc.) in the list called chart_files
        for chart_file in chart_files:

            # This checks whether the image file actually exists on your computer before trying to use it.
            # If the file doesn’t exist, it just skips it to avoid errors.
            if os.path.exists(chart_file):

                # This extracts only the file name from the full path.
                # Example: 
                # if file path is: C:/Reports/Charts/sales_by_region.png then filename becomes "sales_by_region.png"
                filename = os.path.basename(chart_file)

                # This opens the image file in binary mode ('rb' means “read binary”) so Python can read the raw bytes (not text).
                # Images are not text files, so you need to read them as bytes
                with open(chart_file, 'rb') as f:

                    # This reads the image data and wraps it in a MIMEImage object.
                    # This special object tells the email system: "Hey, this is an image that can be shown inside the email."
                    # So now, img represents one image ready to attach
                    img = MIMEImage(f.read())

                    # This creates a Content ID (CID) for the image.
                    # A CID is like a unique name that lets the HTML part of the email display the image inline.
                    # Example:
                    # If filename = "sales_by_region.png", then it looks for "sales_by_region.png" in the chart_mapping dictionary.
                    # If it finds a match, cid will be "sales_by_region"
                    # If not, it will just use the filename without .png
                    cid = chart_mapping.get(filename, filename.replace('.png', ''))

                    # This adds a header to the image telling the email client: "This image’s unique ID is <sales_by_region>."
                    # Later, in HTML template, ywe can refer to this image like this: <img src="cid:sales_by_region">
                    img.add_header('Content-ID', f'<{cid}>')

                    # This says the image should be shown inline (inside the message) — not just attached as a downloadable file.
                    img.add_header('Content-Disposition', 'inline', filename=filename)

                    # Finally, this adds the image to the email message (msg) so that it gets sent along with the email.
                    msg.attach(img)
                print(f"✓ Embedded chart: {filename}")
        

        # Attach report files.
        # This part’s goal is to attach report files (like .txt files or other documents) to the email so the receiver can download them.

        # This goes through every report file in your list.
        for report_file in report_files:

            # This checks if that report file actually exists on your computer.
            # If it’s missing, Python skips it to avoid an error.
            if os.path.exists(report_file):

                # This opens the report file in binary mode ('rb' = “read binary”).
                # Even though it’s a text file, we open it in binary mode because emails handle attachments as raw bytes, not normal text.
                with open(report_file, 'rb') as f:

                    # f.read() reads the file’s contents (the entire report).
                    # MIMEApplication(...) wraps that data in a special email-friendly format called a MIME attachment.
                    # _subtype="txt" tells the email that this file is a text file.
                    attach = MIMEApplication(f.read(), _subtype= "txt")

                    # This adds a header that tells email clients (like Gmail or Outlook):
                    # 1. “This is an attachment, not inline content.”
                    # “And when the user downloads it, show the filename like demo_sales.txt.”
                    # os.path.basename(report_file) just extracts the filename (without the folder path)
                    attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(report_file))

                    # Now that the attachment is ready, this line actually adds it to the email message object (msg)
                    # So, when the email is sent, the recipient will see it as a downloadable attachment.
                    msg.attach(attach)
                print(f"✓ Attached report: {os.path.basename(report_file)}")
        
        # Send email via Gmail SMTP
        # This line removes any spaces from your Gmail App Password before using it to log in.
        app_password = GMAIL_APP_PASSWORD.replace(" ", "")

        # This section connects your Python program to Gmail’s mail server securely — so that it can send emails.
        print("\nConnecting to Gmail SMTP server...")

        # This line creates a connection to Gmail’s email sending server.
        # smtplib.SMTP → is a built-in Python library for sending emails using the SMTP protocol (Simple Mail Transfer Protocol — how emails are sent over the internet).
        # 'smtp.gmail.com' → is Gmail’s SMTP server address (where your email gets sent from).
        # 587 → is the port number used for TLS encryption (a secure connection).
        # the variable server now represents your active connection to Gmail’s SMTP service.
        server = smtplib.SMTP('smtp.gmail.com', 587)

        # This line upgrades your connection to be secure and encrypted using TLS (Transport Layer Security).
        # It makes sure your email and password are not sent in plain text over the internet.
        server.starttls()

        # This section logs in to your Gmail account using your email address and app password, so the program can send emails from your account.
        print("Logging in...")
        # It sends your email and app password securely to Gmail’s SMTP server (since we already did starttls() earlier, the connection is encrypted).
        # If credentials are correct: Gmail allows your program to send emails from your account.
        # If something’s wrong: Gmail will reject the login and you’ll get an error like smtplib.SMTPAuthenticationError.
        server.login(GMAIL_USER, app_password)

        print("Sending beautiful HTML email...")

        # This line does the real email sending.
        # server → This is your SMTP connection.
        # .send_message(...) → This method sends the email.
        # msg → This is the complete email you built earlier(with subject, sender and receiver info, text and HTML versions, attached files, embedded images).
        server.send_message(msg)

        # This command ends the connection with Gmail’s mail server.
        server.quit()

        print(f"\n✓ Beautiful HTML email sent successfully to {RECIPIENT_EMAIL}!")
        return True
    
    # This line catches any error (called an exception) that happens in the try block above.
    # For example, errors like: Wrong Gmail password, No internet connection, Invalid recipient email, Gmail server timeout.
    # Error details stored inside the variable e.
    except Exception as e:
        print(f"\n✗ Error sending email: {str(e)}")

        # The traceback module helps show exactly where the error happened in your code.
        import traceback

        # This prints the detailed error traceback —the full technical explanation of the error, including file name, line number, and function name
        traceback.print_exc()

        # This tells the program that sending the email failed.
        return False
    
if __name__ == "__main__":
    print("Testing HTML email with visualizations...")
    
    # Test with existing demo reports
    report_files = [
        "demo_sales_north_america.txt",
        "demo_marketing_q2_2024.txt",
        "demo_product_cloud_storage.txt"
    ]
    
    # Generate charts first
    from visualizations import generate_all_charts
    chart_files = generate_all_charts()
    
    # Send email
    send_html_email_with_charts(report_files, chart_files)





    

    

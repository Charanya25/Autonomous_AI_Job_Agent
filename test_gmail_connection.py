
import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def test_gmail_connection():
    print("\nGMAIL CONNECTION TEST")
    print("=" * 45)

    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("ERROR: Gmail credentials missing in .env")
        return

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)

        print("SUCCESS: Gmail SMTP connection established!")
        print("Gmail account:", GMAIL_ADDRESS)
        print("No email was sent.")

    except smtplib.SMTPAuthenticationError:
        print("ERROR: Gmail authentication failed.")
        print("Check your App Password in .env.")

    except Exception as error:
        print("Connection failed:", error)

if __name__ == "__main__":
    test_gmail_connection()

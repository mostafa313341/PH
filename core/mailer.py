import smtplib
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, make_msgid

class Mailer:
    def __init__(self):
        self.smtp_file = "data/smtp_config.csv"
        self.smtp_server = ""
        self.smtp_port = 587
        self.username = ""
        self.password = ""
        self.load_config()

    def load_config(self):
        if os.path.exists(self.smtp_file):
            try:
                with open(self.smtp_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self.smtp_server = row.get('host', '').strip()
                        self.smtp_port = int(row.get('port', 587))
                        self.username = row.get('username', '').strip()
                        self.password = row.get('password', '').strip()
                        break
            except Exception as e:
                print(f"Error: {e}")
    def send_phishing_email(self, target_email, subject, html_content, sender_name, sender_email):
        message = MIMEMultipart()
        message["From"] = formataddr((sender_name, sender_email))
        message["To"] = target_email
        message["Subject"] = subject
        message["Date"] = formatdate(localtime=True)
        message["Message-ID"] = make_msgid()
        message.attach(MIMEText(html_content, "html"))
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(sender_email, target_email, message.as_string())
            
            print(f"{sender_name} <{sender_email}>")
            return True
            
        except Exception as e:
            print(f"{e}")
            return False
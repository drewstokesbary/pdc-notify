from mail.gmail_api import GmailAPITransport
from mail.models import EmailMessage

def get_transport():
    return GmailAPITransport()

def send_message(message: EmailMessage) -> None:
    get_transport().send(message)
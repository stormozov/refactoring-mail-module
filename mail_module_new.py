import email
import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class GmailClient:
    """Initialize a GmailClient instance.

    Args:
        login (str): The login to use for the Gmail SMTP and IMAP servers.
        password (str): The password to use for the Gmail SMTP and IMAP servers.
        smtp_server (str): The hostname of the Gmail SMTP server.
        imap_server (str): The hostname of the Gmail IMAP server.

    Methods:
        send_message: Send an email message via the Gmail SMTP server.
        receive_message: Receive a message from the inbox with the given header.
    """
    def __init__(
            self,
            login: str,
            password: str,
            smtp_server: str,
            imap_server: str
    ) -> None:
        """Initialize a GmailClient instance.

        Args:
            login (str): The login to use for the Gmail SMTP and IMAP servers.
            password (str): The password to use for the Gmail SMTP
                and IMAP servers.
            smtp_server (str): The hostname of the Gmail SMTP server.
            imap_server (str): The hostname of the Gmail IMAP server.
        """
        self.login = login
        self.password = password
        self.smtp_server = smtp_server
        self.imap_server = imap_server

    def send_message(self, subj: str, recipient_list: list[str], body: str) \
            -> None:
        """Send an email message via the Gmail SMTP server.

        Args:
            subj: The subject of the message.
            recipient_list: The list of recipients of the message.
            body: The body of the message.

        Returns:
            None
        """
        msg = MIMEMultipart()
        msg['From'] = self.login
        msg['To'] = ', '.join(recipient_list)
        msg['Subject'] = subj
        msg.attach(MIMEText(body))

        with smtplib.SMTP(self.smtp_server, 587) as ms:
            ms.ehlo()
            ms.starttls()
            ms.ehlo()
            ms.login(self.login, self.password)
            ms.sendmail(self.login, recipient_list, msg.as_string())

    def receive_message(self, subject: str = None) -> (
            email.message.Message):
        """Receive a message from the inbox with the given subject.

        Args:
            subject: The subject of the message to receive. If None, the latest
                message is retrieved.

        Returns:
            The latest message with the given subject, or the latest message
                if no subject is provided.
        """
        with imaplib.IMAP4_SSL(self.imap_server) as mail:
            mail.login(self.login, self.password)
            mail.list()
            mail.select('inbox')
            criterion = '(HEADER Subject "%s")' % subject if subject else 'ALL'
            result, data = mail.uid('search', None, criterion)

            assert data[0], 'There are no letters with current header'

            latest_email_uid = data[0].split()[-1]
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]

            return email.message_from_string(raw_email)


if __name__ == '__main__':
    gmail_client = GmailClient(
        login='login@gmail.com',
        password='qwerty',
        smtp_server='smtp.gmail.com',
        imap_server='imap.gmail.com'
    )

    # Send message
    msg_subject = 'Subject'
    recipients = ['vasya@email.com', 'petya@email.com']
    message = 'Message'
    gmail_client.send_message(msg_subject, recipients, message)

    # Receive message
    header = None
    email_message = gmail_client.receive_message(header)
    print(email_message)

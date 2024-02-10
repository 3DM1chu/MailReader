import json
from email.header import decode_header

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import imaplib
import email

origins = [
    "http://localhost:3000",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/mail")
async def imap():
    with open("mails.txt", "r") as file:
        login = file.read()
    user = login.split("|")[0]
    password = login.split("|")[1]
    host = login.split("|")[2]

    # Connect securely with SSL
    mail = imaplib.IMAP4_SSL(host)
    ## Login to remote server
    mail.login(user, password)
    # Get the list of all mailboxes
    status, mailbox_list  = mail.list()

    if status == 'OK':
        for mailbox in mailbox_list:
            _, mailbox_name = mailbox.decode().split(' "/" ')
            mailbox_name = mailbox_name.strip('"')
            if mailbox_name == "Wersje robocze":
                continue

            # Select the current mailbox
            mail.select(mailbox_name)

            # Search for all emails in the current mailbox
            status, data = mail.search(None, 'ALL')

            # Iterate through all emails in the current mailbox
            if status == 'OK':
                for num in data[0].split():
                    status, data = mail.fetch(num, '(RFC822)')
                    if status == 'OK':
                        raw_email = data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        subject = decode_header(msg['Subject'])
                        subject = ''.join(
                            [part[0].decode(part[1] or 'utf-8') if isinstance(part[0], bytes) else part[0] for part in
                             subject])
                        sender = msg['From']
                        if "ubereats@uber.com" not in sender:
                            continue
                        #print(msg)
                        print(f'Message in {mailbox_name} - {num}\nSubject: {subject}\nFrom: {sender}\n')

    else:
        print("Failed to fetch mailboxes")

    # Logout from the server
    mail.logout()

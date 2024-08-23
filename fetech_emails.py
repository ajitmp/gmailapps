from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from bs4 import BeautifulSoup
import os.path

def get_urls(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all anchor tags in the HTML
    anchor_tags = soup.find_all('a')
    # Extract the URLs from the href attribute of each anchor tag
    urls = [a['href'] for a in anchor_tags if 'href' in a.attrs]
    return urls

def get_urls_from_text(emailtext):
    result =list()
    lines = emailtext.split('\n')
    for line in lines:
        if line.startswith('Read'):
            result.append(line.split()[3])
    return result

def main():
    # Define the scope of the access request
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    # Load credentials from token.json
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Check if credentials are valid, otherwise prompt for login again
    if not creds or not creds.valid:
        print("Credentials are invalid. Please authenticate again using gmail_auth.py.")
        return

    # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)

    # Get the list of emails
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
    else:
        print('Messages:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            #print(f"Message snippet: {msg['snippet']}")

            # Decode the message payload to get the email content
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                    #if part['mimeType'] == 'text/html':
                        data = part['body']['data']
                        text = base64.urlsafe_b64decode(data).decode('utf-8')
                        #print(f"Email content: {text}")
                        print(get_urls_from_text(text))
                        print("--------------------------")
            else:
                # Handle single part messages
                data = msg['payload']['body']['data']
                text = base64.urlsafe_b64decode(data).decode('utf-8')
                print(f"Email content: {text}")

if __name__ == '__main__':
    main()

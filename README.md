# Python Email Server with GUI

A full-featured SMTP email server with GUI for sending real emails and testing locally.

## Features

- **Dual Mode Operation**
  - **Local Mode** - Test emails locally without internet
  - **External Mode** - Send real emails via Gmail/other SMTP servers
- **GUI Interface** - Easy-to-use tkinter-based interface
- **SMTP Server** - Built-in server to receive emails using modern aiosmtpd
- **Send Real Emails** - Send to Gmail, Yahoo, Outlook, etc.
- **File Attachments** - Attach multiple files to emails
- **CC/BCC Support** - Send to multiple recipients
- **Inbox** - View all received emails with clear/refresh options
- **Server Log** - Monitor activity in real-time with timestamps
- **Email Validation** - Validates email format before sending
- **Connection Testing** - Test SMTP settings before sending

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- aiosmtpd

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Start the Application

```bash
python email_server.py
```

### Using the GUI

1. **Server Tab** (for receiving emails locally)
   - Enter host (default: localhost) and port (default: 1025)
   - Click "Start Server" to begin receiving emails
   - Monitor incoming emails in the server log
   - Click "Stop Server" to stop receiving emails

2. **Send Email Tab**
   
   **SMTP Configuration:**
   - **Local Mode** - Send to your local server for testing
   - **External Mode** - Send real emails to Gmail, etc.
     - Enter SMTP server (e.g., smtp.gmail.com)
     - Enter port (587 for Gmail)
     - Enter your email and App Password
     - Click "Test Connection" to verify settings
   
   **Email Details:**
   - Fill in From, To, CC, BCC, Subject, and Message
   - Add file attachments using "Add File" button
   - Multiple recipients supported (comma-separated)
   - Click "Send Email" to send

3. **Inbox Tab**
   - View all received emails in the list
   - Click on an email to view its full content
   - Use "Refresh" to update the display
   - Use "Clear Inbox" to delete all emails
   - Email counter shows total received emails

## Usage Examples

### Local Testing
1. Start the server using the "Server" tab
2. Switch to "Send Email" tab (keep "Local Mode" selected)
3. Send a test email
4. Check the "Inbox" tab to see the received email

### Sending Real Emails (Gmail)
1. **Setup Gmail App Password:**
   - Go to myaccount.google.com/apppasswords
   - Enable 2-Factor Authentication if not already enabled
   - Generate an App Password for "Mail"
   - Copy the 16-character password

2. **Configure in App:**
   - Switch to "Send Email" tab
   - Select "External (Real Emails)" mode
   - SMTP Server: smtp.gmail.com
   - Port: 587
   - Email: your-email@gmail.com
   - Password: [paste your App Password]
   - Click "Test Connection" to verify

3. **Send Email:**
   - Fill in recipient (e.g., kiprutobeauttah@gmail.com)
   - Add subject and message
   - Click "Send Email"
   - Email will be delivered to the real recipient!

## Improvements Over Original

- Uses modern `aiosmtpd` instead of deprecated `smtpd`/`asyncore`
- Proper server start/stop functionality
- Email format validation
- Port number validation
- Connection timeout handling
- Better error messages
- Inbox management (clear, refresh, counter)
- Timestamps in server log
- Thread-safe GUI updates
- Handles multipart emails correctly

## Notes

- This is a development server - not for production use
- Emails are only stored in memory (lost when app closes)
- Port 1025 is used to avoid requiring admin privileges
- Server runs in a background thread
- No authentication required (development only)

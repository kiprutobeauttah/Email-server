<div align="center">

# Python Email Server with GUI

[![Python Version](https://img.shields.io/badge/Python-3.7%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=flat-square&logo=windows&logoColor=white)](https://github.com/kiprutobeauttah/Email-server)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP8-black?style=flat-square)](https://www.python.org/dev/peps/pep-0008/)
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

A full-featured SMTP email server with GUI for sending real emails and testing locally.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture) • [Documentation](#documentation)

</div>

---

## Features

### Core Functionality
- <img src="https://img.icons8.com/fluency/20/000000/server.png"/> **Dual Mode Operation**
  - Local Mode - Test emails locally without internet
  - External Mode - Send real emails via Gmail/other SMTP servers
  - Direct Send - Attempt delivery without authentication

### Email Capabilities
- <img src="https://img.icons8.com/fluency/20/000000/email.png"/> **Send Real Emails** - Deliver to Gmail, Yahoo, Outlook, etc.
- <img src="https://img.icons8.com/fluency/20/000000/attach.png"/> **File Attachments** - Attach multiple files to emails
- <img src="https://img.icons8.com/fluency/20/000000/group.png"/> **CC/BCC Support** - Send to multiple recipients
- <img src="https://img.icons8.com/fluency/20/000000/inbox.png"/> **Inbox Management** - View, clear, and refresh received emails

### Technical Features
- <img src="https://img.icons8.com/fluency/20/000000/gui.png"/> **Modern GUI** - Easy-to-use tkinter-based interface
- <img src="https://img.icons8.com/fluency/20/000000/server-shutdown.png"/> **SMTP Server** - Built-in server using modern aiosmtpd
- <img src="https://img.icons8.com/fluency/20/000000/log.png"/> **Server Log** - Real-time activity monitoring with timestamps
- <img src="https://img.icons8.com/fluency/20/000000/checkmark.png"/> **Email Validation** - Format validation before sending
- <img src="https://img.icons8.com/fluency/20/000000/test-tube.png"/> **Connection Testing** - Verify SMTP settings before sending

## Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        A[Main Window] --> B[Server Tab]
        A --> C[Send Email Tab]
        A --> D[Inbox Tab]
    end
    
    subgraph "Business Logic Layer"
        E[Server Manager] --> F[Email Handler]
        G[SMTP Sender] --> H[Email Validator]
        G --> I[Message Builder]
    end
    
    subgraph "Network Layer"
        J[Local SMTP Server<br/>aiosmtpd]
        K[Direct Send<br/>DNS + SMTP]
        L[Authenticated SMTP<br/>Gmail/External]
    end
    
    subgraph "Data Layer"
        M[(Received Emails<br/>In-Memory)]
        N[Attachments<br/>File System]
    end
    
    B --> E
    C --> G
    D --> M
    
    E --> J
    G --> K
    G --> L
    
    F --> M
    I --> N
    
    J -.->|Receives| F
    K -.->|Sends| O[Recipient MX Server]
    L -.->|Sends| P[SMTP Server<br/>smtp.gmail.com]
    
    style A fill:#e1f5ff
    style E fill:#fff4e1
    style G fill:#fff4e1
    style J fill:#e8f5e9
    style K fill:#e8f5e9
    style L fill:#e8f5e9
    style M fill:#f3e5f5
    style N fill:#f3e5f5
```

### Component Overview

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **GUI Layer** | User interaction and display | tkinter |
| **Server Manager** | SMTP server lifecycle management | aiosmtpd, threading |
| **SMTP Sender** | Email transmission logic | smtplib, dnspython |
| **Email Handler** | Process incoming emails | aiosmtpd handlers |
| **Validators** | Input validation and sanitization | regex, custom logic |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/kiprutobeauttah/Email-server.git
cd Email-server

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Installation

## Project Structure

```
Email-server/
├── main.py                 # Application entry point
├── src/
│   ├── __init__.py
│   ├── email_handler.py    # Incoming email handler
│   ├── server_manager.py   # SMTP server management
│   ├── smtp_sender.py      # Email sending logic
│   ├── validators.py       # Input validation
│   └── gui/
│       ├── __init__.py
│       ├── main_window.py  # Main GUI window
│       ├── server_tab.py   # Server control tab
│       ├── send_tab.py     # Send email tab
│       └── inbox_tab.py    # Inbox tab
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

## Usage

## Usage Examples

### 1. **Server Tab** (for receiving emails locally)
   - Enter host (default: localhost) and port (default: 1025)
   - Click "Start Server" to begin receiving emails
   - Monitor incoming emails in the server log
   - Click "Stop Server" to stop receiving emails

### 2. **Send Email Tab**
   
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

### 3. **Inbox Tab**
   - View all received emails in the list
   - Click on an email to view its full content
   - Use "Refresh" to update the display
   - Use "Clear Inbox" to delete all emails
   - Email counter shows total received emails

## Testing Scenarios

### Local Testing
1. Start the server using the "Server" tab
2. Switch to "Send Email" tab (keep "Local Mode" selected)
3. Send a test email
4. Check the "Inbox" tab to see the received email

## Configuration

### Gmail SMTP Setup
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

## Technologies Used

| Technology | Purpose | Version |
|------------|---------|---------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | Core Language | 3.7+ |
| ![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=flat-square) | GUI Framework | Built-in |
| ![aiosmtpd](https://img.shields.io/badge/aiosmtpd-SMTP%20Server-green?style=flat-square) | Async SMTP Server | 1.4.4+ |
| ![dnspython](https://img.shields.io/badge/dnspython-DNS-orange?style=flat-square) | DNS Resolution | 2.3.0+ |
| ![smtplib](https://img.shields.io/badge/smtplib-SMTP%20Client-red?style=flat-square) | SMTP Client | Built-in |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Kipruto Beauttah**

[![GitHub](https://img.shields.io/badge/GitHub-kiprutobeauttah-181717?style=flat-square&logo=github)](https://github.com/kiprutobeauttah)
[![Email](https://img.shields.io/badge/Email-Contact-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:kiprutobeauttah@gmail.com)

## Support

If this project helped you, please consider giving it a star on GitHub!

## Screenshots

### Server Tab
![Server Tab](https://via.placeholder.com/800x400?text=Server+Tab+Screenshot)

### Send Email Tab
![Send Email Tab](https://via.placeholder.com/800x400?text=Send+Email+Tab+Screenshot)

### Inbox Tab
![Inbox Tab](https://via.placeholder.com/800x400?text=Inbox+Tab+Screenshot)

## Disclaimer

This is a development tool. Do not use in production environments without proper security measures.

## Known Issues

- Direct send mode may not work if ISP blocks port 25
- Some email providers may reject unauthenticated emails
- Emails sent via direct mode often end up in spam

## Resources

- [Gmail App Passwords](https://myaccount.google.com/apppasswords)
- [SMTP Protocol](https://tools.ietf.org/html/rfc5321)
- [aiosmtpd Documentation](https://aiosmtpd.readthedocs.io/)

---

<div align="center">
  
### Written by
  
<h2>
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=28&duration=3000&pause=1000&color=3776AB&center=true&vCenter=true&width=435&lines=Beauttah;Kipruto+Beauttah;Software+Developer" alt="Beauttah" />
</h2>

[![GitHub](https://img.shields.io/badge/GitHub-kiprutobeauttah-181717?style=flat-square&logo=github)](https://github.com/kiprutobeauttah)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://linkedin.com/in/kiprutobeauttah)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-FF5722?style=flat-square&logo=google-chrome&logoColor=white)](https://kiprutobeauttah.github.io)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:3776AB,100:2E9EF7&height=100&section=footer" width="100%"/>

</div>

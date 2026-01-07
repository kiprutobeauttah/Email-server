"""Email and input validation utilities"""

import re


class EmailValidator:
    """Validates email addresses and inputs"""
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @classmethod
    def validate_email(cls, email):
        """Validate single email address format"""
        return bool(cls.EMAIL_PATTERN.match(email.strip()))
    
    @classmethod
    def validate_email_list(cls, email_string):
        """Validate comma-separated email list"""
        if not email_string:
            return True, []
        
        emails = [e.strip() for e in email_string.split(',')]
        invalid = [e for e in emails if not cls.validate_email(e)]
        
        if invalid:
            return False, invalid
        return True, emails
    
    @staticmethod
    def validate_port(port_string):
        """Validate port number"""
        try:
            port = int(port_string)
            if 1 <= port <= 65535:
                return True, port
            return False, "Port must be between 1 and 65535"
        except ValueError:
            return False, "Port must be a number"

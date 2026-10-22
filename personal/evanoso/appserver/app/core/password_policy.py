"""Shared rules for newly created and changed passwords; login stays compatible."""
import re
import string
from typing import Annotated
from pydantic import AfterValidator, StringConstraints

PASSWORD_RULE = 'Use at least 12 characters with uppercase and lowercase letters, a number, and a symbol (maximum 72 UTF-8 bytes).'

def validate_password(value: str) -> str:
    if (len(value) < 12 or len(value.encode('utf-8')) > 72
            or not re.search(r'[A-Z]', value) or not re.search(r'[a-z]', value)
            or not re.search(r'[0-9]', value) or not any(c in string.punctuation for c in value)):
        raise ValueError(PASSWORD_RULE)
    return value

StrongPassword = Annotated[str, StringConstraints(strip_whitespace=False), AfterValidator(validate_password)]

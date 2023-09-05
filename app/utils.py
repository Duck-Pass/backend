import re


def is_valid_email(email):
    # Define a regex pattern for a basic email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    # Use re.match to check if the email matches the pattern
    if re.match(pattern, email):
        return True
    else:
        return False


def bytea_to_text(value):
    """
    Convert bytea PostgreSQL type to text
    :param bytea value: Value to convert
    :return: Converted value
    """

    bytea_as_bytes = bytes(value)
    return bytea_as_bytes.decode('utf-8')

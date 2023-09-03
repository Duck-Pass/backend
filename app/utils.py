def bytea_to_text(value):
    """
    Convert bytea PostgreSQL type to text
    :param bytea value: Value to convert
    :return: Converted value
    """

    bytea_as_bytes = bytes(value)
    return bytea_as_bytes.decode('utf-8')

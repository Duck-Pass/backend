def bytea_to_text(value):
    bytea_as_bytes = bytes(value)
    return bytea_as_bytes.decode('utf-8')

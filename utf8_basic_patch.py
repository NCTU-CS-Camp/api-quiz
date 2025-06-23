import requests, base64

def _basic_auth_str_utf8(username: str, password: str) -> str:
    creds = f"{username}:{password}".encode("utf-8")
    token = base64.b64encode(creds).decode("ascii")
    return f"Basic {token}"
requests.auth._basic_auth_str = _basic_auth_str_utf8
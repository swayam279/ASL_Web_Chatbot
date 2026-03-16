from urllib.parse import urlparse

import requests


def url_checker(url, timeout= 10):
    parsed= urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False
    
    try:
        r= requests.head(url, allow_redirects=True, timeout= timeout)
        if r.status_code < 400:
            return True
        
        r = requests.get(url, stream=True, allow_redirects=True, timeout=timeout)
        return r.status_code < 400
    except Exception:
        return False
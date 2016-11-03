""" Module to check texts for bullshit with the BlaBlaMeter

See http://www.blablameter.com for info about the BS index.
The site does not offer an official API, so use at your own risk.
"""

import requests
import re

def check_bullshit(text, lang='en'):
    """Check the `text` for bullshit.

    Returns the BS index.

    `lang` can be one of 'en', 'de', 'es'.
    """

    if lang=='en':
        url = 'http://www.blablameter.com/index.php'
        data={'bc_input': text}
    elif lang=='de':
        url = 'http://www.blablameter.de/index.php'
        data={'bc_ip': text}
    elif lang=='es':
        url = 'http://www.blablameter.com/spanish/index.php'
        data={'bc_input': text}
    else:
        raise ValueError("Unknown language: %s"%(lang,))

    r = requests.post(url, data=data)
    if r.status_code != 200:
        raise ValueError("Wrong HTTP response: %d"%(r.status_code,))

    text = r.text
    match = re.search(r'Bullshit-Index ([-+\d.]+)', text)
    if not match:
        raise ValueError("No BS index found in response.")

    BS = float(match.group(1))
    return BS

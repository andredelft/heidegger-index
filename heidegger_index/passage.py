import requests
from bs4 import BeautifulSoup
from pyCTS import CTS_URN


STRIP_TAGS = ["bibl", "label", "note"]


def strip_tei_xml(xml: str):
    body = BeautifulSoup(xml, "xml").TEI

    if not body:
        return

    for el in body(STRIP_TAGS):
        el.decompose()

    return body.text.strip()


def get_perseus_passage(urn: str):
    if not CTS_URN(urn).passage_component:
        return

    api_url = f"https://scaife-cts.perseus.org/api/cts?request=GetPassage&urn={urn}"

    try:
        r = requests.get(api_url)
    except requests.HTTPError:
        return

    return strip_tei_xml(r.text)

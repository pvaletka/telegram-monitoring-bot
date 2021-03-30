import requests
from lxml import html
from typing import List

class DetainedInfo:
    name = ''
    citi = ''
    place = ''
    comments = ''
    wfName = ''
    id = 999999999

class VesnaParser:
    def parseTalbe(self, url) -> List[DetainedInfo]:
        table = requests.get(url)
        tree = html.fromstring(table.text)
        rows = tree.xpath("//table/tbody/tr[position() > 2]")
        result = []
        for row in rows:
            detained = DetainedInfo()
            allData = row.findall("td")
            detained.name = allData[1].text_content()
            detained.citi = allData[2].text_content()
            detained.place = allData[3].text_content()
            detained.comments = allData[4].text_content()
            result.append(detained)
        return result

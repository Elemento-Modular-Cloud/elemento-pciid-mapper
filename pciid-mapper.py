#! /bin/env python3

from io import BytesIO
from re import match
import pycurl
import json

REMOTE = "https://pci-ids.ucw.cz/v2.2/pci.ids"
VENDOR_KEYWORDS = {"10de": ["Tesla", "GeForce", "Quadro", "Audio", "RTX", "GTX", "GA102GL", "GA100", "[A"],
                   "8086": ["Iris", "Graphics"],
                   "1002": ["Radeon", "Instinct", "FirePro", "Vega", "Audio"],
                   "15b3": ["ConnectX"]}
VENDOR_WATCHLIST = {k: [] for k in VENDOR_KEYWORDS.keys()}
VENDOR_DATA = {}
MODELS_DATA = {}


def main():
    bytesBody = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, REMOTE)
    curl.setopt(curl.WRITEFUNCTION, bytesBody.write)
    curl.perform()
    curl.close()

    data = bytesBody.getvalue().decode("utf-8").splitlines()

    current_vendor = ''
    for index, line in enumerate(data):
        if match(r'\w', line):
            parts = line.split()
            if parts[0] is not current_vendor:
                if current_vendor in VENDOR_WATCHLIST.keys():
                    VENDOR_WATCHLIST[current_vendor][1] = index
                    print("vendor {} is {} {}"
                          .format(current_vendor,
                                  VENDOR_WATCHLIST[current_vendor][2],
                                  VENDOR_WATCHLIST[current_vendor][0:2]))
                if parts[0] in VENDOR_WATCHLIST.keys():
                    VENDOR_WATCHLIST[parts[0]] = [index, 0, ' '.join(parts[1:])]
            current_vendor = parts[0]

    VENDOR_DATA['0000'] = "None"
    MODELS_DATA['0000'] = []

    for (vendor_id, metadata) in VENDOR_WATCHLIST.items():
        VENDOR_DATA[vendor_id] = metadata[2]
        MODELS_DATA[vendor_id] = []
        limits = metadata[0:2]
        for line in data[limits[0] + 1:limits[1]]:
            line = line.replace('\t', '', 1)
            if match(r'\w', line):
                parts = line.split()
                mod = parts[0]
                desc = ' '.join(parts[1:])
                if any(keyword in desc for keyword in VENDOR_KEYWORDS[vendor_id]):
                    MODELS_DATA[vendor_id].append([desc, mod])

    with open('vendors.json', 'w') as f:
        json.dump(VENDOR_DATA, f, indent=2)

    with open('models.json', 'w') as f:
        json.dump(MODELS_DATA, f, indent=1)


if __name__ == "__main__":
    main()

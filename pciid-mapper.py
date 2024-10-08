#! /bin/env python3
# #******************************************************************************#
# # Copyright(c) 2019-2023, Elemento srl, All rights reserved                    #
# # Author: Elemento srl                                                         #
# # Contributors are mentioned in the code where appropriate.                    #
# # Permission to use and modify this software and its documentation strictly    #
# # for personal purposes is hereby granted without fee,                         #
# # provided that the above copyright notice appears in all copies               #
# # and that both the copyright notice and this permission notice appear in the  #
# # supporting documentation.                                                    #
# # Modifications to this work are allowed for personal use.                     #
# # Such modifications have to be licensed under a                               #
# # Creative Commons BY-NC-ND 4.0 International License available at             #
# # http://creativecommons.org/licenses/by-nc-nd/4.0/ and have to be made        #
# # available to the Elemento user community                                     #
# # through the original distribution channels.                                  #
# # The authors make no claims about the suitability                             #
# # of this software for any purpose.                                            #
# # It is provided "as is" without express or implied warranty.                  #
# #******************************************************************************#
#
# #------------------------------------------------------------------------------#
# #elemento-monorepo-server                                                      #
# #Authors:                                                                      #
# #- Gabriele Gaetano Fronze' (gfronze at elemento.cloud)                        #
# #- Filippo Valle (fvalle at elemento.cloud)                                    #
# #------------------------------------------------------------------------------#
#


from io import BytesIO
from re import match
import requests
import json

REMOTE = "https://pci-ids.ucw.cz/v2.2/pci.ids"
VENDOR_KEYWORDS = {"10de": ["Tesla", "GeForce", "Quadro", "Fermi", "Kepler", "Maxwell", "Pascal", "Volta", "Turing", "Ampere", "Hopper", "Ada Lovelace", "Audio", "RTX", "GTX", "GA102GL", "GA100", "[A", "[H", "[V", "[L", "[P"],
                   "8086": ["Iris", "Graphics"],
                   "1002": ["Radeon", "Instinct", "FirePro", "Vega", "Audio"],
                   "15b3": ["ConnectX"]}
VENDOR_WATCHLIST = {k: [] for k in VENDOR_KEYWORDS.keys()}
VENDOR_DATA = {}
MODELS_DATA = {}
PCI_JS_DATA = []
HEADERS={"User-Agent": "Elemento/www.elemento.cloud/hello@elemento.cloud/AtomOS",
         "Accept-Encoding":"gzip"}

def main():
    req = requests.get(REMOTE, headers=HEADERS)

    data = req.content.decode("utf-8").splitlines()

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
    PCI_JS_DATA.append(
        {
            "name": "None",
            "id": "0000",
            "models": [
                {
                    "name": "None",
                    "id": "0000"
                }
            ]
        }
    )

    for (vendor_id, metadata) in VENDOR_WATCHLIST.items():
        VENDOR_DATA[vendor_id] = metadata[2]
        MODELS_DATA[vendor_id] = []
        JS_VENDOR = {
            "name": metadata[2],
            "id": vendor_id,
            "models": []
        }
        limits = metadata[0:2]
        for line in data[limits[0] + 1:limits[1]]:
            line = line.replace('\t', '', 1)
            if match(r'\w', line):
                parts = line.split()
                mod = parts[0]
                desc = ' '.join(parts[1:])
                if any(keyword in desc for keyword in VENDOR_KEYWORDS[vendor_id]):
                    MODELS_DATA[vendor_id].append([desc, mod])
                JS_VENDOR["models"].append({
                    "name": desc,
                    "id": mod
                })
        PCI_JS_DATA.append(JS_VENDOR)


    with open('vendors.json', 'w') as f:
        json.dump(VENDOR_DATA, f, indent=2)

    with open('models.json', 'w') as f:
        json.dump(MODELS_DATA, f, indent=1)

    with open('javascript_vendor_models.json', 'w') as f:
        json.dump(PCI_JS_DATA, f, indent=2)


if __name__ == "__main__":
    main()

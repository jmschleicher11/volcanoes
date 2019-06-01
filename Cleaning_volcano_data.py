## Getting volcano data

import urllib3
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import load_workbook, worksheet
import numpy as np
import regex as re
import requests
from tqdm import tqdm
tqdm.pandas()


import sys
sys.path.append('../Data/')


def get_hyperlinks(filename):
    """ Access hyperlinks from excel file """
    wb = load_workbook(filename=filename)
    ws = wb.active

    hyperlinks = []
    for row in ws.rows:
        for cell in row:
            if cell.hyperlink is not None:
                hyperlinks.append(cell.hyperlink.display)
    codes = [int(re.search('[0-9]{6}', row).group(0)) for row in hyperlinks]

    html_codes = pd.DataFrame({'hyperlinks': hyperlinks,
                                'Volcano Number': codes})
    return html_codes

holocene = get_hyperlinks('../Data/GVP_Volcano_List_Holocene.xlsx')
pleistocene = get_hyperlinks('../Data/GVP_Volcano_List_Pleistocene.xlsx')

# Read all data into dataframes
volcanoes_H = pd.read_excel('../Data/GVP_Volcano_List_Holocene.xlsx')
volcanoes_P = pd.read_excel('../Data/GVP_Volcano_List_Pleistocene.xlsx')

# Add html links to dataframes
volcanoes_H = volcanoes_H.merge(holocene, on='Volcano Number', how='left')
volcanoes_H['time_period'] = 'H'
volcanoes_P = volcanoes_P.merge(pleistocene, on='Volcano Number', how='left')
volcanoes_P['time_period'] = 'P'

# Combine dataframes into 1
volcanoes = pd.concat([volcanoes_H, volcanoes_P], axis=0)

# Rename columns
volcanoes = volcanoes.rename(columns={'Volcano Number': 'id',
'Volcano Name': 'name','Country': 'country',
'Primary Volcano Type': 'primary_type', 'Activity Evidence': 'activity',
'Last Known Eruption': 'last_eruption', 'Region': 'region',
'Subregion': 'subregion', 'Latitude': 'latitude', 'Longitude': 'longitude',
'Elevation (m)': 'elevation_m', 'Dominant Rock Type': 'rock_type',
'Tectonic Setting': 'tectonic_setting'})

volcanoes.to_csv('../Data/all_volcano_data.csv', index=False)

def volcano_pages(volcanoes):
    r = requests.get(volcanoes['hyperlinks'], allow_redirects=True)
    open('../Data/volcano_html_pages/'+str(volcanoes['id'])+'.html','wb')\
        .write(r.content)

volcanoes.progress_apply(volcano_pages, axis=1)

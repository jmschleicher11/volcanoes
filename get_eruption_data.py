from bs4 import BeautifulSoup
import pandas as pd
import regex as re

def clean_dates(date, certainty):
    if certainty == 'Discredited':
        return None
    else:
        ## Make BCE years negative
        if re.search('BCE', date):
            date = re.split('BCE()', date)[0]
            date = re.sub('[^\w]', '', date)
            date = int(re.match(r'\d{4}', date)[0])
            date = -date
        ## Extract year, removing extra information
        elif re.search('\d', date):
            date = re.split('[±()]', date)[0]
            date = re.sub('[^\w]', '', date)
            date = int(re.match(r'\d{4}', date)[0])
        ## If no date information, return None
        ## Note: column converted to floats if NaN is present
        else:
            date = None
        return date

def eruption_range(row):

    start = clean_dates(row['start_date'], row['eruption_certainty'])
    end = clean_dates(row['stop_date'], row['eruption_certainty'])

    ## Use the start and end date to make a range of eruption years
    if pd.notnull(start) & pd.notnull(end):
        eruption_years = list(range(start, end+1))
    else:
        eruption_years = start
    return eruption_years

def parse_table(volc):

    print(volc)
    ## Read each volcano's html page as a soup object
    soup = BeautifulSoup(open("../Data/volcano_html_pages/"+str(volc)+".html"),
                    "html.parser")
    ## Identify eruption tables in file
    table = soup.find("table",
        attrs={"class":"DivTable",
               "title": "Eruption history table for this volcano"})

    if table:
        ## Get the headings for the table
        headings = [th.get_text() for th in table.find("tr").find_all("th")]

        headings = [text.replace(" ", "_").lower() for text in headings]

        ## Parse entries in the table
        datasets = []
        for row in table.find_all("tr")[1:]:
            datasets.append([td.get_text() for td in row.find_all("td")])

        eruption_df = pd.DataFrame(datasets, columns=headings)

        eruption_df['id'] = volc

        eruption_df['eruption_years'] = eruption_df\
            .apply(eruption_range, axis=1)

        return eruption_df

    else:
        return


volcano_info = pd.read_csv('../Data/all_volcano_data.csv')
all_eruptions = pd.concat([parse_table(volc) for volc in volcano_info['id']])
all_eruptions.to_csv('../Data/all_eruption_data.csv', index=False)

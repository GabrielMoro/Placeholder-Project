import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re


def get_tables(url, parser='lxml', attrs={"class": "wikitable"}):
    '''
    Input: 
        url : str 
            URL to a webpage containing at least one table
        parser: str
             "param features" from BeautifulSoup's constructor 
             method (Optional, default = 'lxml')
        attrs: dict
            "param attrs" for BeautifulSoup's find_all method
            (Optional, default = {"class": "wikitable"})
    
    Output:
        tables : bs4.element.ResultSet
            list of HTML tags (bs4.element.Tag)
    '''

    page = requests.get(url)
    soup = BeautifulSoup(page.content, parser)
    tables = soup.find_all('table', attrs)

    return tables


def get_dataframe(table, find_rows=['td'], header_attrs={}, regex_in="\[.*\]$|\n", regex_out=''):
    '''
    Input: 
        table : bs4.element.Tag
            HTML tags of a table
        find_rows : list
            str list of HTML table tags
            (Optional, default = ['td'])
        header_attrs : dict
            dictionary of HTML tag attributes
            (e.g. {'class': '...', 'scope' : '...'})
            (Optional, default = {})
        regex_in : str
            regular expression used to filter table 
            header and content text 
            (Optional, default = "\[.*\]$|\n")
        regex_out : str
            string that replaces the pattern occurrences
            of 'regex_in' (Optional, default = '')
        
    Output:
        data : pandas.DataFrame
            pandas dataframe containing the data 
            from the input table
    '''

    # Get header
    headers = []
    for i in table.find_all('th', header_attrs):
        title = re.sub(regex_in, regex_out, i.text)
        headers.append(title)

    # Create and fill dataframe
    data = pd.DataFrame(np.ones((len(table.find_all('tr')[1:]), len(headers)))
                        * np.nan, columns=headers)
    for i, row in enumerate(table.find_all('tr')[1:]):
        row_data = row.find_all(find_rows)

        col = 0
        for cell in row_data:
            row_span = 1
            col_span = 1

            # if rowspan/colspan
            if cell.has_attr('rowspan'):
                row_span = int(cell.attrs['rowspan'])
            if cell.has_attr('colspan'):
                col_span = int(cell.attrs['colspan'])

            while any(data.iloc[i, col:col+col_span].notnull()):
                col += 1

            data.iloc[i:i+row_span, col:col +
                      col_span] = re.sub(regex_in, regex_out, cell.text)

    return data


def map_fill(df1, df2, index, fill_cols):
    '''
    Input:
        df1 : pandas.DataFrame
            dataframe to be filled
        df2 : pandas.DataFrame
            dataframe containing data to fill df1
        index : str
            common column between both dataframes
        fill_cols : list
            string list with columns to be filled
    '''
    for col in fill_cols:
        df1[col] = df1[col].fillna(
            df1[index].map(df2.set_index(index)[col]))

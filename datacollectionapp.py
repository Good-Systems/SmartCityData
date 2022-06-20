# API Key ID
# 9yz7a9cjftdr9qbvdlhz4ii9l

# API Key Secret
# e48r6otlbnf9bt6qd6ymci5hudrbwbk582ulbccarit04orlr

from re import T
from telnetlib import AUTHENTICATION
from sodapy import Socrata
from sys import exit
import pandas as pd
import numpy as np
from sqlalchemy import null
import urllib3
import json


def search_Socrata(a, b, c):
    print("Input fields or NA")
    print("If searching a state government type state name in city and state feilds")
    city = a
    state = b
    topic_name = c
    city_api_list = pd.read_csv("city_api_list.csv", index_col=False)
    # if city_api_list.loc[city_api_list['City'].str.contains(city)] != None:
    if city_api_list["City"].eq(city).any() and city_api_list["State-Abbr."].eq(state).any():
        # print('True')
        # x = city index
        x = city_api_list.loc[city_api_list['City'].str.contains(city)]
        # x = website
        x = x.loc[x['State-Abbr.'].str.contains(state)]['API-site']
        # x = [data, austintx, gov]
        x = str(x).split()
        # x = austintx
        x = x[1]
        # var = ?search_context=austintexastransport
        var = '?search_context=' + str(x)
        var = var + '&q=' + str(topic_name)
        print(var)

    else:
        print("City Not Found.")
        var = ''
    return var


def searchCkan(a, b, c):
    #request_site = 'https://data.sanantonio.gov/api/3/action/package_search?q=health'
    print("Input fields or NA")
    print("If searching a state government type state name in city and state feilds")
    city = a
    state = b
    topic_name = c
    city_api_list = pd.read_csv("city_api_list.csv", index_col=False)
    # if city_api_list.loc[city_api_list['City'].str.contains(city)] != None:
    if city_api_list["City"].eq(city).any() and city_api_list["State-Abbr."].eq(state).any():
        # print('True')
        # x = city index
        x = city_api_list.loc[city_api_list['City'].str.contains(city)]
        # x = website
        x = x.loc[x['State-Abbr.'].str.contains(state)]['API-site']
        # x = [austintx, gov]
        x = str(x).split()
        # x = austintx
        x = x[1]
        # var = ?search_context=austintexas
        var = 'https://' + \
            str(x) + '/api/3/action/package_search?q=' + str(topic_name)
        print(var)

    else:
        print("City Not Found.")
        var = ''
    return var


def mainprogram(a, b, c):

    stoprg = 0
    city_domain = str(search_Socrata(a, b, c))
    if city_domain == '':
        # empty_df = pd.DataFrame(None, None)
        # return empty_df
        return None
    http = urllib3.PoolManager()

    # Scorata URL
    # request_site = 'https://api.us.socrata.com/api/catalog/v1' + city_domain
    # print(request_site)
    # Ckan URL
    # request_site = 'https://data.sanantonio.gov/api/3/action/package_search?q=health'
    # request_site = 'https://phoenixopendata.com/api/3/action/package_search?q=transport'
    # request_site = 'https://data.sanjoseca.gov/api/3/action/package_search?q=health'
    # request_site = 'https://data.milwaukee.gov/api/3/action/package_search?q=transport'

    # RIDB
    # request_site = 'https://ridb.recreation.gov/api/v1/'

    # ArcGis
    request_site = 'https://glendaleaz-cog-gis.hub.arcgis.com/api/feed/dcat-ap/2.0.1.json'
    request = http.request('GET', request_site)
    print("Request")
    print(request)
    #response_body = urlopen(request).read()
    data = request.data
    datastring = str(data)
    print("Data")
    print(data)
    if "error" in datastring:
        # request_site = 'https://phoenixopendata.com/api/3/action/package_search?q=transport'
        request_site = searchCkan(a, b, c)
        request = http.request('GET', request_site)
        print(request)
        # data = request.data
        data = json.loads(request.data)
        print(data)
    data = json.loads(request.data)
    # results_df = pd.json_normalize(data['results'])

    # Ckan
    # while True:
    #     results_df = pd.json_normalize(data['result'], record_path=['results'])
    #     if results_df.size == 0:
    #         return results_df
    #     break
    while True:
        if "socrata" in str(request_site):
            results_df = pd.json_normalize(data['results'])
            if results_df.size == 0:
                return results_df
            break
        if "api/3/action" in str(request_site):
            results_df = pd.json_normalize(
                data['result'], record_path=['results'])
            if results_df.size == 0:
                return results_df
            break
        else:
            # results_df = pd.json_normalize(
            #     data['dcat:dataset'], record_path=['dcat:dataset'])
            results_df = pd.json_normalize(
                data['dcat:dataset'])
            if results_df.size == 0:
                return results_df
            break
    print(results_df.to_string())
    if "socrata" in str(request_site):
        results_df['Index'] = range(1, len(results_df)+1)
        # print(results_df.head())
        results_df.set_index('Index')
        # ['resource.name']
        a = pd.DataFrame(data, columns=['Index', 'Name'], index=None)
        a['Index'] = results_df['Index']
        # SCORATA
        # Final displayed data frame page NAME & More Info
        a['Name'] = results_df['resource.name']
        a['More Info'] = results_df['permalink']
        return a
    if "api/3/action" in str(request_site):
        results_df['Index'] = range(1, len(results_df)+1)
        # print(results_df.head())
        results_df.set_index('Index')
        # ['resource.name']
        a = pd.DataFrame(data, columns=['Index', 'Name'], index=None)
     # CKAN
     #   Final displayed data frame Name & More Infor
        a['Name'] = results_df['title']
        a['More Info'] = results_df['url']
        a['Index'] = results_df['Index']
        print(a.to_string())
        # Drop the cell doesn't contain https
        httpString = "http"
        a = a[a['More Info'].str.contains(httpString) == True]
        a = a.dropna()
        a['Index'] = range(1, len(a)+1)
        # After drop all invalid data, assign the Index
        return a
    else:
        print("REACH HERE")
        results_df['Index'] = range(1, len(results_df)+1)
        # print(results_df.head())
        results_df.set_index('Index')
        # ['resource.name']
        a = pd.DataFrame(data, columns=['Index', 'Name'], index=None)
     # CKAN
     #   Final displayed data frame Name & More Infor
        a['Name'] = results_df['dct:title']
        a['More Info'] = results_df['dct:identifier']
        a['Keywords'] = results_df['dcat:keyword']
        a['Index'] = results_df['Index']
        print(a.to_string())
        # Drop the cell doesn't contain https
        httpString = "http"
        a = a[a['More Info'].str.contains(httpString) == True]
        a = a.dropna()
        # Drop all the things that do not contains the keywords
        print(a['Keywords'].to_string)
        print("Before Drop __________________")
        a['Keywords'] = a['Keywords'].astype('str').str.upper()
        print(a['Keywords'])
        # a = a[a['Keywords'].str.contains(str(c)) == True]
        a = a[a['Keywords'].str.contains(str.upper(c)) == True]
        a = a.drop(a.columns[3], axis=1)
        print("After Drop __________________")
        #a = a[a['More Info'].str.contains(httpString) == True]
        a['Index'] = range(1, len(a)+1)
        # After drop all invalid data, assign the Index
        return a
    # results_df.to_csv('results_test.csv')
    # print()

    '''
    #download the datasets process into a csv (need to move to a function)
    print("Select datasets seperated by commas", end = "")
    num_select = '1'
    #input("or type NA for none: ")
    if num_select != 'NA':
        num_select = num_select.split(",")
        for i in num_select:
            i = int(i)-1  
            #results_df.loc[i]
            x = results_df.iloc[i]
            z = x['resource.id']
            y = x['metadata.domain']
            #print(z)
            client = Socrata(y, None)
            results = client.get(z)
            final = pd.DataFrame.from_records(results)
            
            #data = json.loads(request.data)
            #final = pd.json_normalize(data['results'])
            
            y = results_df.loc[i]['resource.name'] + '.csv'
            final.to_csv(y)
            print("Downloaded", y)  
    
     '''


def downloaddata(a):
    print('test')
    # print(request.data)

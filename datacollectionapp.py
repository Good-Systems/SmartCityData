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

api_name = ''


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
        # x[1] api domain name
        domain = x[1]
        
        # x[2] api name
        global api_name
        api_name = city_api_list['Working'][int(x[0])]
        domain_name = generateName(str(domain), str(api_name), str(topic_name))
        return domain_name
        # var = ?search_context=austintexastransport
        var = '?search_context=' + str(x)
        var = var + '&q=' + str(topic_name)
        print(var)

    else:
        print("City Not Found.")
        var = ''
    return var


def generateName(x, api_name, topic_name):
    domain_name = ''
    if(api_name == 'socrata'):
        domain_name = 'https://api.us.socrata.com/api/catalog/v1'
        domain_name += '?search_context=' + x + '&q=' + str(topic_name)
    elif(api_name == 'ckan'):
        domain_name = 'https://' + x + '/api/3/action/package_search?q=' + topic_name
    else:
        domain_name = 'https://' + x + '/api/feed/dcat-ap/2.0.1.json'
    return domain_name


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


def searchArcGis(a, b, c):
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
        print("WEBSITE_______----------")
        print()
        # x = [austintx, gov]
        x = str(x).split()
        # x is the api website
        x = x[1]
        var = 'https://' + \
            str(x) + '/api/feed/dcat-ap/2.0.1.json'
        print(var)

    else:
        print("City Not Found.")
        var = ''
    return var


def mainprogram(a, b, c):

    # stoprg = 0
    # Find the request site
    request_site = search_Socrata(a, b, c)
    if request_site == '':
        print("Request Not Found")
        return None
    # if city_domain == '':
    #     # empty_df = pd.DataFrame(None, None)
    #     # return empty_df
    #     return None
    http = urllib3.PoolManager()

    # Scorata URL
    # request_site = 'https://api.us.socrata.com/api/catalog/v1' + city_domain
    # print(request_site)

    # RIDB
    # request_site = 'https://ridb.recreation.gov/api/v1/'

    # ArcGis
    #request_site = 'https://glendaleaz-cog-gis.hub.arcgis.com/api/feed/dcat-ap/2.0.1.json'
    request = http.request('GET', request_site)

    print("Request")
    print(request)

    #response_body = urlopen(request).read()
    # get data from the request
    data = request.data
    # get the json file from the request data
    data = json.loads(request.data)

    # datastring = str(data)
    # print("Data")
    # print(data)

    # if "error" in datastring:
    #     # request_site = 'https://phoenixopendata.com/api/3/action/package_search?q=transport'
    #     request_site = searchCkan(a, b, c)
    #     request = http.request('GET', request_site)
    #     data = request.data
    #     print("REACH THE ERROR IN CKAN REQUEST DATA")
    #     print(data)
    #     dataStringCkan = str(data)
    #     print(request)

    #     if "error".upper() in dataStringCkan.upper():
    #         print("REACH THE ERROR IN ")
    #         request_site = searchArcGis(a, b, c)
    #         request = http.request('GET', request_site)
    #         data = request.data
    #         # data = json.loads(request.data)
    #     # data = request.data
    #     # data = json.loads(request.data)
    #     print(data)

    # data = json.loads(request.data)

    while True:
        # Socrata
        # if "socrata" in str(request_site):
        #     results_df = pd.json_normalize(data['results'])
        #     if results_df.size == 0:
        #         return results_df
        #     break
        if api_name == 'socrata':
            results_df = pd.json_normalize(data['results'])
            # if results_df.size == 0:
            #     return results_df
            # break
        # Ckan
        elif api_name == 'ckan':
            results_df = pd.json_normalize(
                data['result'], record_path=['results'])
            # if results_df.size == 0:
            #     return results_df
            # break
        # ArcGis
        elif api_name == 'arcgis':
            # results_df = pd.json_normalize(
            #     data['dcat:dataset'], record_path=['dcat:dataset'])
            results_df = pd.json_normalize(data['dcat:dataset'])
            # if results_df.size == 0:
            #     return results_df
            # break
        if results_df.size == 0:
            return results_df
        break
    print(results_df.to_string())
    # Scorata
    if api_name == 'socrata':
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
    if api_name == 'ckan':
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
        # httpString = "http"
        # a = a[a['More Info'].str.contains(httpString) == True]
        # a = a.dropna()
        a['Index'] = range(1, len(a)+1)
        # After drop all invalid data, assign the Index
        return a
    if api_name == 'arcgis':
        print("REACH HERE")
        results_df['Index'] = range(1, len(results_df)+1)
        # print(results_df.head())
        results_df.set_index('Index')
        # ['resource.name']
        a = pd.DataFrame(data, columns=['Index', 'Name'], index=None)
     # ArcGis
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
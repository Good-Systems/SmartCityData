# API Key ID
# 9yz7a9cjftdr9qbvdlhz4ii9l

# API Key Secret
# e48r6otlbnf9bt6qd6ymci5hudrbwbk582ulbccarit04orlr

import html
from html.entities import html5
from html.parser import HTMLParser
from re import T
from telnetlib import AUTHENTICATION
from sodapy import Socrata
from sys import exit
import pandas as pd
import numpy as np
from sqlalchemy import null
import urllib3
import json

import requests

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
        #print(var)

    else:
        print("City Not Found.")
        var = ''
    return var


def generateName(x, api_name, topic_name):
    domain_name = ''
    if(api_name == 'socrata'):
        domain_name = 'https://api.us.socrata.com/api/catalog/v1'
        domain_name += '?search_context=' + x
        #if &q= already in url, add topic name to end of url after a %20
        if '&q=' in domain_name:
            domain_name += '%20' + topic_name
        else:
            domain_name += '&q=' + topic_name
    elif(api_name == 'ckan'):
        q = ''
        if '?q=' in x:
            #store ?q= to end of string into a variable and delete it from x
            q = x[x.find('?q='):]
            x = x[:x.find('?q=')]
        domain_name = 'https://' + x + '/api/3/action/package_search'
        if q != '':
            domain_name += q + '%20' + topic_name
        if topic_name != '' and q == '':
            domain_name += '?q=' + topic_name
    elif(api_name == 'arcgis'):
        domain_name = 'https://' + x + '/api/feed/dcat-ap/2.0.1.json'
    else: #custom arcgis url
        q = ''
        if '?q=' in x:
            #store ?q= to end of string into a variable and delete it from x
            q = x[x.find('?q='):]
            x = x[:x.find('?q=')]
        domain_name = 'https://' + x + '/api/v3/search'
        if q != '':
            domain_name += q + '%20' + topic_name
        if topic_name != "" and q == '':
            domain_name += "?q=" + topic_name
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
    print("Site: " + request_site)
    # ArcGis
    #request_site = 'https://glendaleaz-cog-gis.hub.arcgis.com/api/feed/dcat-ap/2.0.1.json'
    #do not check the SSL certificate, I know my links are secure
    http = urllib3.PoolManager()
    #request = http.request('GET', request_site)
    
    request = http.request('GET', request_site)
    print("Request")
    #print(request)
    #response_body = urlopen(request).read()
    # get data from the request
    data = request.data
    # get the json file from the request data
    data = json.loads(request.data)
    #datastring = str(data)
    # print("Data")
    # print(data)

    # ARCGIS backup data
    # load in arcgislookup.json as a dictionary
    # here is what arcgislookup looks like
    # {'search': 'hub.arcgis.com', 'result': {'count': 3400, 'records': [{'domain': 'gcc-map-covid-19-sb-county-gaviotacoast.hub.arcgis.com', 'firstSeen': 1586736000, 'lastSeen': 1607299200}]}}
    
    #set city to lowercase(a)
    # city = a.lower()
    # arcgis_sites = []
    # ARCbackup = False
    # with open('arcgislookup.json') as f:
    #     arcgislookup = json.load(f)
    #     # for item in result.records:
    #     # search domain for city name,
    #     # if city name is found, get the domain and add it to arcgis_sites list
    #     for item in arcgislookup['result']['records']:
    #         if item['domain'].find(city) != -1:
    #             print("Found ArcGIS site")
    #             print("Domain: " + item['domain'])
    #             arcgis_sites.append(item['domain'])
    #         else:
    #             print("No ArcGIS site found")
    #             print("Domain: " + item['domain'])
    # if len(arcgis_sites) > 0:
    #     ARCbackup = True

    #     topic_name = c
        
    #     for site in arcgis_sites:
    if api_name == 'arcgis':
        topic_name = c
        # remove any entries from the data that do not contain the topic name
        #data['dcat:dataset']
        #for item in data['dcat:dataset']:
        #if item['dct:title'].find(topic_name) != -1 and item['dct:description'].find(topic_name) != -1:
        #    delete item
        for item in data['dcat:dataset']:
            if item['dct:title'].find(topic_name) == -1 and item['dct:description'].find(topic_name) == -1:
                data['dcat:dataset'].remove(item)




    if api_name == 'arcgiscustom':
        #request_site = "https://opendata.arcgis.com/api/v3/search"
        topic_name = c
        postData = {
            "agg": {
                "fields": "downloadable,hasApi,source,tags,type,access"
            },
            "fields": {
                "datasets": "id,name,created,modified,modifiedProvenance,searchDescription,recordCount,source,extent,owner,thumbnailUrl,type,url,xFrameOptions,contentSecurityPolicy,siteUrl,tags,collection,size,initiativeCategories,slug,startDate,venue,initiativeId,initiativeTitle,organizers,isAllDay,onlineLocation,timeZone"
            },
            # "catalog": {
            #     "orgId": "any(qvkbeam7Wirps6zC)"
            # }#,
        #    "q": topic_name
        }
        options = {
            "method": 'POST',
            "body": postData,
            "json": True,
            "url": request_site
        }
        request = requests.post(request_site, headers={'Content-Type': 'application/json'}, json=postData)
        #request = requests.post(request_site)
        print(request.text)
        data = json.loads(request.text)

        meta = pd.json_normalize(data['meta'])
        # if data['next'] != None:, request_site = data['next'] and append contents of data to current data
        try: 
            #set a countdown timer of 30 seconds
            #if the timer runs out, stop the loop
            timer = 5

            while meta['next'].empty == False:
                if timer == 0:
                    break
                request_site2 = meta['next']
                print("Next request: ", request_site2[0])
                request = http.request('GET', request_site2[0])
                data2 = json.loads(request.data)
                # we can't just add since both are dictionaries
                data['data'] = data['data'] + data2['data']
                #replace data meta with new meta
                data['meta'] = data2['meta']
                meta = pd.json_normalize(data['meta'])
                #subtract 1 from timer every second, do not stop loop
                timer = timer - 1
        except:
            print("No more pages")





    # if "error" in datastring:
    #     if api_name == 'socrata':
    #         print("Socrata Error")
    #         return None
    #     elif api_name == 'ckan':
    #         print("Ckan Error")
    #         return None
    #     else:
    #         print("ArcGis Error")
    #         #if is ArcGis error,
    #         #the site is using https://github.com/koopjs/koop-provider-hub-search
    #         #The request must have at least one of the following filters: "id", "group", "orgid". If you provided a "site" option, ensure the site catalog has group and/or org information
    #         #so we need to call tahe request again with one of the filters above
    #         print("A")
    #         #we need to get the site name
    #         request_site = searchArcGis(a, b, c)
    #         request = http.request('GET', request_site)

            
    #         print("B")
    #         data = request.data
    #         print("C")
    #         print("DATA IS:")
    #         print(data)
    #         # get the json file from the request data
    #         data = json.loads(request.data)
    #         print("D")
    #         datastring = str(data)
    #         print("E")
    #         print("Data2")
    #         print(data)
    #         if "error" in datastring:
    #             print("ArcGis Error AGAIN")
    #             return None







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
            print("Socrata")
            #print(results_df)
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
        elif api_name == 'arcgiscustom':
            results_df = pd.json_normalize(data['data'])
        if results_df.size == 0:
            return results_df
        break
    #print(results_df.to_string())
    # Scorata
    if api_name == 'socrata':
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", results_df['resource.name'])
        

        results_df['Index'] = range(1, len(results_df)+1)
        # print(results_df.head())
        results_df.set_index('Index')
        # ['resource.name']
        a = pd.DataFrame(data, columns=['Name'], index=None)
        #a['Index'] = results_df['Index']
        # SCORATA
        # Final displayed data frame page NAME & More Info
        a['Name'] = results_df['resource.name']
        #a['More Info'] = results_df['permalink']
        #set a['Name'] as results_df['resource.name'] with an href link to the more info
        a['Name'] = '<a href="' + results_df['permalink'] + '">' + results_df['resource.name'] + '</a>'
        #a['Name'] = results_df['permalink']
        #a['Desc'] = "Description"
        # if results_df['resource.description'] > 50 chars, shorten it
        #a['Desc'] = results_df['resource.description']
        #if resource.description does not exist, r3 = 'No Description'
        #print("READ THIS RESOURCE DESC")
        #print(results_df['resource.description'])
        #print("READ THIS RESOURCE DESC")
        #strip the tags from the description
        results_df['resource.description'] = results_df['resource.description'].str.replace(r'\r', ' ', regex=True)
        results_df['resource.description'] = results_df['resource.description'].str.replace(r'\n', ' ', regex=True)
        results_df['resource.description'] = results_df['resource.description'].str.replace(r'<[^>]*>', ' ', regex=True)

        for index, desc in results_df['resource.description'].items():

            if desc is None or desc == '' or "http" in desc:
                results_df['resource.description'][index] = 'No description was provided.'
            
            elif len(desc) > 99:
                #print("MAX FOUND AT", results_df['resource.description'][index])
                #split until end of 50th char and the first space after
                r1 = desc[:100]
                #remove the last word
                r3 = r1.rsplit(' ', 1)[0]
                #This is the stored value
                try:
                    r4 = r1.rsplit(' ', 1)[1]
                except:
                    r4 = ''
                r1 = r3
                if len(desc) > 199:
                    r2 = r4 + desc[100:199]
                    #remove the last word
                    r2 = r2.rsplit(' ', 1)[0]
                    r3 = r1 + '<br>' + r2 + '...'
                else:
                    r2 = r4 + desc[100:]
                    r3 = r1 + '<br>' + r2
                #adding a period to the end of the description, if not found
                #if last char is a space, replace it with a period
                if desc[-1] == ' ':
                    desc = desc[:-1] + '.'
                elif r3[-1] != '.':
                    r3 = r3 + '.'
                #remove all words after "Data Update" or "Update Frequency"
                if "Data Update" in r3:
                    r3 = r3[:r3.find("Data Update")]
                elif "Update Frequency" in r3:
                    r3 = r3[:r3.find("Update Frequency")]
                
                results_df['resource.description'][index] = r3
            else:
                #adding a period to the end of the description, if not found
                #if last char is a space, replace it with a period
                if desc[-1] == ' ':
                    desc = desc[:-1] + '.'
                elif desc[-1] != '.':
                    desc = desc + '.'
                #remove all words after "Data Update" or "Update Frequency"
                try:
                    if "Data Update" in r3:
                        r3 = r3[:r3.find("Data Update")]
                    elif "Update " in r3:
                        r3 = r3[:r3.find("Update ")]
                except:
                    pass
                    
                results_df['resource.description'][index] = desc
            #remove all spaces before periods
            results_df['resource.description'][index] = results_df['resource.description'][index].replace(' .', '.')
            #else:
            #    print("NO MAX FOUND AT", results_df['resource.description'][index])
            #    r3 = results_df['resource.description'][index]
            #    results_df['resource.description'][index] = r3

        

            #r1 = results_df['resource.description'].str.split(' ', 
        #a['Desc'] = results_df['resource.description'].str.split(' ', 1).str[0]
        a['Name'] += '<br>' + results_df['resource.description']
        
        #a['Desc'] = results_df['resource.description']
        if 'resource.updatedAt' in results_df.columns:
            a['Last Updated'] = results_df['resource.updatedAt']
            # set display none for last updated
            a['Last Updated'] = '<span style="display:none;">' + a['Last Updated'] + '</span>'

        if 'resource.download_count' in results_df.columns:
            a['Popularity'] = results_df['resource.download_count']
            # set display none for popularity
            a['Popularity'] = '<span style="display:none">' + a['Popularity'].astype(str) + '</span>'
        #url = requests.get(results_df['permalink'])
        #soup = BeautifulSoup(url.content, 'html.parser')
        #a['Desc'] = soup
        #a['Desc'] = soup.find('meta', attrs={'name': 'description'})['content']

        return a
    if api_name == 'ckan':
        results_df['Index'] = range(1, len(results_df)+1)
        # print(results_df.head())
        results_df.set_index('Index')
        # ['resource.name']
        a = pd.DataFrame(data, columns=['Name'], index=None)
     # CKAN
     #   Final displayed data frame Name & More Infor
        a['Name'] = results_df['title']
        a['Name'] = '<a href="' + results_df['url'] + '">' + results_df['title'] + '</a>'
        #a['More Info'] = results_df['url']
        #a['Index'] = results_df['Index']
        #print(a.to_string())
        # Drop the cell doesn't contain https
        # httpString = "http"
        # a = a[a['More Info'].str.contains(httpString) == True]
        # a = a.dropna()
        results_df['notes'] = results_df['notes'].str.replace(r'\r', ' ', regex=True)
        results_df['notes'] = results_df['notes'].str.replace(r'\n', ' ', regex=True)
        results_df['notes'] = results_df['notes'].str.replace(r'<[^>]*>', ' ', regex=True)

        for index, desc in results_df['notes'].items():

            if desc is None or desc == '' or "http" in desc:
                results_df['notes'][index] = 'No description was provided.'

            elif len(desc) > 99:
                r1 = desc[:100]
                #remove the last word
                r3 = r1.rsplit(' ', 1)[0]
                #This is the stored value
                r4 = r1.rsplit(' ', 1)[1]
                r1 = r3
                if len(desc) > 199:
                    r2 = r4 + desc[100:199]
                    #remove the last word
                    r2 = r2.rsplit(' ', 1)[0]
                    r3 = r1 + '<br>' + r2 + '...'
                else:
                    r2 = r4 + desc[100:]
                    r3 = r1 + '<br>' + r2
                #adding a period to the end of the description, if not found
                #if last char is a space, replace it with a period
                if desc[-1] == ' ':
                    desc = desc[:-1] + '.'
                elif r3[-1] != '.':
                    r3 = r3 + '.'
                #remove all words after "Data Update" or "Update Frequency"
                if "Data Update" in r3:
                    r3 = r3[:r3.find("Data Update")]
                elif "Update Frequency" in r3:
                    r3 = r3[:r3.find("Update Frequency")]

                results_df['notes'][index] = r3
            else:
                #adding a period to the end of the description, if not found
                #if last char is a space, replace it with a period
                if desc[-1] == ' ':
                    desc = desc[:-1] + '.'
                elif desc[-1] != '.':
                    desc = desc + '.'
                #remove all words after "Data Update" or "Update Frequency"
                try:
                    if "Data Update" in r3:
                        r3 = r3[:r3.find("Data Update")]
                    elif "Update " in r3:
                        r3 = r3[:r3.find("Update ")]
                except:
                    pass

                results_df['notes'][index] = desc

            #remove all spaces before periods
            results_df['notes'][index] = results_df['notes'][index].replace(' .', '.')

        a['Name'] += '<br>' + results_df['notes']

        if 'metadata_modified' in results_df.columns:
            a['Last Updated'] = results_df['metadata_modified']
            # set display none for last updated
            a['Last Updated'] = '<span style="display:none;">' + a['Last Updated'] + '</span>'
        if 'num_resources' in results_df.columns:
            a['Popularity'] = results_df['num_resources']
            # set display none for popularity
            a['Popularity'] = '<span style="display:none">' + a['Popularity'].astype(str) + '</span>'

        return a
    if api_name == 'arcgis':
        #print("REACH HERE")
        results_df['Index'] = range(1, len(results_df)+1)
        # print(results_df.head())
        results_df.set_index('Index')
        # ['resource.name']
        a = pd.DataFrame(data, columns=['Name'], index=None)
     # ArcGis
     #   Final displayed data frame Name & More Infor
        #a['Name'] = results_df['dct:title']
        a['Name'] = '<a href="' + results_df['dct:identifier'] + '">' + results_df['dct:title'] + '</a>'
        #a['More Info'] = results_df['dct:identifier']
        #a['Keywords'] = results_df['dcat:keyword']
        #a['Index'] = results_df['Index']
        #print(a.to_string())
        # Drop the cell doesn't contain https
        #httpString = "http"
        #a = a[a['More Info'].str.contains(httpString) == True]
        #a = a.dropna()
        # Drop all the things that do not contains the keywords
        #print(a['Keywords'].to_string)
        #print("Before Drop __________________")
        #a['Keywords'] = a['Keywords'].astype('str').str.upper()
        #print(a['Keywords'])
        # a = a[a['Keywords'].str.contains(str(c)) == True]
        #a = a[a['Keywords'].str.contains(str.upper(c)) == True]
        #a = a.drop(a.columns[3], axis=1)
        #print("After Drop __________________")
        #a = a[a['More Info'].str.contains(httpString) == True]
        #a['Index'] = range(1, len(a)+1)
        # After drop all invalid data, assign the Index

        #strip the tags from the description
        results_df['dct:description'] = results_df['dct:description'].str.replace(r'\r', '', regex=True)
        results_df['dct:description'] = results_df['dct:description'].str.replace(r'\n', '', regex=True)
        results_df['dct:description'] = results_df['dct:description'].str.replace(r'<[^>]*>', '', regex=True)

        #reuse the exact same code from the Socrata section
        for index, desc in results_df['dct:description'].items():

            if desc is None or desc == '' or "http" in desc:
                results_df['dct:description'][index] = 'No description was provided.'
            
            elif len(desc) > 99:
                #print("MAX FOUND AT", results_df['resource.description'][index])
                #split until end of 50th char and the first space after
                r1 = desc[:100]
                #remove the last word
                r3 = r1.rsplit(' ', 1)[0]
                #This is the stored value
                r4 = r1.rsplit(' ', 1)[1]
                r1 = r3
                if len(desc) > 199:
                    r2 = r4 + desc[100:199]
                    #remove the last word
                    r2 = r2.rsplit(' ', 1)[0]
                    r3 = r1 + '<br>' + r2 + '...'
                else:
                    r2 = r4 + desc[100:]
                    r3 = r1 + '<br>' + r2
                #adding a period to the end of the description, if not found
                #if last char is a space, replace it with a period
                if desc[-1] == ' ':
                    desc = desc[:-1] + '.'
                elif r3[-1] != '.':
                    r3 = r3 + '.'
                #remove all words after "Data Update" or "Update Frequency"
                if "Data Update" in r3:
                    r3 = r3[:r3.find("Data Update")]
                elif "Update Frequency" in r3:
                    r3 = r3[:r3.find("Update Frequency")]
                
                results_df['dct:description'][index] = r3
            else:
                #adding a period to the end of the description, if not found
                #if last char is a space, replace it with a period
                if desc[-1] == ' ':
                    desc = desc[:-1] + '.'
                elif desc[-1] != '.':
                    desc = desc + '.'
                #remove all words after "Data Update" or "Update Frequency"
                try:
                    if "Data Update" in r3:
                        r3 = r3[:r3.find("Data Update")]
                    elif "Update " in r3:
                        r3 = r3[:r3.find("Update ")]
                except:
                    pass    
                results_df['dct:description'][index] = desc
            #remove all spaces before periods
            results_df['dct:description'][index] = results_df['dct:description'][index].replace(' .', '.')

        a['Name'] += '<br>' + results_df['dct:description']


        print("request_site", request_site)

        if 'dct:modified' in results_df.columns:
            a['Last Updated'] = results_df['dct:modified']
            # set display none for last updated
            a['Last Updated'] = '<span style="display:none;">' + a['Last Updated'] + '</span>'
        #if 'dct:'


        if 'dct:accrualPeriodicity' in results_df.columns:
            a['Popularity'] = results_df['dct:accrualPeriodicity']
            # set display none for popularity
            a['Popularity'] = '<span style="display:none">' + a['Popularity'].astype(str) + '</span>'

        return a
    # results_df.to_csv('results_test.csv')
    # print()
    if api_name == 'arcgiscustom':
        #print("REACH HERE")
        results_df['Index'] = range(1, len(results_df)+1)
        # print(results_df.head())
        results_df.set_index('Index')
        # ['resource.name']
        a = pd.DataFrame(data, columns=['Name'], index=None)

        a['Name'] = '<a href="' + results_df['links.itemPage'] + '">' + results_df['attributes.name'] + '</a>'

        #strip the tags from the description
        results_df['attributes.searchDescription'] = results_df['attributes.searchDescription'].str.replace(r'\r', '', regex=True)
        results_df['attributes.searchDescription'] = results_df['attributes.searchDescription'].str.replace(r'\n', '', regex=True)
        results_df['attributes.searchDescription'] = results_df['attributes.searchDescription'].str.replace(r'<[^>]*>', '', regex=True)

        #reuse the exact same code from the Socrata section
        for index, desc in results_df['attributes.searchDescription'].items():
                
                if desc is None or desc == '' or "http" in desc:
                    results_df['attributes.searchDescription'][index] = 'No description was provided.'
                
                elif len(desc) > 99:
                    #print("MAX FOUND AT", results_df['resource.description'][index])
                    #split until end of 50th char and the first space after
                    r1 = desc[:100]
                    #remove the last word
                    r3 = r1.rsplit(' ', 1)[0]
                    #This is the stored value
                    r4 = r1.rsplit(' ', 1)[1]
                    r1 = r3
                    if len(desc) > 199:
                        r2 = r4 + desc[100:199]
                        #remove the last word
                        r2 = r2.rsplit(' ', 1)[0]
                        r3 = r1 + '<br>' + r2 + '...'
                    else:
                        r2 = r4 + desc[100:]
                        r3 = r1 + '<br>' + r2
                    #adding a period to the end of the description, if not found
                    #if last char is a space, replace it with a period
                    if desc[-1] == ' ':
                        desc = desc[:-1] + '.'
                    elif r3[-1] != '.':
                        r3 = r3 + '.'
                    #remove all words after "Data Update" or "Update Frequency"
                    if "Data Update" in r3:
                        r3 = r3[:r3.find("Data Update")]
                    elif "Update Frequency" in r3:
                        r3 = r3[:r3.find("Update Frequency")]
                    
                    results_df['attributes.searchDescription'][index] = r3
                else:
                    #adding a period to the end of the description, if not found
                    #if last char is a space, replace it with a period
                    if desc[-1] == ' ':
                        desc = desc[:-1] + '.'
                    elif desc[-1] != '.':
                        desc = desc + '.'
                    #remove all words after "Data Update" or "Update Frequency"
                    try:
                        if "Data Update" in r3:
                            r3 = r3[:r3.find("Data Update")]
                        elif "Update " in r3:
                            r3 = r3[:r3.find("Update ")]
                    except:
                        pass
                    results_df['attributes.searchDescription'][index] = desc
                #remove all spaces before periods
                results_df['attributes.searchDescription'][index] = results_df['attributes.searchDescription'][index].replace(' .', '.')
        a['Name'] += '<br>' + results_df['attributes.searchDescription']

        if 'attributes.modified' in results_df.columns:
            a['Last Updated'] = results_df['attributes.modified']
            # set display none for last updated
            #convert unix epoch to date
            a['Last Updated'] = pd.to_datetime(a['Last Updated'], unit='ms')
            a['Last Updated'] = a['Last Updated'].dt.strftime('%Y-%m-%d')
            a['Last Updated'] = '<span style="display:none;">' + a['Last Updated'] + '</span>'
        if 'attributes.recordCount' in results_df.columns:
            a['Popularity'] = results_df['attributes.recordCount']
            # set display none for popularity
            a['Popularity'] = '<span style="display:none">' + a['Popularity'].astype(str) + '</span>'
        return a

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
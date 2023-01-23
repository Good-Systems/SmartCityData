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

# Testing out speed of requests vs urllib3 vs scrapy
# I decided to use scrapy from testing out speeds
# For 100 URL requests
# urllib3 -> 28.297308 s
# requests -> 28.1786405 s
# scrapy -> 1.4110803 s
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.spiders.init import InitSpider
from twisted.internet import reactor
import requests

api_name = ''
smartcitydata_api = {}

#ArcGis Popularity variables
fetch_url = []
dataSeries = pd.Series()
temp = []
#SCRAPY (For Quick ArcGIS API)
class ArcGisPopularity(InitSpider):
    name = "scrapythescraper"
    global temp

    def __init__(self, *args, **kwargs):
        self.start_requests()

    def start_requests(self):
        #print("DATA SERIES IS")
        #print(dataSeries)
        for url in fetch_url:
           #print("DE")
           yield scrapy.Request(url, callback=self.parse, dont_filter=True)
  
    def parse(self, response):
        jsonresponse = json.loads(response.body)
        #Error handling
        if 'error' in jsonresponse:
            id = response.url[response.url.rfind('/') + 1:response.url.find('?f=')]
            numViews = 0
            temp.append((id, numViews))
            return numViews
        id = jsonresponse['id']
        numViews = jsonresponse['numViews']
        #print(temp)
        temp.append((id, numViews))
        #print(numViews)
        return numViews
#END SCRAPY

def search_Socrata(a, b, c):
    print("Input fields or NA")
    print("If searching a state government type state name in city and state feilds")
    city = a
    state = b
    topic_name = c
    #if underscore in city name, replace with space
    #if '_' in city:
    #    city = city.replace('_', ' ')
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
        print(city)
        print("City Not Found.")
        var = ''
    return var


def generateName(x, api_name, topic_name):
    domain_name = ''
    if(api_name == 'socrata'):
        domain_name = 'https://api.us.socrata.com/api/catalog/v1'
        domain_name += '?search_context=' + x
        #if &q= already in url, adding topic name to end of url after a %20
        if '&q=' in domain_name:
            domain_name += '%20' + topic_name
        else:
            domain_name += '&q=' + topic_name
    elif(api_name == 'ckan'):
        q = ''
        if '?q=' in x:
            #storing ?q= to end of string into a variable and delete it from x
            q = x[x.find('?q='):]
            x = x[:x.find('?q=')]
        domain_name = 'https://' + x + '/api/3/action/package_search'
        if q != '':
            domain_name += q + '%20' + topic_name
        if topic_name != '' and q == '':
            domain_name += '?q=' + topic_name
        #Fixing # of datasets returned
        if '?q=' not in domain_name:
            domain_name += '?q=&rows=100'
        else:
            domain_name += '&rows=100'
    elif(api_name == 'arcgis'):
        domain_name = 'https://' + x + '/api/feed/dcat-ap/2.0.1.json'
    else: #custom arcgis url
        q = ''
        if '?q=' in x:
            #storing ?q= to end of string into a variable and delete it from x
            q = x[x.find('?q='):]
            x = x[:x.find('?q=')]
        domain_name = 'https://' + x + '/api/v3/search'
        if q != '':
            domain_name += q + '%20' + topic_name
        if topic_name != "" and q == '':
            domain_name += "?q=" + topic_name
        print("Found domain name:")
        print(domain_name)
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


def mainprogram(a, b, c, scdapi):
    global api_name

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
    arcgiscity = False
    if (api_name == 'arcgis'):
        if "?q=" in request_site:
            print("?Q= ON REQUEST SITE" + request_site)
            #remove the ?q= to the next / in the url
            #so request_site should go from gis.data.alaska.gov?q=juneau/api/feed/dcat-ap/2.0.1.json to gis.data.alaska.gov/api/feed/dcat-ap/2.0.1.json
            #remove the ?q= + a from the url
            request_site = request_site.split("?q=")[0] + "/api/feed/dcat-ap/2.0.1.json"
            print("NEW REQUEST SITE: " + request_site)
            arcgiscity = True
            

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
    backup = False
    try:
        data = json.loads(request.data)
    except:
        #We will use our Backup Database
        backup = True
        arcgiscity = True
        api_name = 'arcgiscustom'
        request_site = "https://hub.arcgis.com/api/v3/search"

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
            if topic_name != '':
                if item['dct:title'].find(topic_name) == -1 and item['dct:description'].find(topic_name) == -1 and topic_name in item['dcat:keyword']:
                    data['dcat:dataset'].remove(item)
            if arcgiscity:
                if item['dct:title'].find(a) == -1 and item['dct:description'].find(a) and a in item['dcat:keyword']:
                    data['dcat:dataset'].remove(item)
            #if ?q= is in the url, remove it and get the name after it
            
            




    if api_name == 'arcgiscustom' or backup:
        #request_site = "https://opendata.arcgis.com/api/v3/search"
        topic_name = c
        # postData = {
        #     "agg": {
        #         "fields": "downloadable,hasApi,source,tags,type,access"
        #     },
        #     "fields": {
        #         "datasets": "id,name,created,modified,modifiedProvenance,searchDescription,recordCount,source,extent,owner,thumbnailUrl,type,url,xFrameOptions,contentSecurityPolicy,siteUrl,tags,collection,size,initiativeCategories,slug,startDate,venue,initiativeId,initiativeTitle,organizers,isAllDay,onlineLocation,timeZone"
        #     },
        #     # "catalog": {
        #     #     "orgId": "any(qvkbeam7Wirps6zC)"
        #     # }#,
        # #    "q": topic_name
        # }
        # options = {
        #     "method": 'POST',
        #     "body": postData,
        #     "json": True,
        #     "url": request_site
        # }
        #Below are the official V3 API parameters
            # "parameters": {
            #     "query": "search term",
            #     "filter": "filter applied to search. Example: 'filter[tags]=airports'",
            #     "page[size]": "Number of resources per page. Example: 'page[size]=25' ",
            #     "page[number]": "The page number for the resources. Example: 'page[number]=2'"
            # }
        #ARCGIS ORGID Grabber
        # To get the orgid for a specific ArcGIS site
        # Go to detroitmi.maps.arcgis.com/sharing/rest/portals/self?culture=en&f=pjson
        # Go to masoncityiowa.maps.arcgis.com/sharing/rest/portals/self?culture=en&f=pjson
        # Get "id" from the JSON response
        # For example, the ID for Detroit Michigan is qvkbeam7Wirps6zC
        # For example, the ID for Mason City Iowa is 84FpxbPitJq31AWu
        # Then, replace the orgId in the postData below with the ID for the city you want to search
        #request_site_org will be request_site without anything past the first . in the URL
        if "hub.arcgis.com" in request_site:
            if (not backup):
                request_site_org = request_site.split(".")[0]
                requestOrg = request_site_org + ".maps.arcgis.com/sharing/rest/portals/self?culture=en&f=pjson"
                # Gett "id" from the JSON response
                org_id = requests.get(requestOrg).json()['id']
                print("Org ID: " + org_id)
            else:
                org_id = ""

            if (not backup):
                if topic_name != "":
                    postData = {
                        "agg": {
                            "fields": "downloadable,hasApi,source,tags,type,access",
                            "size": "100"
                        },
                        "fields": {
                            "datasets": "id,name,created,modified,modifiedProvenance,searchDescription,recordCount,source,extent,owner,thumbnailUrl,type,url,xFrameOptions,contentSecurityPolicy,siteUrl,tags,collection,size,initiativeCategories,slug,startDate,venue,initiativeId,initiativeTitle,organizers,isAllDay,onlineLocation,timeZone"
                        },
                        "catalog": {
                            "orgId": "any(" + org_id + ")"
                        },
                        "q": topic_name
                    }
                else:
                    postData = {
                        "agg": {
                            "fields": "type,access,source,categories,license,tags,region,sector",
                            "size": "100"
                        },
                        "fields": {
                            "datasets": "id,name,created,modified,modifiedProvenance,searchDescription,recordCount,source,extent,owner,thumbnailUrl,type,url,xFrameOptions,contentSecurityPolicy,siteUrl,tags,collection,size,initiativeCategories,slug,startDate,venue,initiativeId,initiativeTitle,organizers,isAllDay,onlineLocation,timeZone"
                        },
                        "catalog": {
                            "orgId": "any(" + org_id + ")"
                        },
                        "q": a
                }
            else:
                if topic_name != "":
                    postData = {
                        "agg": {
                            "fields": "downloadable,hasApi,source,tags,type,access",
                            "size": "100"
                        },
                        "fields": {
                            "datasets": "id,name,created,modified,modifiedProvenance,searchDescription,recordCount,source,extent,owner,thumbnailUrl,type,url,xFrameOptions,contentSecurityPolicy,siteUrl,tags,collection,size,initiativeCategories,slug,startDate,venue,initiativeId,initiativeTitle,organizers,isAllDay,onlineLocation,timeZone"
                        },
                        "q": a + " " + topic_name
                    }
                else:
                    postData = {
                        "agg": {
                            "fields": "type,access,source,categories,license,tags,region,sector",
                            "size": "100"
                        },
                        "fields": {
                            "datasets": "id,name,created,modified,modifiedProvenance,searchDescription,recordCount,source,extent,owner,thumbnailUrl,type,url,xFrameOptions,contentSecurityPolicy,siteUrl,tags,collection,size,initiativeCategories,slug,startDate,venue,initiativeId,initiativeTitle,organizers,isAllDay,onlineLocation,timeZone"
                        },
                        "q": a
                }

            #request_site = request_site
            request = requests.post(request_site, headers={'Content-Type': 'application/json'}, json=postData)
        else:
            request = requests.post(request_site)
        print("Requesting from:" + request_site)
        #print(request.text)
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

        for item in data['data']:
            if item.get('name') == None:
                data['data'].remove(item)
                continue
            if topic_name != '':
                if item['name'].find(topic_name) == -1 and item['searchDescription'].find(topic_name) == -1:
                   data['data'].remove(item)
            if arcgiscity:
                if item['name'].find(a) == -1 and item['searchDescription'].find(a) == -1:
                    data['data'].remove(item)

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
        a['Name'] = '<a href="javascript:;" onclick="socrata_preview(\'' + results_df['permalink'] + '\')">' + results_df['resource.name'] + '</a>'
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
                
                if not scdapi: # API -> Full Description # Web -> Shortened Description
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
        if 'resource.page_views.page_views_total' in results_df.columns:
            a['Popularity'] = results_df['resource.page_views.page_views_total']
            # set display none for popularity
            a['Popularity'] = '<span style="display:none">' + a['Popularity'].astype(str) + '</span>'
        
        #Custom SmartCity Data API Creation
        print("Calling API")
        if scdapi:
            return api_builder(a)

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
        print("results_df['title'] is", results_df['title'])
        # if results_df['url'] is null, then the url is located at the key "url" inside the dictionary named "resources"
        print("URL BEFORE")
        #print(results_df['resources']['0-100'])
        pdframe = []
        for i in (results_df['resources']):
            pdframe.append(i[0]['url'])
        #Convert array to pandas dataframe
        results_df['url'] = pdframe
        
        if results_df['url'].isnull().values.any():
            results_df['url'] = results_df['resources'].apply(lambda x: x[0]['url'])

        #AWS FIX
        #while results_df['url'].str.contains "/dataset/185ac735-10d9-4ea8-9e87-a7c48a750ada/resource/8082433c-b5d9-4037-b5ed-8cf8ac79be04"
        #where the ids can be any string of characters, the only consistent part is the /dataset/ and /resource/
        while results_df['url'].str.contains("/download/").any():
            #find the first line that contains /dataset/
            index = results_df['url'][results_df['url'].str.contains("/download/")].index[0]
            print("Found AWS URL on line", index)
            #url will have layers={} at the end, we want the {} to be stored
            print("URL IS", results_df['url'][index])
            #Remoe anything after the first slash after /resource/ not including /resource/
            #https://data.birminghamal.gov/dataset/0416b4d2-8c6c-4c72-8b06-1212c38d6217/resource/0f471f6a-fd5c-4da3-8d2f-bff2fb64ae9d/download/birminghamaleconomic.csv
            #should become
            #https://data.birminghamal.gov/dataset/0416b4d2-8c6c-4c72-8b06-1212c38d6217/resource/0f471f6a-fd5c-4da3-8d2f-bff2fb64ae9d
            aws_url = results_df['url'][index][:results_df['url'][index].find("/download/")]
            print("AWS URL IS", aws_url)
            results_df['url'][index] = aws_url

        
        #ARCGIS CROSSREFERENCE FIX
        while results_df['url'].str.contains("maps.arcgis.com").any():
            #find the first line that contains arcgis.com
            index = results_df['url'][results_df['url'].str.contains("maps.arcgis.com")].index[0]
            print("Found ARCGIS URL on line", index)
            #url will have layers={} at the end, we want the {} to be stored
            print("URL IS", results_df['url'][index])
            id = results_df['url'][index][results_df['url'][index].find("=")+1:]
            while "&" in id:
                id = id[:id.find("&")]
            print("ID IS", id)
            results_df['url'][index] = "ARCGIS" + id

        while results_df['url'].str.contains("hub.arcgis.com").any():
            #find the first line that contains arcgis.com
            index = results_df['url'][results_df['url'].str.contains("hub.arcgis.com")].index[0]
            print("Found ARCGIS URL on line", index)
            #fix the URL to api feed
            #get rid of everything after the .com
            arcgis_url = results_df['url'][index][:results_df['url'][index].find(".com")+4]
            arcgis_url = arcgis_url + "/api/feed/dcat-ap/2.0.1.json"
            print("ARC GIS URL IS", arcgis_url)
            #fetch the json
            arcgis_json = requests.get(arcgis_url).json()

            print(arcgis_json['dcat:dataset'][0]['dct:identifier'].split("id=")[1])

            arcgis_dict = {}
            for i in arcgis_json['dcat:dataset']:
                arcgis_id = i['dct:identifier'].split("id=")[1]
                while "&" in arcgis_id:
                    arcgis_id = arcgis_id.split("&")[0]
                #append {i['@id']: arcgis_id} to arcgis_dict
                arcgis_dict[i['@id']] = arcgis_id
            print(arcgis_dict)

            #Replace all urls with the arcgis_dict value if the key matches
            for i in results_df['url']:
                if i in arcgis_dict:
                    print("FOUND MATCH")
                    print(arcgis_dict[i])
                    #get index of i
                    index = results_df['url'][results_df['url'] == i].index[0]
                    results_df['url'][index] = "ARCGIS" + arcgis_dict[i]
                    print("URL AFTER", results_df['url'][index])
        

     #   Final displayed data frame Name & More Infor
        a['Name'] = results_df['title']
        a['Name'] = '<a href="javascript:;" onclick="ckan_preview(\'' + results_df['url'] + '\')">' + results_df['title'] + '</a>'
        #'<a href="javascript:;" onclick="arcgis_preview(\'' + id + '\')">' + results_df['dct:title'] + '</a>'


        print("URLS")
        print(results_df['url'])


        
        
        
        
        
        
        
        
        
        
        #a['More Info'] = results_df['url']
        #a['Index'] = results_df['Index']
        #print(a.to_string())
        # Drop the cell doesn't contain https
        # httpString = "http"
        # a = a[a['More Info'].str.contains(httpString) == True]
        # a = a.dropna()
        print("CKAN")
        print(a.to_string())
        #if results_df['notes'] is null, set it to ''
        if results_df['notes'].isnull().any():
            results_df['notes'] = ''
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
                
                if not scdapi: # API -> Full Description # Web -> Shortened Description
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

        #Custom SmartCity Data API Creation
        print("Calling API")
        if scdapi:
            return api_builder(a)

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
        #get the id= afarom the results_df['dct:identifier']
        id = results_df['dct:identifier'].str.split('id=', expand=True)[1].str.split('&', expand=True)[0]
        print("ID:")
        print(id)
        a['Name'] = '<a href="javascript:;" onclick="arcgis_preview(\'' + id + '\')">' + results_df['dct:title'] + '</a>'
        #a['Name'] = '<a href="' + results_df['dct:identifier'] + '">' + results_df['dct:title'] + '</a>'
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
                
                if not scdapi: # API -> Full Description # Web -> Shortened Description
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

            print("AAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBB")
            print(results_df['dct:description'][index])
            if results_df['dct:description'][index] is None or results_df['dct:description'][index] == '' or "description" in results_df['dct:description'][index]:
                results_df['dct:description'][index] = 'No description was provided.'

        a['Name'] += '<br>' + results_df['dct:description']


        print("request_site", request_site)
        # print("results_df columns", results_df.columns)

        if 'dct:modified' in results_df.columns:
            # print("dct:modified in results_df.columns")
            a['Last Updated'] = results_df['dct:modified']
            a['Last Updated'] = '<span style="display:none;">' + a['Last Updated'] + '</span>'

        # if 'dct:issued' in results_df.columns:
        #     print("dct:issued in results_df.columns")
        #     a['Last Updated'] = results_df['dct:issued']
        #     # set display none for last updated
        #     a['Last Updated'] = '<span style="display:none;">' + str(a['Last Updated']) + '</span>'
        #if 'dct:'
        # print("a[\'Last Updated\']", a['Last Updated'])

        if 'dct:accrualPeriodicity' in results_df.columns:
            a['Popularity'] = results_df['dct:accrualPeriodicity']
            # set display none for popularity
            a['Popularity'] = '<span style="display:none">' + a['Popularity'].astype(str) + '</span>'

        else:
            try:
                global fetch_url
                global dataSeries
                global temp
                # fetch("https://www.arcgis.com/sharing/rest/content/items/" + arcgis_id + "?f=json")
                # //https://www.arcgis.com/sharing/rest/content/items/fb38ba78520f40a0bd1c2b78e1e636dd?f=json
                # //read the json response
                # //add CORS header to the response
                # .then(response => {
                #     console.log("The data is being fetched!")
                #     return response.json()
                # }).then(data => {
                #     console.log("The data has been fetched!")
                #     console.log(data)
                #     console.log(data.type)
                # Above is the javascript code for the fetch request, below is the python code
                #"dct:identifier": "https://www.arcgis.com/home/item.html?id=575bd48fb01c44899334301c8e6da015&sublayer=0"
                #"dct:identifier": "https://www.arcgis.com/home/item.html?id=d8396beb7f4f48a0a3911c9545fb5c70
                #Above are two different dct:identifier for the arcgis item
                arcgis_id = results_df['dct:identifier'].str.split('id=', expand=True)[1]
                if '&' in arcgis_id[1]:
                    arcgis_id = arcgis_id.str.split('&', expand=True)[0]
                fetch_url = "https://www.arcgis.com/sharing/rest/content/items/" + arcgis_id + "?f=json"
                print("fetch_url", fetch_url)
                #Save fetch_url to a file
                # with open("fetch_url.txt", "w") as f:
                #    f.write(fetch_url.to_csv(index=False, header=False))
                
                #Retrieve the json response
                #tell requests that the data is a Series
                #We need to do this because fetch_url is a Series
                #for item in fetch_url Series
                # dataSeries1 = pd.Series()
                #This puts a ~25 second delay on site
                #Set time = 0
                #use timer to calculate how long it will take to fetch all the data
                #start timer
                # start = time.perf_counter()
                # for i in fetch_url:
                #     response = requests.get(i)
                #     data3 = response.json()['numViews']
                #     print(type(data3))
                #     print("Heck yeah")
                #     print("data", data3)
                #     #append data3 to a new series
                #     dataSeries1 = dataSeries1.append(pd.Series(data3), ignore_index=True)
                # end = time.perf_counter()
                # #end timer
                # timeTime = end - start
                # print("Time with REQUESTS", timeTime)
                #With Scrapy
                
                settings = {}
                settings['ITEM_PIPELINES'] = {'__main__.ArcGisPopularity': 1}
                settings['LOG_DISABLED'] = True
                runner = CrawlerRunner(settings=settings)
                deferred = runner.crawl(ArcGisPopularity)
                deferred.addBoth(lambda _: reactor.stop())

                try:
                    reactor.run()
                except Exception as e:
                    #print(e)
                    import sys
                    del sys.modules['twisted.internet.reactor']
                    #from twisted.internet import reactor
                    from twisted.internet import default
                    default.install()

                # print("DataSeries")
                # print(dataSeries)

                # print("ID")
                # print(id)
                # print the maximum number of views in temp
                print("Max views", max(temp, key=lambda item:item[1]))

                for i in id:
                    tempindex = [index for index, (id_str,views) in enumerate(temp) if id_str == i]
                    #print("tempindex", tempindex)
                    if tempindex:
                        view1 = temp[tempindex[0]][1]
                        views = int(view1)
                        dataSeries = dataSeries.append(pd.Series(views), ignore_index=True) 

                #There is a missing id. Find the missing id that exists in dataSeries id but not in temp id
                for i in id:
                    #id is a dataframe with one column of all the ids
                    #temp is a list of tuples with the id and the number of views
                    #Find the id that exists in id but not in temp
                    tempindex = [index for index, (id_str,views) in enumerate(temp) if id_str == i]
                    if not tempindex:
                        print("Missing id", i)



                print("DataSeries")
                print(dataSeries)

                # print("DataSeries1")
                # print(dataSeries1)

                a['Popularity'] = dataSeries
                #a['Popularity'] = dataSeries1
                # set display none for popularity
                a['Popularity'] = '<span style="display:none">' + a['Popularity'].astype(str) + '</span>'

            except Exception as e:
                print("Specific error: ", e)
                print("Error in fetching the json response")

            #a['Popularity'] = 'Not Available'
            # set display none for popularity
            #a['Popularity'] = '<span style="display:none">' + a['Popularity'].astype(str) + '</span>'

        #Custom SmartCity Data API Creation
        print("Calling API")
        if scdapi:
            # print("Calling arcgis api builder with a" + str(a['Last Updated']))
            return api_builder(a)

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
                    
                    if not scdapi: # API -> Full Description # Web -> Shortened Description
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


        #Custom SmartCity Data API Creation
        print("Calling API")
        if scdapi:
            return api_builder(a)
    
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

#Custom API builder for SmartCityData
def api_builder(a):
    global smartcitydata_api
    print(a)
    print("API Builder has been reached")
    #a['Name'], a['Last Updated'], a['Popularity']
    #URL is everything between (\' and \')
    url = a['Name'].str.extract(r'(?<=\')(.*?)(?=\')', expand=False)
    #print(url)
    #Title is everything between > and </a>
    title = a['Name'].str.extract(r'(?<=>)(.*?)(?=</a>)', expand=False)
    #print(title)
    #Description is everything after the first <br>
    desc = a['Name'].str.extract(r'(?<=<br>)(.*?)(?=$)', expand=False)
    #take out any remaining <br> tags
    desc = desc.str.replace(r'<br>', ' ', regex=True)
    #print(desc)
    #Last Updated is everything between > and </span>
    print(a['Last Updated'])
    updated = a['Last Updated'].str.extract(r'(?<=>)(.*?)(?=</span>)', expand=False)
    print("UPDATED is:")
    print(updated)
    #print(updated)
    #Popularity is everything between > and </span>
    popularity = a['Popularity'].str.extract(r'(?<=>)(.*?)(?=</span>)', expand=False)
    #print(popularity)
    #Create a new json file with the data
    #The json file will have the following format:
    #{"data":[{"title":"title","url":"url","description":"description","last_updated":"last_updated","popularity":"popularity"}]}
    #for each item in the dataframe

    newjson = {"data":[]}
    for i in range(len(a)):
        newjson["data"].append({"title":title[i], "url":url[i], "description":desc[i], "last_updated":updated[i], "views":popularity[i]})
    newcsv = pd.DataFrame(newjson["data"])

    #Now I have both JSON and CSV
    #smartcitydata_api = newjson
    #print("SmartCityData API:")
    #print(smartcitydata_api)

    #HTML Prettify
    newhtml = newcsv.to_html()

    #JSON Prettify
    newjson = json.dumps(newjson, indent=4)
    #print(newjson)
    newjson.replace('\n', '<br>')
    
    #CSV Prettify
    newcsv = newcsv.to_csv()
    # Since CSV is string format, we have to remove index column manually
    for line in newcsv.splitlines():
        prevline = line
        line = line[line.find(',')+1:]
        newcsv = newcsv.replace(prevline, line)
    #print(newcsv)


    return newjson, newcsv, newhtml



def downloaddata(a):
    print('test')
    # print(request.data)
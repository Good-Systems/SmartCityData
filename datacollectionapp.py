
#API Key ID
#9yz7a9cjftdr9qbvdlhz4ii9l

#API Key Secret
#e48r6otlbnf9bt6qd6ymci5hudrbwbk582ulbccarit04orlr



from telnetlib import AUTHENTICATION
from sodapy import Socrata
from sys import exit
import pandas as pd
import numpy as np
from sqlalchemy import null
import urllib3
import json


def search(a,b,c):
    
    print("Input fields or NA")
    print("If searching a state government type state name in city and state feilds")
    city = a
    state = b
    topic_name = c
    
    city_api_list = pd.read_csv("city_api_list.csv", index_col = False)
        
    #if city_api_list.loc[city_api_list['City'].str.contains(city)] != None:
    if city_api_list["City"].eq(city).any() and city_api_list["State-Abbr."].eq(state).any():
        #print('True')

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




def mainprogram(a,b,c):
    
    
    stoprg = 0
    
    city_domain = str(search(a,b,c))
    if city_domain == '':
        # empty_df = pd.DataFrame(None, None)
        # return empty_df
        return None
    http = urllib3.PoolManager()

    #?domains=data.austintexas.gov'
   
    # request_site = 'https://api.us.socrata.com/api/catalog/v1'+ city_domain
    request_site = 'https://phoenixopendata.com/api/3/action/package_search?q=transport'
    # request_site = 'https://ridb.recreation.gov/api/v1/'
    request = http.request('GET',request_site)

    #response_body = urlopen(request).read()
    data = json.loads(request.data)
    # results_df = pd.json_normalize(data['results'])

    while True: 
        results_df = pd.json_normalize(data['result'], record_path=['results'])
        if results_df.size == 0:
            return results_df
        break
    print("this is dataset -----------------------------")
    print(results_df.to_string())       
    #DataFrame.from_records(str(request.data))
    print("end-------------------------------------")
    results_df['Index'] = range(1,len(results_df)+1)
    #print(results_df.head())
    results_df.set_index('Index')
    #['resource.name']
    a = pd.DataFrame(data, columns = ['Index', 'Name'], index = None)
    a['Index'] = results_df['Index']
    # a['Name'] = results_df['resource.name']
    # a['More Info'] = results_df['permalink']
    a['Name'] = results_df['title']
    a['More Info'] = results_df['url']
    #print(a[['Index','Name']].to_string(index=False))
    return a
    #results_df.to_csv('results_test.csv')
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
    #print(request.data)



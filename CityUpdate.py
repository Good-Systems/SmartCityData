import pandas as pd

f = open('CitiesUpdate.txt', "w+")
citycsv = pd.read_csv('city_api_list.csv')
# print(citycsv['City'][0])
counter = 1
for i in range(citycsv.shape[0]):
    f.write('INSERT INTO city (id, state, name)')
    f.write('\n')
    f.write('VALUES ('+ str(counter) +', \''+ citycsv['State-Abbr.'][i] + '\', \'' + citycsv['City'][i] + '\');')
    f.write('\n')
    f.write('\n')
    counter += 1
f.close

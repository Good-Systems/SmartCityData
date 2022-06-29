import pandas as pd

f = open('indexUpdate.txt', "w+")
citycsv = pd.read_csv('city_api_list.csv')
# print(citycsv['City'][0])
counter = 61
for i in range(57, 106):
    f.write('UPDATE city')
    f.write('\n')
    f.write('SET id=' + str(counter))
    f.write('\n')
    f.write('WHERE name = \'' + citycsv['City'][i-1] + '\' & state = \'' + citycsv['State-Abbr.'][i-1] + '\';')
    # f.write('VALUES ('+ str(counter) +', \''+ citycsv['State-Abbr.'][i] + '\', \'' + citycsv['City'][i] + '\');')
    f.write('\n')
    f.write('\n')
    counter += 1
f.close

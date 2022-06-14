import pandas as pd
newcities = pd.read_csv('newCities.csv')
f = open('CitiesUpdate3.txt', "w+")
for i in range(101):
    # print("REACH HERE")
    # print(i)
    for j in range(newcities['domain'].shape[0]):
        # print("reach here")
        # print(j)
        # a = newcities['city'][i]
        if str(newcities['city'][i]).lower() in str(newcities['domain'][j]).lower():
            # newcities['contain'][j] = 1
            print("REACH HERE")
            f.write(str(newcities['city'][i]) + ', ' + str(newcities['domain'][j] + '\n'))

    # if newcities['city'][i] in newcities['domain']:
    #     print(i)
    # else:
    #     print(str(i) + 'is false')
    
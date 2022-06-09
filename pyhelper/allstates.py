f = open('allstates.txt', 'w+')
f2 = open('states.txt', 'r')
full = []
abbr = []
for line in f2:
    a = line.split()
    s = a[1]
    l = len(a)
    for i in range(2,l):
        s += ' '
        s += a[i]   
    f.write('(\''+ a[0] + '\', \'' + s + '\'),')

f.close


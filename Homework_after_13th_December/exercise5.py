import numpy as np


t = np.load('sample_treated.npz')
o = t['outputs']


if_object_grows_doubles = []
print('Number of objects which grows doubles:')

for i in range(len(o)):
    if(o[i][0]*2 <= o[i][-1]):
        if_object_grows_doubles.append(True)
        print(i)
    else:
        if_object_grows_doubles.append(False)

#List if_object_grows_doubles contains which object grows doubles

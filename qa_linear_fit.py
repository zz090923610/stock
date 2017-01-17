import numpy as np
import matplotlib.pyplot as plt
from qa_udr import load_daily_data

dl=load_daily_data('002263')
c=[]
for i in dl:
    c.append(i['close'])
x=np.arange(len(c))
m,b = np.polyfit(x,c,1)
plt.ion()
plt.plot(x,c,'.')
plt.plot(x,m*x + b,'-')

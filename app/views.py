from django.shortcuts import render
from django.http import HttpResponse
from .forms import locationForm
from django.conf import settings

import pandas as pd
import random
import os

CHAR = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
name = ""
# Create your views here.
def random_name():
    name = ""
    for i in range(10):
        name += random.choice(CHAR)
    return name

def get_data(file):
    df = pd.read_csv(file) #getting the csv data as dataframe
    #now manipulating the data to get the desired output
    df['TR'] = ""
    df['+DM1'] = ""
    df['-DM1'] = ""
    df['TR14'] = ""
    df['+DM14'] = ""
    df['-DM14'] = ""
    df['+DI14'] = ""
    df['-DI14'] = ""
    df['DI 14 Diff'] = ""
    df['DI 14 Sum'] = ""
    df['DX'] = ""
    df['ADX'] = ""
    
    row_length = df.shape[0]
    print(row_length)

    #calculating all the data for the then created column
    j = 1
    adx_counter = 0
    for i in range(row_length - 1):
        df['TR'][j] = max(df['High'][j] - df['Low'][j],abs(df['High'][j] - df['Close'][j-1]),abs(df['Low'][j] - df['Close'][j-1]))
        df['+DM1'][j] = max(df['High'][j] - df['High'][j-1], 0) if (df['High'][j]-df['High'][j-1]) > (df['Low'][j-1] - df['Low'][j]) else 0
        df['-DM1'][j] = max(df['Low'][j-1] - df['Low'][j], 0) if (df['High'][j]-df['High'][j-1]) < (df['Low'][j-1] - df['Low'][j]) else 0
        
        if( j == 14 ):
            df['TR14'][j] = sum(list(df['TR'][1:15]))
            df['+DM14'][j] = sum(list(df['+DM1'][1:15]))
            df['-DM14'][j] = sum(list(df['-DM1'][1:15]))
            df['+DI14'][j] = 100 * round(df['+DM14'][j]/df['TR14'][j],4)
            df['-DI14'][j] = 100 * round(df['-DM14'][j]/df['TR14'][j],4)
            df['DI 14 Diff'][j] = abs(df['+DI14'][j] - df['-DI14'][j])
            df['DI 14 Sum'][j] = df['+DI14'][j] + df['-DI14'][j]
            df['DX'][j] = 100 * round(df['DI 14 Diff'][j]/ df['DI 14 Sum'][j],4)
        
        if(j > 14):
            df['TR14'][j] = df['TR14'][j-1] - round(df['TR14'][j-1] / 14, 4) + df['TR'][j]
            df['+DM14'][j] = df['+DM14'][j-1] - round(df['+DM14'][j-1] / 14,4) + df['+DM1'][j]
            df['-DM14'][j] = df['-DM14'][j-1] - round(df['-DM14'][j-1] / 14,4) + df['-DM1'][j]
            df['+DI14'][j] = 100 * round(df['+DM14'][j]/df['TR14'][j], 4)
            df['-DI14'][j] = 100 * round(df['-DM14'][j]/df['TR14'][j],4)
            df['DI 14 Diff'][j] = abs(df['+DI14'][j] - df['-DI14'][j])
            df['DI 14 Sum'][j] = df['+DI14'][j] + df['-DI14'][j]

            df['DX'][j] = 100 * (df['DI 14 Diff'][j] / df['DI 14 Sum'][j])
            adx_counter += 1
        
        if adx_counter == 13:
            df['ADX'][j] = (sum(df['DX'][14:j]))/14
        else:
            if adx_counter > 13:
                df['ADX'][j] = round((df['ADX'][j-1] * 13 + df['DX'][j]) / 14, 4)
        
        j += 1
        print(j)
        # if i == 14:
        #     adx_counter += 1
        #     df['TR']

    print(df)
    name = random_name()
    df.to_excel(f'media\Files\data.xlsx')

def home(request):
    if request.method == 'POST':
        form = locationForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            get_data(file)
            file_name = random_name()
            file_path = os.path.join(settings.FILES_DIR, file_name)
            print(file_path)
            
            return HttpResponse(f'<a href="media\Files\data.xlsx" download>File Download</a>')

    else:
        form = locationForm
    return render(request, 'app/file.html',{'form':form})
import pandas as pd
import numpy as np
import os
import xlsxwriter
from matplotlib import pyplot as plt



# Library for analysis JST - Jednostki Samorzadu Terytorialnego

def read_jst(path):
    file = pd.read_excel(path,skiprows=3,sheet_name=None) # w kolumnach ma byc wk, pk, gk, gt, nazwa jst i dochody
    file = list(file.values())[0]
    file = file[3:].reset_index(drop=True) # 3 pierwsze wiersze sa nan
    file['dochody'] = file['Dochody wykonane\n(wpłaty minus zwroty)']
    file = file[['WK','PK','GK','GT','Nazwa JST','województwo','powiat','dochody']]
    file['kod'] = ''
    if(file['WK'][0]!='-'):
        file["WK"] = file["WK"].apply(lambda x: str(int(x)) if len(str(int(x)))==2 else '0'+str(int(x)))
        file['kod'] = file['kod']+file['WK']
    if(file['PK'][0]!='-'):
        file["PK"] = file["PK"].apply(lambda x: str(int(x)) if len(str(int(x)))==2 else '0'+str(int(x)))
        file['kod'] = file['kod']+file['PK']
    if(file['GK'][0]!='-'):
        file["GK"] = file["GK"].apply(lambda x: str(int(x)) if len(str(int(x)))==2 else '0'+str(int(x)))
        file['kod'] = file['kod']+file['GK']
    if(file['GT'][0]!='-'):
        file["GT"] = file["GT"].apply(lambda x: str(int(x)))
        file['kod'] = file['kod']+file['GT']
    file = file[['kod','Nazwa JST','województwo','powiat','dochody']]
    file = file.reset_index(drop=True)
    file = file.groupby(by=['kod','Nazwa JST','województwo','powiat']).sum()
    file = file.reset_index()
    return file


def read_gus(gus_file):
    gus = pd.read_excel(gus_file,skiprows=5,sheet_name=None)
    m = 0
    for i in gus:
        s = gus[i]
        s = s.dropna()
        s = s.loc[(s['Identyfikator terytorialny\nCode'].apply(lambda x: int(0 if str(x).strip()=='' else str(x).strip()))>0) 
              | (s['Wyszczególnienie\nSpecification']=='   Wiek  przedprodukcyjny     ')
              | (s['Wyszczególnienie\nSpecification']=='   Wiek  produkcyjny          ')
              | (s['Wyszczególnienie\nSpecification']=='   Wiek  poprodukcyjny        '), 
              ['Wyszczególnienie\nSpecification','Identyfikator terytorialny\nCode',
               'Ogółem \nTotal','Mężczyźni Males','Kobiety \nFemales']]
        s = s.reset_index(drop=True)
        s = s.rename(columns={'Identyfikator terytorialny\nCode': 'id', 'Ogółem \nTotal': 'Ogółem', 'Mężczyźni Males': 'M',
                     'Kobiety \nFemales': 'K', 'Wyszczególnienie\nSpecification': 'info'})
        s['wojewodztwo'] = i
        if(m==0):
            m=1
            ss = s
        else:
            ss = ss.append(s, ignore_index=True)
            ss = ss.reset_index(drop=True)
    ss['info'] = ss['info'].apply(lambda x: 'Wiek przedprodukcyjny' if x=='   Wiek  przedprodukcyjny     ' else x)
    ss['info'] = ss['info'].apply(lambda x: 'Wiek produkcyjny' if x=='   Wiek  produkcyjny          ' else x)
    ss['info'] = ss['info'].apply(lambda x: 'Wiek poprodukcyjny' if x=='   Wiek  poprodukcyjny        ' else x)
    ss['Wiek przedprodukcyjny'] = ''
    ss['Wiek produkcyjny'] = ''
    ss['Wiek poprodukcyjny'] = ''
    ss['id'] = ss['id'].apply(lambda x: str(x))
    ss = ss.reset_index(drop=True)
    for i, r in ss.iterrows():
        if(str(r['id']).strip()!=''):
            id = r['id']
        else:
            ss.loc[ss['id']==id,r['info']] = r['Ogółem']
    ss = ss.loc[ss['id'].apply(lambda x: int(0 if str(x).strip()=='' else str(x).strip()))>0]
    ss = ss.reset_index(drop=True)
    for c in ['M','K','Wiek przedprodukcyjny','Wiek produkcyjny','Wiek poprodukcyjny']:
        ss[c] = ss[c].apply(lambda x: int(x))
    return ss

def check_data(m):
    dlugosc_kodu = len(m['kod'][0])
    example_city = 'Jelenia Góra'
    example_m = 'Górnośląsko-Zagłębiowska\nMetropolia' 
    if(dlugosc_kodu==7):
        w = 'gminy'
    elif(dlugosc_kodu==4 and example_city not in list(m['Nazwa JST'])):
        w = 'powiaty'
    elif(dlugosc_kodu==4 and example_city in list(m['Nazwa JST'])):
        w = 'miasta_npp'
    elif(dlugosc_kodu==2 and example_m not in list(m['Nazwa JST'])):
        w = 'wojewodztwa'
    elif(dlugosc_kodu==2 and example_m in list(m['Nazwa JST'])):
        w = 'metropolia'
    else:
        print('Dane nie sa w odpowiednim formacie.')
    return w


def merge_one_col(ret, k, kod, del_namecol, namecol, val):
    val = val.reset_index()
    val[namecol] = val[del_namecol]
    del val[del_namecol]
    ret[k] = ret[k].merge(val, how='left', left_on='kod', right_on=kod)
    del ret[k][kod]
    return ret

# Mean and variance
# Estimation income
# Przyjmuje, że udział JST w podatkach PIT wynosi:
# - 39,34 % dla gminy
# - 10,25 % dla powiatu
# - 1,60 % dla województwa
# - 39,34 % + 10,25 % = 49,59 % dla miast na prawach powiatu
def merge_results_subunits(ret, directories):
    for k in ret:
        check = check_data(ret[k])
        if(check=='wojewodztwa'):
            wojewodztwa = ret[k].copy()
            k_woj = k
        if(check=='powiaty'):
            powiaty = ret[k].copy()
            k_pow = k
        if(check=='gminy'):
            gminy = ret[k].copy()
            k_gm = k
        if(check=='miasta_npp'):
            miasta = ret[k].copy()
            k_mi = k
    gminy['kod4'] = gminy['kod'].apply(lambda x: x[:4])
    gminy['kod2'] = gminy['kod'].apply(lambda x: x[:2])
    powiaty['kod2'] = powiaty['kod'].apply(lambda x: x[:2])
    miasta['kod2'] = miasta['kod'].apply(lambda x: x[:2])
    for j in directories: # Mean and variance
        ret = merge_one_col(ret, k_pow, 'kod4', 'dochody '+j, 'Średni dochód gmin '+j,
                            gminy[['kod4', 'dochody '+j]].groupby('kod4').mean('dochody '+j))
        ret = merge_one_col(ret, k_pow, 'kod4', 'dochody '+j, 'Wariancja dochodu gmin '+j, 
                            gminy[['kod4', 'dochody '+j]].groupby('kod4').agg("var"))
        
        ret = merge_one_col(ret, k_woj, 'kod2', 'dochody '+j, 'Średni dochód gmin '+j, 
                            gminy[['kod2', 'dochody '+j]].groupby('kod2').mean('dochody '+j))
        ret = merge_one_col(ret, k_woj, 'kod2', 'dochody '+j, 'Wariancja dochodu gmin '+j, 
                            gminy[['kod2', 'dochody '+j]].groupby('kod2').agg("var"))
        
        ret = merge_one_col(ret, k_woj, 'kod2', 'dochody '+j, 'Średni dochód powiatów '+j, 
                            powiaty[['kod2', 'dochody '+j]].groupby('kod2').mean('dochody '+j))
        ret = merge_one_col(ret, k_woj, 'kod2', 'dochody '+j, 'Wariancja dochodu powiatów '+j, 
                            powiaty[['kod2', 'dochody '+j]].groupby('kod2').agg("var"))
    for j in directories: # Estimation income
        ret = merge_one_col(ret, k_pow, 'kod4', 'dochody '+j, 'Estymacja dochodu '+j+' na podstawie gmin',
                            gminy[['kod4', 'dochody '+j]].groupby('kod4').sum('dochody '+j))
        ret[k_pow]['Estymacja dochodu '+j+' na podstawie gmin'] = ret[k_pow]['Estymacja dochodu '+j+' na podstawie gmin'].apply(lambda x: x*(0.1025/0.3934))
        
        
        
        ret = merge_one_col(ret, k_woj, 'kod2', 'dochody '+j, 'Estymacja dochodu '+j+' na podstawie miast', 
                            miasta[['kod2', 'dochody '+j]].groupby('kod2').sum('dochody '+j))
        ret[k_woj]['Estymacja dochodu '+j+' na podstawie miast'] = ret[k_woj]['Estymacja dochodu '+j+' na podstawie miast'].apply(lambda x: x*(0.0160/0.4959))
        
        
        
        ret = merge_one_col(ret, k_woj, 'kod2', 'dochody '+j, 'Estymacja dochodu '+j+' na podstawie gmin', 
                            gminy[['kod2', 'dochody '+j]].groupby('kod2').sum('dochody '+j))
        ret[k_woj]['Estymacja dochodu '+j+' na podstawie gmin'] = ret[k_woj]['Estymacja dochodu '+j+' na podstawie gmin'].apply(lambda x: x*(0.0160/0.3934))
        ret[k_woj]['Estymacja dochodu '+j+' na podstawie gmin'] = ret[k_woj]['Estymacja dochodu '+j+' na podstawie gmin']+ret[k_woj]['Estymacja dochodu '+j+' na podstawie miast']
        
        ret = merge_one_col(ret, k_woj, 'kod2', 'dochody '+j, 'Estymacja dochodu '+j+' na podstawie powiatów', 
                            powiaty[['kod2', 'dochody '+j]].groupby('kod2').sum('dochody '+j))
        ret[k_woj]['Estymacja dochodu '+j+' na podstawie powiatów'] = ret[k_woj]['Estymacja dochodu '+j+' na podstawie powiatów'].apply(lambda x: x*(0.0160/0.1025))
        ret[k_woj]['Estymacja dochodu '+j+' na podstawie powiatów'] = ret[k_woj]['Estymacja dochodu '+j+' na podstawie powiatów']+ret[k_woj]['Estymacja dochodu '+j+' na podstawie miast']
        
        del ret[k_woj]['Estymacja dochodu '+j+' na podstawie miast']
    return ret


def merge_gus(m, gus):
    gus2 = gus.copy()
    del gus2['info']
    del gus2['wojewodztwo']
    check = check_data(m)
    if(check=='gminy'):
        m = m.merge(gus2, how='left', left_on='kod', right_on='id')
        del m['id']
    elif(check=='metropolia'):
        return m
    elif(check=='miasta_npp'): 
        gus2['id3'] = gus2['id'].apply(lambda x: x[-3:])
        gus2 = gus2.loc[gus2['id3']=='011']
        gus2 = gus2.reset_index(drop=True)
        del gus2['id3']
        gus2['id'] = gus2['id'].apply(lambda x: x[:4])
        gus2 = gus2.groupby('id').sum()
        gus2 = gus2.reset_index()
        m = m.merge(gus2, how='left', left_on='kod', right_on='id')
        del m['id']
    elif(check=='powiaty'): 
        gus2['id'] = gus2['id'].apply(lambda x: x[:4])
        gus2 = gus2.groupby('id').sum()
        gus2 = gus2.reset_index()
        m = m.merge(gus2, how='left', left_on='kod', right_on='id')
        del m['id']
    elif(check=='wojewodztwa'): 
        gus2['id'] = gus2['id'].apply(lambda x: x[:2])
        gus2 = gus2.groupby('id').sum()
        gus2 = gus2.reset_index()
        m = m.merge(gus2, how='left', left_on='kod', right_on='id')
        del m['id']
    else:
        print('Dane nie sa w odpowiednim formacie.')
    return m

# Zakładam arbitralnie, że 70% osób w wieku produkcyjnym i poprodukcyjnym płaci podatki.
# Dodatkowo przyjmuje, że podatek PIT dla wszystkich wynosi 17%, a kwota wolna to 8 000 PLN.
# Przyjmuje, że udział JST w podatkach PIT wynosi:
# - 39,34 % dla gminy
# - 10,25 % dla powiatu
# - 1,60 % dla województwa
# - 39,34 % + 10,25 % = 49,59 % dla miast na prawach powiatu
def income_per_capita(m, year):
    check = check_data(m)
    if(check=='metropolia'):
        return m
    m['Liczba osob placaca podatki'] = m['Wiek produkcyjny']+m['Wiek poprodukcyjny']
    m['Liczba osob placaca podatki'] = m['Liczba osob placaca podatki'].apply(lambda x: int(x*0.7) if np.isnan(x)==False else x)
    if(check=='gminy'):
        m['caly_pit'] = m['dochody '+year].apply(lambda x: x/0.3934 if np.isnan(x)==False else x)
    if(check=='powiaty'):
        m['caly_pit'] = m['dochody '+year].apply(lambda x: x/0.1025 if np.isnan(x)==False else x)
    if(check=='wojewodztwa'):
        m['caly_pit'] = m['dochody '+year].apply(lambda x: x/0.0160 if np.isnan(x)==False else x)
    if(check=='miasta_npp'):
        m['caly_pit'] = m['dochody '+year].apply(lambda x: x/0.4959 if np.isnan(x)==False else x)
    m['caly_pit'] = m['caly_pit'].apply(lambda x: x/0.17 if np.isnan(x)==False else x)
    m['Średni dochód mieszkańca miesięcznie w '+year] = ((m['caly_pit']/m['Liczba osob placaca podatki'])+8000)/12
    del m['Liczba osob placaca podatki']
    del m['caly_pit']
    return m



def create_excel(ret, out_file):
    writer = pd.ExcelWriter(out_file, engine='xlsxwriter')
    for k in ret:
        ret[k].to_excel(writer, k,index=False)
        wb = writer.book
        ws = writer.sheets[k]
        ws.set_column(1,3,28)
        ws.set_column(4,7,16)
        ws.set_column(11,13,20)
        ws.set_column(14,27,25)
    writer.save()
    writer.close()
    return 'Done'


def create_report(paths, names, directories, gus_file, out_file=False):
    ret = {}
    
    gus=read_gus(gus_file)

    for l in range(len(paths[directories[0]])):
        j=0
        for d in directories:
            if(j==0):
                m = read_jst(paths[d][l])
                m['dochody '+d] = m['dochody']
                del m['dochody']
                j=1
            else:
                m = m.merge(read_jst(paths[d][l]),how='outer',on=['kod','Nazwa JST','województwo','powiat'])
                m['dochody '+d] = m['dochody']
                del m['dochody']
        
        m['zmiana'] = m['dochody '+directories[1]]-m['dochody '+directories[0]]
        m['zmiana %'] = 100*(m['dochody '+directories[1]]-m['dochody '+directories[0]])/m['dochody '+directories[0]]
        m = m.sort_values(by='zmiana %')
        
        m = merge_gus(m, gus)
        for d in directories:
            m = income_per_capita(m, d)
        
        ret[names[l]] = m
        
    ret = merge_results_subunits(ret, directories)
        
    if(out_file!=False):
        create_excel(ret, out_file)

    return ret

# Create image
    
def pretty_ylim(left_bar, right_bar):
    max_value=list(left_bar)
    for y in list(right_bar):
        max_value.append(y)
    max_value = int(max(max_value))
    
    zeros = len(str(max_value))-1
    mv = round(max_value, -1*zeros)
    if(mv<max_value):
        add = '1'
        for a in range(zeros):
            add = add+'0'
        mv = mv + int(add)
    return mv

def create_image(title, ylabel, nazwy, left_bar, right_bar, labels, c=['green','red'], alpha=[0.65,0.65]):
    nazwy = list(nazwy)
    
    mv = pretty_ylim(left_bar, right_bar)
    
    if(mv>1000000):
        mv = mv/1000000
        left_bar = list(left_bar/1000000)
        right_bar = list(right_bar/1000000)
        v=' [mln]'
    elif(mv>1000):
        mv = mv/1000
        left_bar = list(left_bar/1000)
        right_bar = list(right_bar/1000)
        v=' [tys]'
    else:
        left_bar = list(left_bar)
        right_bar = list(right_bar)
        v=''
    fig = plt.figure(figsize=(14,7))
    plt.title(title, fontsize=20)
    plt.xticks(range(len(nazwy)), nazwy, fontsize=20, rotation=90)
    plt.ylim(0, mv) #
    plt.yticks(fontsize=20)
    plt.ylabel(ylabel+v, fontsize=20)

    barcoll = plt.bar(range(len(nazwy)),left_bar, label=labels[0],color=c[0],alpha=alpha[0],
                      edgecolor='black',width=-0.35,align='edge')
    barcoll = plt.bar(range(len(nazwy)),right_bar,label=labels[1],color=c[1],alpha=alpha[1],
                      edgecolor='black',width=0.35, align='edge')

    plt.legend(fontsize=20)
    plt.show()
    plt.close()
    return None
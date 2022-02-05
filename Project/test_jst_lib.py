from jst_lib import *
import pytest
from _pytest.monkeypatch import MonkeyPatch
import pandas as pd



@pytest.mark.parametrize("wk,pk,gk,gt,n,w,p,d,k2,n2,w2,p2,d2", [
([0,0,0,'01','07'], [0,0,0,'01','09'], [0,0,0,'01','08'], [0,0,0,'1','2'], 
 [0,0,0,'Nazwa','Nazwa2'], [0,0,0,'Nazwa','Nazwa3'], [0,0,0,'Nazwa','Nazwa4'], [0,0,0,8,700],
 ['0101011', '0709082'], ['Nazwa','Nazwa2'], ['Nazwa','Nazwa3'], ['Nazwa','Nazwa4'], [8,700]),
 
([0,0,0,'11','11'], [0,0,0,'01','01'], [0,0,0,'08','08'], [0,0,0,'1','1'], 
 [0,0,0,'Nazwa2','Nazwa2'], [0,0,0,'Nazwa3','Nazwa3'], [0,0,0,'Nazwa4','Nazwa4'], [0,0,0,8,700],
 ['1101081'], ['Nazwa2'], ['Nazwa3'], ['Nazwa4'], [708]) 
])
def test_read_jst(wk,pk,gk,gt,n,w,p,d,k2,n2,w2,p2,d2):
    monkeypatch = MonkeyPatch()
    def mock_readexcel(*args, **kwargs):
        df = pd.DataFrame({'WK': wk,'PK': pk,'GK': gk,'GT': gt,
        'Nazwa JST': n,'województwo': w,'powiat': p,
        "Dochody wykonane\n(wpłaty minus zwroty)": d})
        return {'Arkusz1': df}
    monkeypatch.setattr(pd, "read_excel", mock_readexcel)
    
    f = read_jst('path')
    
    r = pd.DataFrame({'kod': k2,'Nazwa JST': n2,'województwo': w2,
                      'powiat': p2,'dochody':d2})
    
    assert list(f['kod'])==list(r['kod'])
    assert list(f['Nazwa JST'])==list(r['Nazwa JST'])
    assert list(f['województwo'])==list(r['województwo'])
    assert list(f['powiat'])==list(r['powiat'])
    assert list(f['dochody'])==list(r['dochody'])


    
@pytest.mark.parametrize("w, i, o, m, k, i2, o2, m2, k2, wprzed2, w2, wpo2", [
([0,0,'Jelenia Góra','0-4', '   Wiek  przedprodukcyjny     ', '   Wiek  produkcyjny          ','   Wiek  poprodukcyjny        '], 
 [0,0,'0261011','','','',''], [0,0,78335,2957,1001,1002,1003], [0,0,36363,1000,'','',''], [0,0,41972,1957,'','',''],
 ['0261011'], [78335], [36363], [41972], [1001], [1002], [1003]),
 
([0,0,'Jelenia Góra', '   Wiek  przedprodukcyjny     ', '   Wiek  produkcyjny          ','   Wiek  poprodukcyjny        '], 
 [0,0,'0261011','','',''], [0,0,78335,1001,1002,1003], [0,0,36363,'','',''], [0,0,41972,'','',''],
 ['0261011'], [78335], [36363], [41972], [1001], [1002], [1003]),
])
def test_read_gus(w, i, o, m, k, i2, o2, m2, k2, wprzed2, w2, wpo2):
    monkeypatch = MonkeyPatch()
    def mock_readexcel(*args, **kwargs):
        df = pd.DataFrame({'Wyszczególnienie\nSpecification': w,'Identyfikator terytorialny\nCode': i,
        'Ogółem \nTotal': o,'Mężczyźni Males': m, 'Kobiety \nFemales': k})
        return {'Mazowieckie': df}
    monkeypatch.setattr(pd, "read_excel", mock_readexcel)
    
    f = read_gus('path')
    
    r = pd.DataFrame({'id': i2, 'Ogółem': o2,'M': m2,'K': k2,
                      'Wiek przedprodukcyjny': wprzed2,'Wiek produkcyjny': w2,'Wiek poprodukcyjny': wpo2})
    
    assert list(f['id'])==list(r['id'])
    assert list(f['Ogółem'])==list(r['Ogółem'])
    assert list(f['M'])==list(r['M'])
    assert list(f['K'])==list(r['K'])
    assert list(f['Wiek przedprodukcyjny'])==list(r['Wiek przedprodukcyjny'])
    assert list(f['Wiek produkcyjny'])==list(r['Wiek produkcyjny'])
    assert list(f['Wiek poprodukcyjny'])==list(r['Wiek poprodukcyjny'])



@pytest.mark.parametrize("k,n,r", [
(['10','11','12'], ['Mazowieckie','Pomorskie','Lubuskie'], 'wojewodztwa'),
(['21'], ['Mazowieckie'], 'wojewodztwa'),
(['10','11'], ['Pomorskie','Lubuskie'], 'wojewodztwa'),
(['41','11','12','15'], ['Mazowieckie','Pomorskie','Lubuskie','tttt'], 'wojewodztwa'),
(['10','11','16'], ['a','b','c'], 'wojewodztwa'),
(['1011111','1110101','1100002'], ['gm1','gm2','gm3'], 'gminy'),
(['4011111'], ['gm1'], 'gminy'),
(['6711111','1110101','1100002','1100001'], ['gm1','gm2','gm3',''], 'gminy'),
(['1234567','7654321'], ['gm1','gm2'], 'gminy'),
(['1010','1111','1212'], ['powiat1','powiat2','powiat3'], 'powiaty'),
(['4321','1234'], ['powiat1','powiat2'], 'powiaty'),
(['1010','1111','1212'], ['Warszawa','Szczecin','Jelenia Góra'], 'miasta_npp'),
(['10','11','12'], ['m1','Górnośląsko-Zagłębiowska\nMetropolia','m2'], 'metropolia')
])
def test_check_data(k,n,r):
    m = pd.DataFrame({'kod': k, 'Nazwa JST': n})
    assert check_data(m)==r



@pytest.mark.parametrize("g,i,del_namecol, namecol, kody1, kody2, wartosci1, wartosci2", [
('gminy', 'id', 'dochody 2020', 'Średnia', ['1010'], ['1010'], [100], [100]),
('powiaty', 'kod2', 'dochod 2019', 'Średnia', ['1010','1111'], ['1111', '1010'], [100, 110], [110, 100]),
('woj', 'kod4', 'dochody 2020', 'Var', ['1010','1111'], ['1010','1111'], [100, 110], [100, 110]),
('gminy', 'id', 'dochody 2020', 'Średnia', ['1010','1111'], ['1111', '1010', '1000'], [100, 110], [110, 100, 200])
])
def test_merge_one_col(g,i, del_namecol, namecol, kody1, kody2, wartosci1, wartosci2):
    df = pd.DataFrame({'kod': kody1})
    df2 = pd.DataFrame({del_namecol: wartosci2, i: kody2})
    f = merge_one_col({g: df}, g, i, del_namecol, namecol, df2)
    f = f[g]
    
    r = pd.DataFrame({'kod': kody1, namecol: wartosci1})
    assert list(f['kod'])==list(r['kod'])
    assert list(f[namecol])==list(r[namecol])



@pytest.mark.parametrize("k1,k2,k3,k4,d1,d2,d3,d4,r1,r2", [
(['1111111','1111222','1111223','2222222', '1122222'], ['1111','2222'], ['1010', '1234'], ['10','11','12','22'],
 [5,8,5,8,0], [100,101], [12,13], [4,3,2,1],
 [0, (5+8+5+0)/4, 0, 8.0],[0, 11, 0, 0]  
)])
def test_merge_results_subunits(k1,k2,k3,k4,d1,d2,d3,d4,r1,r2):
    dfg = pd.DataFrame({'Nazwa JST': ['','','','',''], 'kod': k1, 'dochody 2019': [1,2,3,4,9], 'dochody 2020': d1})
    dfp = pd.DataFrame({'Nazwa JST': ['',''], 'kod': k2, 'dochody 2019': [99,98], 'dochody 2020': d2})
    dfm = pd.DataFrame({'Nazwa JST': ['Jelenia Góra',''], 'kod': k3, 'dochody 2019': [10,11], 'dochody 2020': d3})
    dfw = pd.DataFrame({'Nazwa JST': ['','','',''], 'kod': k4, 'dochody 2019': [1,2,3,4], 'dochody 2020': d4})
    f = merge_results_subunits({'p': dfp, 'g': dfg, 'w': dfw, 'm': dfm}, ['2019','2020'])
    
    assert list(f['w']['Średni dochód gmin 2020'].fillna(0)) == r1
    assert list(f['w']['Wariancja dochodu gmin 2020'].fillna(0)) == r2



@pytest.mark.parametrize("k1,n1,w1,p1,d1,i2, o2, m2, k2, wprzed2, w2, wpo2,ii2, ww2, r1, r2, r3", [
(['0101011', '0709082'], ['Nazwa','Nazwa2'], ['Nazwa','Nazwa3'], ['Nazwa','Nazwa4'], [8,700],
 ['0101011'], [78335], [36363], [41972], [1001], [1002], [1003], [''], [''],
 [78335,0], [41972,0], [36363,0]
),
(['0101', '0709'], ['Nazwa','Nazwa2'], ['Nazwa','Nazwa3'], ['Nazwa','Nazwa4'], [8,700],
 ['0101011','0101111','0709'], [78335,100,200], [36363,1,1], [41972,1,1], [1001,1,1], [1002,1,1], [1003,1,1], ['','',''], ['','',''],
 [78435,200], [41973,1], [36364,1]
)
])
def test_merge_gus(k1,n1,w1,p1,d1,i2, o2, m2, k2, wprzed2, w2, wpo2,ii2, ww2, r1, r2, r3):
    m = pd.DataFrame({'kod': k1,'Nazwa JST': n1,'województwo': w1,
                      'powiat': p1,'dochody':d1})
    gus = pd.DataFrame({'id': i2, 'Ogółem': o2,'M': m2,'K': k2,
                      'Wiek przedprodukcyjny': wprzed2,'Wiek produkcyjny': w2,'Wiek poprodukcyjny': wpo2, 'info': ii2, 'wojewodztwo': ww2})
    f = merge_gus(m, gus)
    
    assert list(f['Ogółem'].fillna(0)) == r1
    assert list(f['K'].fillna(0)) == r2
    assert list(f['M'].fillna(0)) == r3



@pytest.mark.parametrize("k1,n1,w1,p1,d1,r1,r2", [
(['01', '07'], ["Górnośląsko-Zagłębiowska\nMetropolia",'Nazwa2'], [100,110], [300,400], [8,700], 
 ['kod','Nazwa JST','Wiek produkcyjny','Wiek poprodukcyjny','dochody 2020'], ''
),
(['0101111', '0709847'], ["Nazwa1",'Nazwa2'], [800,400], [200,600], [66878,66878], 
 ['kod','Nazwa JST','Wiek produkcyjny','Wiek poprodukcyjny','dochody 2020','Średni dochód mieszkańca miesięcznie w 2020'],
 [int(((1000000/700)+8000)/12),int(((1000000/700)+8000)/12)]
)
])
def test_income_per_capita(k1,n1,w1,p1,d1,r1,r2):
    m = pd.DataFrame({'kod': k1,'Nazwa JST': n1,'Wiek produkcyjny': w1,
                      'Wiek poprodukcyjny': p1,'dochody 2020':d1})
    f = income_per_capita(m, '2020')
    assert list(f.columns) == r1
    if('Średni dochód mieszkańca miesięcznie w 2020' in list(f.columns)):
        assert list(f['Średni dochód mieszkańca miesięcznie w 2020'].apply(lambda x: int(x))) == r2



@pytest.mark.parametrize("list1,list2,r", [
([10,11,12], [10,11,12], 20), 
([10,11,121], [10,11,12], 200),
([10,11,19], [10,11,12], 20),
([10,11,9999], [10,11,12], 10000),
([10,11,12], [10,344,12], 400),
([10,11,12], [100,11,12], 100), 
([10,11,12], [101,11,12], 200), 
([10,11,12], [199,11,12], 200)
])
def test_pretty_ylim(list1,list2,r):
    assert pretty_ylim(list1, list2)==r
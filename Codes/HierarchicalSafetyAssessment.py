import numpy as np
import os
import pandas as pd
from functools import cmp_to_key

Compare_count = 0
df_compare_record = pd.DataFrame(columns=['A', 'B', 'Compare_result', 'K', 'Ms', 'j', 'Dis']) 
# K; distinguished in which layer; 
# Ms: distinguished in which mode; 
# j: distingguished in which bit of the mode
# dis: |SV1[j] - SV2[j]|

from ConfigurationRankingbyHSA import ComparebyImportanceClass, s_to_impl, calc_sv, sv_add_s, comp_sv


# This function(Comp2ADSbySeverity) compare 2 ADS by their testing results' severity:
# input: ADS1 and ADS2's severity(sv1 and sv2) and their configuration(string, name1 and name2)
# output: result = -1 means ADS2 is safer,1 means the otherwise, 0 means ADS1 and ADS2 are tied

def Comp2ADSbySeverity(sv1,sv2, name1,name2):
    global df_compare_record
    global Compare_count
    Compare_count += 1

    impl_sv1 = {}
    impl_sv2 = {}
    N_req = 10
    Pattern = {0:(7,), 1:(2,), 2:(3,8), 3:(4,5,6)}
    
    for s in sv1:
        impl = s_to_impl(s,Pattern,N_req)
        if impl_sv1.get(impl) == None:
            impl_sv1[impl] = calc_sv(s,Pattern)
        else:
            impl_sv1[impl] = sv_add_s(impl_sv1[impl], s, Pattern)

    for s in sv2:
        impl = s_to_impl(s,Pattern,N_req)
        if impl_sv2.get(impl) == None:
            impl_sv2[impl] = calc_sv(s,Pattern)
        else:
            impl_sv2[impl] = sv_add_s(impl_sv1[impl], s, Pattern)
            
    N_class = 4
    result = 0
    LEVEL = 4
    g1 = list(impl_sv1.keys())
    g2 = list(impl_sv2.keys())
    Ms = []
    Msj = 4
    Dis = 0
    for i in range(N_class): # N_class = 4
        g11 = [j[0:(i+1)] for j in g1]
        g22 = [j[0:(i+1)] for j in g2]
        g = g11 + g22
        g = list(set(g))
        g = sorted(g, key=cmp_to_key(ComparebyImportanceClass))
        for t in g:
            sum_s1 = [0,0,0,0]
            sum_s2 = [0,0,0,0]
            for j in impl_sv1.keys():
                if j[0:(i+1)] == t:
                    for jj in range(i+1):
                        sum_s1[jj] += impl_sv1[j][jj]                     
            for j in impl_sv2.keys():
                if j[0:(i+1)] == t:
                    for jj in range(i+1):
                        sum_s2[jj] += impl_sv2[j][jj]
            cmp_r = comp_sv(sum_s1,sum_s2)
            if(cmp_r[0] != 0):
                result = cmp_r[0]
                LEVEL = i+1
                Ms = t
                Msj = cmp_r[1]
                Dis = cmp_r[2]
                break
        if(result != 0):
            break
    df_compare_record = df_compare_record.append({'A':name1,'B':name2,'Compare_result':result,
                                                  'K': LEVEL, 'Ms': Ms, 
                                                  'j': Msj, 'Dis': Dis},ignore_index=True)
    return result

def getDF(folder):
    df = pd.DataFrame(columns=['Severity'])
    file = folder + '/' + 'A_resultMod.txt'
    result = np.loadtxt(file)
    for i in range(10000): # len(fileList); 1000-5000-10000
        df.loc[i,'Severity'] = result[i]
    return df


def recordCompareResult(f, folder): 
    global df_compare_record
    df_list = {}
    config_list = os.listdir(folder)
    for config in config_list:
        df_list[config] = getDF(folder + '/' + config)
    for i in  range(len(config_list) - 1):
        for j in range((i+1),len(config_list)):
            Comp2ADSbySeverity(df_list[config_list[i]]['Severity'], df_list[config_list[j]]['Severity'],config_list[i],config_list[j] )
    writer = pd.ExcelWriter('*' + f + '_ALLcompare_result.xlsx',engine = 'xlsxwriter')
    df_compare_record.to_excel(writer,sheet_name = 'Sheet1')
    writer.save()
    

if __name__ == '__main__': 
    datafolder = '*'

    folder_list = ['***']
    # folder_list.remove('LeftAndRight_Datalog_2021_12_26_21_26')
    Scenario = ['BlindIntersection','CarOppositeLane', 'CloseToCrash', 'LeftAndRight', 'ParkedCarInFrontCarOppositeLane', 'RightTurn']
    for f in folder_list:
        print(datafolder + '/' + f)
        recordCompareResult(f, datafolder + '/' + f + '/New_Revised')
        df_compare_record = df_compare_record.drop(index = df_compare_record.index)
    


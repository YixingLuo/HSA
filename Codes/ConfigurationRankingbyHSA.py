import numpy as np
import os
import pandas as pd
from functools import cmp_to_key


Compare_count = 0
df_compare_record = pd.DataFrame(columns=['A', 'B', 'Compare_result', 'K', 'Ms', 'j', 'Dis']) 
rootdir = ''

from HierarchicalSafetyAssessment import ComparebyImportanceClass, s_to_impl, calc_sv, sv_add_s, comp_sv

# This function(getDF) read the recorded result and return a dataframe
def getDF(folder):
    df = pd.DataFrame(columns=['Severity'])
    file = folder + '/Requirements_Violation_Severity.txt'
    result = np.loadtxt(file)
    for i in range(10000): # len(fileList); 1000-5000-10000
        df.loc[i,'Severity'] = result[i]
    return df


# This function(Comp2ADSbySeverity) compare 2 ADS by their testing results' severity:
# input: ADS1 and ADS2 are their testing result(here are strings about ADS's configuration)
# output: result = -1 means ADS2 is safer,1 means the otherwise, 0 means ADS1 and ADS2 are tied
def Comp2ADSbySeverity(ADS1, ADS2):
    global df_compare_record
    global Compare_count
    global rootdir
    
    Compare_count += 1
    
    df1 = getDF(rootdir + '/' + ADS1)
    df2 = getDF(rootdir + '/' + ADS2)
    sv1 = df1['Severity']
    sv2 = df2['Severity']
    
    impl_sv1 = {}
    impl_sv2 = {}
    
    f = open(r"E:\UAV\mazda_PP\Hierarchical-Safety-Assessment\Results_RVA\Requirements_Level_Pattern.txt",encoding = "utf-8")
    f2 = open(r"E:\UAV\mazda_PP\Hierarchical-Safety-Assessment\Results_RVA\N_req.txt",encoding = "utf-8")
    
    N_req = eval(f2.read())
    Pattern = eval(f.read())
    
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
            impl_sv2[impl] = sv_add_s(impl_sv2[impl], s, Pattern)
            
    N_class = len(Pattern)
    result = 0
    LEVEL = len(Pattern)
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
            sum_s1 = [0 for x in range(0,N_class)]
            sum_s2 = [0 for x in range(0,N_class)]
            for j in impl_sv1.keys():
                if j[0:(i+1)] == t:
                    for jj in range(i+1):
                        sum_s1[jj] += impl_sv1[j][jj]
                        
            for j in impl_sv2.keys():
                if j[0:(i+1)] == t:
                    for jj in range(i+1):
                        sum_s2[jj] += impl_sv2[j][jj]
            # print("sum_s2 = ", sum_s2)
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
    df_compare_record = df_compare_record.append({'A':ADS1,'B':ADS2,'Compare_result':result,
                                                  'K': LEVEL, 'Ms': Ms, 
                                                  'j': Msj, 'Dis': Dis},ignore_index=True)
    return result

# This function(SortADS) sort a list of ADS by their satifactory of safety requirements 
# and record the compare result in excels
def SortADS(fname, compfolder):
    global df_compare_record
    pd.set_option('display.max_columns',None)
    pd.set_option('display.max_rows',None)
    
    ADS_list = os.listdir(compfolder)

    ADS_list = sorted(ADS_list, key=cmp_to_key(Comp2ADSbySeverity))
    
    
    df = pd.DataFrame(columns=['Scenario','rank'])
    ADS_list.reverse()
    df['Scenario'] = ADS_list
    
    # print(df)
    # print(df_compare_record)
    
    N_ADS = len(ADS_list)
    rank_count = 1
    rank_now = 1
    # df['rank'][0] = rank_now
    df.loc[0, 'rank'] = rank_now

    for i in range(1,N_ADS):
        query_stc = 'A == ' + "\'" + df.loc[i-1,'Scenario'] + "\'" + ' and B == ' + "\'" + df.loc[i,'Scenario']  + "\'"
        l = df_compare_record.query(query_stc)
        if l.empty == True:
            query_stc = 'A == ' + "\'" + df.loc[i,'Scenario'] + "\'" + ' and B == ' + "\'" + df.loc[i-1,'Scenario']  + "\'"
            l = df_compare_record.query(query_stc)
        
        l_dis = l.iloc[0]['Dis']
        if(l_dis == 0):
            rank_count += 1
        else:
            rank_count += 1
            rank_now = rank_count
        df.loc[i, 'rank'] = rank_now
        
    # * represent an address
    result_folder = '*/Hierarchical-Safety-Assessment/test_result/rank_list/'
    writer2 = pd.ExcelWriter(result_folder + 'Rankindlist_' + fname + '.xlsx',engine = 'xlsxwriter')
    df.to_excel(writer2,sheet_name = 'Sheet1')
    writer2.save()
    
    # writer3 = pd.ExcelWriter(result_folder + fname + '_Severity_Compare_process_record.xlsx',engine = 'xlsxwriter')
    # df_compare_record.to_excel(writer3,sheet_name = 'Sheet1')
    # writer3.save()

    global Compare_count
  
    

if __name__ == '__main__':
    # datafolder = 'E:/UAV/mazda_PP/Hierarchical-Safety-Assessment/TESTDATA'
    # folder_list = ['BlindIntersection']
    datafolder = '*/Hierarchical-Safety-Assessment/Results_RVA'
    folder_list = os.listdir(datafolder)
    folder_list.remove('README.md')
    folder_list.remove('Requirements_Level_Pattern.txt')
    folder_list.remove('N_req.txt')
    
    for f in folder_list:
        print(datafolder + '/' + f)
        rootdir = datafolder + '/' + f
        SortADS(f, datafolder + '/' + f)
        df_compare_record = df_compare_record.drop(index = df_compare_record.index)
        Compare_count = 0


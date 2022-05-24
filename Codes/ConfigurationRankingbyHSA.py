import numpy as np
import os
import pandas as pd
from functools import cmp_to_key
from HierarchicalSafetyAssessment import ComparebyImportanceClass, s_to_impl, calc_sv, sv_add_s, comp_sv

Compare_count = 0
df_compare_record = pd.DataFrame(columns=['A', 'B', 'Compare_result', 'K', 'Ms', 'j', 'Dis']) 
rootdir = ''

# This function(getDF) read the recorded result and return a dataframe
def getDF(folder):
    df = pd.DataFrame(columns=['Severity'])
    file = folder + '/Requirements_Violation_Severity.txt'
    result = np.loadtxt(file)
    for i in range(10000): # len(fileList); 1000-5000-10000
        df.loc[i,'Severity'] = result[i]
    return df


# This function(Comp2ADSbySeverity) compare 2 ADS by their testing results' severity:
# input: ADS1 and ADS2 (here are strings of ADS's configuration)
# output: result = -1 means ADS2 is safer,1 means the otherwise, 0 means ADS1 and ADS2 are tied
# #############=====Additional remarks====##############################
# note that we make the output of Comp2ADSbySeverity like this (only -1, 0, 1)
# because this function will be later used in "cmp_to_key" (a function provided by functools module)
# and this was function was introduced for the usage of python Sort(), 
# for more information about this cmp_to_key , see:https://docs.python.org/3/library/functools.html
# in short, this return-value-design make Sort() put the "worse" ADS configuration in the front of 
# the list than the better ones
# also, we record other useful information in df_compare_record (this is a global variable)
# useful information like K, Ms, Dis, etc, you can see more detailed description in comments
# in HierarchicalSafetyAssessment.py.
# in short, if Dis == 0, means Comp2ADSbySeverity cannot distinguish ADS1 and ADS2
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

    filename = os.path.abspath(os.path.join(os.getcwd(),"..")) + '/Results_RVA/Requirements_Level_Pattern.txt'
    f = open(filename, encoding = "utf-8")
    filename = os.path.abspath(os.path.join(os.getcwd(),"..")) + '/Results_RVA/N_req.txt'
    f2 = open(filename, encoding = "utf-8")
    
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
# #############=====Additional remarks====##############################
# as the comments of function Comp2ADSbySeverity, the Sort do returns a sorted list of ADS
# from the worst to the best, but there are ADSs that are "the same", so if we want to get a 
# specific rank value for each ADS we have to know which ADSs are the same, and since cmp_to_key
# cannot carry this kind of information, so we need to query this in df_compare_record
def SortADS(fname, compfolder):
    global df_compare_record
    pd.set_option('display.max_columns',None)
    pd.set_option('display.max_rows',None)
    
    ADS_list = os.listdir(compfolder)

    ADS_list = sorted(ADS_list, key=cmp_to_key(Comp2ADSbySeverity))
    
    
    df = pd.DataFrame(columns=['Scenario','rank'])
    ADS_list.reverse()
    df['Scenario'] = ADS_list

    
    N_ADS = len(ADS_list)
    rank_count = 1
    rank_now = 1
    df.loc[0, 'rank'] = rank_now

    for i in range(1,N_ADS):
        # query_stc construct a sql_like query, it searches the df_compare_record for the record that satisfied
        # A == ADS_list[i-1] && B == ADS_list[i] or A == ADS_list[i] && B == ADS_list[i]
        # because we do not know the order in which 2 ADS are compared
        query_stc = 'A == ' + "\'" + df.loc[i-1,'Scenario'] + "\'" + ' and B == ' + "\'" + df.loc[i,'Scenario']  + "\'"
        l = df_compare_record.query(query_stc)
        if l.empty == True:
            query_stc = 'A == ' + "\'" + df.loc[i,'Scenario'] + "\'" + ' and B == ' + "\'" + df.loc[i-1,'Scenario']  + "\'"
            l = df_compare_record.query(query_stc)
        
        # by the query about we get the record about this 2 ADS in df_compare_record
        # we only need to query each 2 adjacent ADS in the sorted list, 
        # because the "same" relation has transitivity, 
        # for example, if ADS1==ADS2, and ADS2==ADS3 and ADS3!=ADS4, 
        # than ADS1,ADS2,ADS3 will all have the same rank value 1, and ADS4's rank value will be 4
        
        l_dis = l.iloc[0]['Dis']
        if(l_dis == 0):
            rank_count += 1
        else:
            rank_count += 1
            rank_now = rank_count
        df.loc[i, 'rank'] = rank_now

    result_folder = os.path.abspath(os.path.join(os.getcwd(),"..")) + '/Results_HSA'
    if not os.path.exists(result_folder):
        os.mkdir(result_folder)
    writer = pd.ExcelWriter(result_folder + '/RankindList_' + fname + '.xlsx',engine = 'xlsxwriter')
    df.to_excel(writer,sheet_name = 'Sheet1')
    writer.save()


    global Compare_count
  
    

if __name__ == '__main__':

    datafolder = os.path.abspath(os.path.join(os.getcwd(),"..")) + '/Results_RVA'

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


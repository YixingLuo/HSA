import numpy as np
import os
import pandas as pd
from functools import cmp_to_key


Compare_count = 0
df_compare_record = pd.DataFrame(columns=['A', 'B', 'Compare_result', 'K', 'Ms', 'j', 'Dis']) 
rootdir = ''


# This function(ComparebyImportanceClass) compare 2 results by their Importance class.
# Note that the imput parameters(Ipc1, Ipc2) are already Importance class
# The returned result t is -1, 0 , 1; -1 means Ipc1 is severer than Ipc2,
# while 1 means that Ipc2 is severer. if t = 0, it means we can not distinguish
# which one is severer in this level(importance class)
def ComparebyImportanceClass(Ipc1, Ipc2): # sort a "Importance class" [0:k]
    result = 0
    for i in range(len(Ipc1)):
        if Ipc1[i] > Ipc2[i]:
            result = -1
            break
        elif Ipc1[i] < Ipc2[i]:
            result = 1
            break
    return result

# Severity compare

# This function(s_to_impl) calculate a result's Importance level by a given pattern
# input parameters: result(Severity) and given pattern(Pattern)
# output: the result's importance level
# Note that the given pattern should be a dict, in our case it is {0:(7,), 1:(2,), 2:(3,8), 3:(4,5,6)}
# N_req: the number of requirements in results, in out case it is 10
def s_to_impl(Severity, Pattern, N_req): # severity to ImpL                                                                                    
    p = [0 for x in range(0,N_req)]
    for i in range(N_req):
        if Severity[i] == 0:
            p[i] = 0
        else:
            p[i] = 1
    N_imp = len(Pattern)
    l = [0 for x in range(0,N_imp)]
    for i in range(N_imp):
        for j in range(len(Pattern[i])):
            l[i] += p[Pattern[i][j]]
    return tuple(l)

# This function(calc_sv) calculate a result's Severity by a given pattern(Pattern)
# input parameters: result(s) and given pattern(Pattern)
# output: the result's Severity(sv)
# Note that the given pattern should be a dict, in our case it is {0:(7,), 1:(2,), 2:(3,8), 3:(4,5,6)}
# N_req: the number of requirements in results, in out case it is 10
def calc_sv(s,Pattern):
    N_imp = len(Pattern)
    sv = [0 for x in range(0,N_imp)]
    for i in range(N_imp):
        for j in range(len(Pattern[i])):
            sv[i] += s[Pattern[i][j]]
    return sv

# This function(sv_add_s) add a result(s2) to a severity(s1), and return the overall severity
def sv_add_s(s1,s2, Pattern):
    N_imp = len(Pattern)
    for i in range(N_imp):
        for j in range(len(Pattern[i])):
            s1[i] += s2[Pattern[i][j]]
    return s1

# This function(comp_sv) compare 2 severity(sv1 and sv2), the returned result is a list:
# result[0] is the compare result:-1 means sv1 is severer,1 means the otherwise, 0 means sv1 and sv2 are tied
# result[1] records in which layer sv1 and sv2 are distinguished
# result[2] records sv1 and sv2's differneces in the layer in which they are distinguished
def comp_sv(sv1,sv2):
    result = [0,len(sv1),0]
    # print("compare_sv:",sv1,sv2)
    for i in range(len(sv1)):
        if sv1[i] > sv2[i]:
            result[0] = -1
            result[1] = i
            result[2] = sv1[i] - sv2[i]
            break
        elif sv1[i] < sv2[i]:
            result[0] = 1
            result[1] = i
            result[2] = sv2[i] - sv1[i]
            break
    return result


# This function(getDF) read the recorded result and return a dataframe
def getDF(folder):
    df = pd.DataFrame(columns=['Severity'])
    file = folder + '/A_resultMod.txt'
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
            impl_sv2[impl] = sv_add_s(impl_sv2[impl], s, Pattern)
            
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
    ADS_list = os.listdir(compfolder)

    ADS_list = sorted(ADS_list, key=cmp_to_key(Comp2ADSbySeverity))
    
    
    df = pd.DataFrame(columns=['Scenario'])
    
    df['Scenario'] = ADS_list
    
    # * represent an address
    writer2 = pd.ExcelWriter('*' + fname + '_Severity_Sort_list.xlsx',engine = 'xlsxwriter')
    df.to_excel(writer2,sheet_name = 'Sheet1')
    writer2.save()
    
    writer3 = pd.ExcelWriter('**' + fname + '_Severity_Compare_process_record.xlsx',engine = 'xlsxwriter')
    df_compare_record.to_excel(writer3,sheet_name = 'Sheet1')
    writer3.save()

    global Compare_count
  
    

if __name__ == '__main__':
    datafolder = '***'
    # folder_list = ['CarOppositeLane_Datalog_2021_12_26_21_25', 'ParkedCarInFrontCarOppositeLane_Datalog_2021_12_26_21_27', 'RightTurn_Datalog_2021_12_26_21_27']
    folder_list = ['***']
    Scenario = ['BlindIntersection','CarOppositeLane', 'CloseToCrash', 'LeftAndRight', 'ParkedCarInFrontCarOppositeLane', 'RightTurn']
    for f in folder_list:
        print(datafolder + '/' + f)
        rootdir = datafolder + '/' + f + '/New_Revised'
        SortADS(f, datafolder + '/' + f + '/New_Revised')
        df_compare_record = df_compare_record.drop(index = df_compare_record.index)
        Compare_count = 0

    


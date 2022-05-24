import numpy as np
import os
from time import time
import pandas as pd

df_compare_record = pd.DataFrame(columns=['Configuration A', 'Configuration B', 'Comparison Results'])

# This function(get_comparison_under_scenario) is designed to calculate comparison results of two configurations through ConservativeComparison under a test scenario
# input parameters: violation_severity_A, violation_severity_B
# output: the comparison results of given test scenario
def get_comparison_under_scenario (violation_severity_A, violation_severity_B):
    comparison_severity = []
    ## compare the violation severity of each requirement for configuration A and configuration B
    for i in range(len(violation_severity_A)):
        if violation_severity_A[i] > violation_severity_B[i]:
            comparison_severity.append(1)
        elif violation_severity_A[i] < violation_severity_B[i]:
            comparison_severity.append(2)
        else:
            comparison_severity.append(0)

    if comparison_severity.count(0) == len(violation_severity_A): ## Configuration_A ties with Configuration_B
        return 0
    elif comparison_severity.count(2) == 0: ## Configuration_B is safer
        return 1
    elif comparison_severity.count(1) == 0: ## Configuration_A is safer
        return 2
    else: ## Configuration_A and Configuration_B cannot be compared under this test scenario
        return -1

# This function(get_comparison_under_testsuite) is designed to calculate comparison results of two configurations through ConservativeComparison under the whole test suite
# input parameters: RVA_results_A, RVA_results_B, scenario_number
# output: the list of comparison results of the whole test suite
def get_comparison_under_testsuite(RVA_results_A, RVA_results_B, scenario_number):
    compare_list = []
    fileList_orig = np.loadtxt(RVA_results_A + "/Requirements_Violation_Severity.txt") ## Results of requirements violation severity of Configuration_A under the whole test suite
    fileList_mod = np.loadtxt(RVA_results_B + "/Requirements_Violation_Severity.txt")  ## Results of requirements violation severity of Configuration_B under the whole test suite
    for i in range(scenario_number):
        orig_result = fileList_orig[i]
        mod_result = fileList_mod[i]
        comparison_severity = get_comparison_under_scenario(orig_result, mod_result) ## get comparison result under a specific test scenario
        compare_list.append(comparison_severity)

    return compare_list

if __name__ == '__main__':
    Traffic_Situations = [
                  "CarOppositeLane",
                  "CloseToCrash",
                  "LeftAndRight",
                  "BlindIntersection",
                  "RightTurn",
                  "CarBehindAndInFront"
                  ]

    for Traffic in Traffic_Situations:

        RVA_result = os.path.join(os.getcwd(), "..", "Results_RVA/" + Traffic)
        print(RVA_result)
        configuration_list = os.listdir(RVA_result)
        configuration_list.sort()

        num_scenarios = 10000 ## number of test scenarios in the test suite
        used_time = 0 ## time used for the total comparison
        # alpha_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
        alpha = 1 ## Percentage of considered test scenarios

        ## To calculate the distinguishable rate of ConservativeComparison under different percentages of considered test scenarios
        comparison_all = []
        count = 0
        for pre in range(len(configuration_list)):
            for next in range(pre + 1, len(configuration_list)):
                pre_result_folder = RVA_result + '/' + configuration_list[pre]
                next_result_folder = RVA_result + '/' + configuration_list[next]
                start_time = time()
                comparison = get_comparison_under_testsuite(pre_result_folder, next_result_folder, num_scenarios)
                comparison_all.append(comparison)
                end_time = time()
                used_time += end_time - start_time
                count += 1
                if count % 10 == 0:
                    print('finish:', count, "/ 1830 ")
                comparison = np.array(comparison)
                # print(np.array(comparison).shape, np.sum(np.array(comparison) == 0), np.sum(np.array(comparison) == 1), np.sum(np.array(comparison) == 2))
                if (np.sum(comparison == 1) + np.sum(comparison == 0)) >= alpha * num_scenarios and np.sum(comparison == 1) > 0:
                    df_compare_record = df_compare_record.append(
                        {'Configuration A': configuration_list[pre], 'Configuration B': configuration_list[next],
                         'Comparison Results': "A=B"},
                        ignore_index=True)
                elif (np.sum(comparison == 2) + np.sum(comparison == 0)) >= alpha * num_scenarios and np.sum(comparison == 2) > 0:
                    df_compare_record = df_compare_record.append(
                        {'Configuration A': configuration_list[pre], 'Configuration B': configuration_list[next],
                         'Comparison Results': "A<B"},
                        ignore_index=True)
                elif np.sum(comparison == 0) >= alpha * num_scenarios:
                    df_compare_record = df_compare_record.append(
                        {'Configuration A': configuration_list[pre], 'Configuration B': configuration_list[next],
                         'Comparison Results': "A>B"},
                        ignore_index=True)
                else:
                    df_compare_record = df_compare_record.append(
                        {'Configuration A': configuration_list[pre], 'Configuration B': configuration_list[next],
                         'Comparison Results': "incomparable"},
                        ignore_index=True)


        print("time_used:", used_time/count, count, used_time)


        result_folder = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/Results_ConservativeComparison' ## results save folder
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)

        ## save the comparison results under all test scenarios
        result_name = result_folder + "/ConservativeComparison_All_" + Traffic + ".txt"
        np.savetxt(result_name, comparison_all, fmt="%d", delimiter=" ")

        ## save comparison results of ConservativeComparison to files
        writer = pd.ExcelWriter(result_folder + '/ConservativeComparison_' + Traffic + '.xlsx', engine='xlsxwriter')
        df_compare_record.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        df_compare_record = df_compare_record.drop(index=df_compare_record.index)
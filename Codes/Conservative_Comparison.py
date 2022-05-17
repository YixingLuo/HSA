import numpy as np
import os
from time import time


def get_comparison_under_scenario (violation_severity_1, violation_severity_2):
    comparison_severity = []
    for i in range(len(violation_severity_1)):
        if violation_severity_1[i] > violation_severity_2[i]:
            comparison_severity.append(1)
        elif violation_severity_1[i] < violation_severity_2[i]:
            comparison_severity.append(2)
        else:
            comparison_severity.append(0)

    if comparison_severity.count(0) == len(violation_severity_1): ## tie
        return 0
    elif comparison_severity.count(2) == 0: ## configuration_2 is safer
        return 1
    elif comparison_severity.count(1) == 0: ## configuration_1 is safer
        return 2
    else: ## cannot compare
        return -1

def get_comparison_under_testsuite(RVA_results_1, RVA_results_2, num):
    compare_list = []
    fileList_orig = np.loadtxt(RVA_results_1 + "/Requirements_Violation_Severity.txt")
    fileList_mod = np.loadtxt(RVA_results_2 + "/Requirements_Violation_Severity.txt")
    scenario_number = num
    for i in range(scenario_number):
        orig_result = fileList_orig[i]
        mod_result = fileList_mod[i]
        comparison_severity = get_comparison_under_scenario(orig_result, mod_result)
        compare_list.append(comparison_severity)

    return compare_list

if __name__ == '__main__':
    Traffic_Situations = [
                  "CarOppositeLane",
                  "CloseToCrash",
                  "LeftAndRight",
                  "BlindIntersection",
                  "RightTurn_Datalog",
                  "CarBehindAndInFront"
                  ]

    for Traffic in Traffic_Situations:

        RVA_result = os.path.join(os.getcwd(), "..", "Results_RVA/" + Traffic)
        print(RVA_result)
        configuration_list = os.listdir(RVA_result)
        configuration_list.sort()

        num_scenarios = 10000
        used_time = 0

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

        print("time_used:", used_time/count, count, used_time)
        result_name = os.getcwd() + "/ConservativeComparison_" + Traffic + ".txt"
        np.savetxt(result_name, comparison_all, fmt="%d", delimiter=" ")


        ## Distinguishable Rate
        ## Percentage of considered test scenarios
        alpha_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

        comparison_list = np.loadtxt(result_name)
        comparison = np.array(comparison_list)

        for alpha in alpha_list:
            comparable_rate_list = []
            tie_rate_list = []
            not_equal_rate_list = []
            incomparable_rate_list = []

            count_tie = 0
            count_better = 0
            count_worse = 0
            incomparable = 0
            for i in range(comparison.shape[0]):
                current_comparison = comparison[i][0:num_scenarios]
                if (np.sum(current_comparison == 1) + np.sum(
                        current_comparison == 0)) >= alpha * num_scenarios and np.sum(current_comparison == 1) > 0:
                    count_worse += 1
                elif (np.sum(current_comparison == 2) + np.sum(
                        current_comparison == 0)) >= alpha * num_scenarios and np.sum(current_comparison == 2) > 0:
                    count_better += 1
                elif np.sum(current_comparison == 0) >= alpha * num_scenarios:
                    count_tie += 1
                else:
                    incomparable += 1

            comparable_rate = 1 - incomparable / comparison.shape[0]
            tie_rate = count_tie / comparison.shape[0]
            not_equal_rate = (count_worse + count_better) / comparison.shape[0]
            incomparable_rate = incomparable / comparison.shape[0]
            comparable_rate_list.append(comparable_rate)
            tie_rate_list.append(count_tie)
            not_equal_rate_list.append(count_worse + count_better)
            incomparable_rate_list.append(incomparable)


            for i in range(len(tie_rate_list)):
                print("tie:", tie_rate_list[i])
            for i in range(len(not_equal_rate_list)):
                print("not_equal:", not_equal_rate_list[i])
            for i in range(len(incomparable_rate_list)):
                print("incomparable:", incomparable_rate_list[i])

            print("alpha:", alpha, np.mean(comparable_rate_list))
import json

result_path = ""
with open(result_path, "r") as f:
    summary = json.load(f)

correct_sum = 0
focal_method_sum = 0
total_method_sum = 0
all_methods = 0
covered_methods = 0
for project, res in summary["project_count"].items():
    # count the number of True values in the dictionary
    true_count = sum(value for value in res["methods"].values() if value)

    all_methods += len(res["methods"])
    covered_methods += true_count
    # count the percentage of True values
    true_percentage = (true_count / len(res["methods"])) * 100
    correct_sum += res['passed']
    total_method_sum += res['total']
    print(project, res['correct'] / res["total"] * 100, true_percentage)
    # print(res['passed'], res["total"], true_count, len(res["methods"]))

# print(correct_sum)
print("Total", correct_sum / total_method_sum * 100, covered_methods / all_methods * 100)
# print(covered_methods / all_methods * 100)

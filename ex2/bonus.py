from pulp import *
from datetime import datetime
import numpy as np
from datetime import timedelta

def solve_it_via_lp(surgeries):
    prob = LpProblem("Surgeries Assignment", LpMinimize)


    anesthesiologists = range(1, len(surgeries))  # Assuming 5 anesthesiologists
    surgery_ids = [surgery['surgery_id'] for surgery in surgeries]
    x = LpVariable.dicts('x', (anesthesiologists, surgery_ids), cat='Binary')

    y = LpVariable.dicts('y', (anesthesiologists, surgery_ids), cat='Binary')
    earliest_surgery = LpVariable.dicts('Earliest_Surgery', anesthesiologists, cat='Continuous')
    latest_surgery = LpVariable.dicts('Latest_Surgery', anesthesiologists, cat='Continuous')

    # Define the objective function
    prob += lpSum([(5 + 0.5 * lpSum([(surgeries[j-1]['duration'] - 9) * y[i][j] for j in surgery_ids])) for i in anesthesiologists])

    for j in surgery_ids:
        prob += lpSum([y[i][j] for i in anesthesiologists]) >= 1

    # Assignment Constraint
    for i in anesthesiologists:
        for j in surgery_ids:
            prob += x[i][j] == y[i][j]

    # Room Constraint
    rooms = range(1, 21)
    for j in surgery_ids:
        prob += lpSum([x[i][j] for i in anesthesiologists]) <= 1

    # Gap Constraint
    for i in anesthesiologists:
        for k in range(1, len(surgery_ids)):
            prob += x[i][surgery_ids[k]] + x[i][surgery_ids[k-1]] <= 1

    for i in anesthesiologists:
        earliest_surgery[i] = lpSum(
            [datetime.strptime(str(surgeries[j - 1]['start_time']), '%Y-%m-%d %H:%M:%S').timestamp() * x[i][j] for j in
             surgery_ids])
        latest_surgery[i] = lpSum([datetime.strptime(str(surgeries[j - 1]['end_time']), '%Y-%m-%d %H:%M:%S').timestamp()* x[i][j] for j in surgery_ids])

        duration = latest_surgery[i] - earliest_surgery[i]
        prob += duration >= 5*60
        prob += duration <= 12*60
    # Solve the problem
    prob.solve()

    # Print the status of the solution
    print("Status:", LpStatus[prob.status])

    used_anesthesiologists = []
    # Print the optimal assignments
    for i in anesthesiologists:
        for j in surgery_ids:
            if value(x[i][j]) == 1:
                print(f"Anesthesiologist {i} is assigned to surgery {j}")
                used_anesthesiologists.append(i)
    # Print the optimal cost
    print("Optimal Cost:", value(prob.objective))
    print("The Number of anesthesiologists: ", len(np.unique(used_anesthesiologists)))

def read_surgeries_from_csv(filename):
    import csv
    surgeries = []

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            surgery_id = int(row[0])
            start_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
            duration = int((end_time - start_time).total_seconds() / 60)  # Duration in minutes
            surgeries.append({'surgery_id': surgery_id, 'start_time': start_time, 'end_time': end_time, 'duration': duration})
    return surgeries




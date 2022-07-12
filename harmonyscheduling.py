import numpy as np
import pandas as pd
import math
import random
from statistics import mean
from operator import itemgetter

staff_planning = [
    [[0, 0, 10],[1, 0, 10],[2, 0, 10],[3, 0, 10],[4, 0, 10],[5, 0, 10],[6, 0, 10],[7, 0, 10],[8, 0, 10],[9, 0, 10],[10, 0, 10]],
    [[0, 0, 10],[1, 0, 10],[2, 0, 10],[3, 0, 10],[4, 0, 10],[5, 0, 10],[6, 0, 10],[7, 0, 10],[8, 0, 10],[9, 0, 10],[10, 0, 10]],
    [[0, 0, 10],[1, 0, 10],[2, 0, 10],[3, 0, 10],[4, 0, 10],[5, 0, 10],[6, 0, 10],[7, 0, 10],[8, 0, 10],[9, 0, 10],[10, 0, 10]],
    [[0, 0, 10],[1, 0, 10],[2, 0, 10],[3, 0, 10],[4, 0, 10],[5, 0, 10],[6, 0, 10],[7, 0, 10],[8, 0, 10],[9, 0, 10],[10, 0, 10]],
    [[0, 0, 10],[1, 0, 10],[2, 0, 10],[3, 0, 10],[4, 0, 10],[5, 0, 10],[6, 0, 10],[7, 0, 10],[8, 0, 10],[9, 0, 10],[10, 0, 10]]
]
hourlystaff_needed = np.array([
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2]
])

"""
Employee Present: analyse whether the employee is present yes or no on a given time
Based on the employee list of 3 (id, start time, duration)
"""
def employee_present(employee, time):
    employee_start_time = employee[1]
    employee_duration = employee[2]
    employee_end_time = employee_start_time + employee_duration
    if (time >= employee_start_time) and (time < employee_end_time):
        return True
    return False


"""
convert a staff planning to a staff-needed plannig
The employee planning is organised per employee, the staff-needed planning is the number of employees working per hour
The staff-needed planning is based on the employee planning and will allow to calculate the difference with the staff-needed
It doesnt work overnight, but our shop isnt open at night anyway
"""


def staffplanning_to_hourlyplanning(staff_planning):
    hourlystaff_week = []
    for day in staff_planning:

        hourlystaff_day = []
        for employee in day:

            employee_present_hour = []
            for time in range(0, 24):
                employee_present_hour.append(employee_present(employee, time))

            hourlystaff_day.append(employee_present_hour)

        hourlystaff_week.append(hourlystaff_day)

    hourlystaff_week = np.array(hourlystaff_week).sum(axis=1)
    return hourlystaff_week


"""
the cost is calculated as hours understaffed + hours overstaffed
"""


def cost(hourlystaff, hourlystaff_needed):
    errors = hourlystaff - hourlystaff_needed
    overstaff = abs(errors[errors > 0].sum())
    understaff = abs(errors[errors < 0].sum())

    overstaff_cost = 1
    understaff_cost = 1

    cost = overstaff_cost * overstaff + understaff_cost * understaff
    return cost


"""
generate an entirely random staff planning for a certain number of days
start time is random between 0 and 23; duration is random between 0 and 10
"""


def generate_random_staff_planning(n_days, n_staff):
    period_planning = []
    for day in range(n_days):
        day_planning = []
        for employee_id in range(n_staff):
            start_time = np.random.randint(0, 23)
            duration = np.random.randint(0, 10)
            employee = [employee_id, start_time, duration]
            day_planning.append(employee)

        period_planning.append(day_planning)

    return period_planning

# An example of the code until here

"""
create a parent generation of n parent plannings
"""
def initiate_hm(HMS, n_days = 7, n_staff = 11):
    harmonymemory = []
    for i in range(HMS):
        harmony = generate_random_staff_planning(n_days = n_days, n_staff = n_staff)
        hourly_planning = staffplanning_to_hourlyplanning(harmony)
        score = cost(hourly_planning, hourlystaff_needed)
        harmonymemory.append({"harmony": harmony, "score": score})
    return harmonymemory

"""
the overall function
"""

def harmony_search(hourlystaff_needed, HMS = 20, HMCR = 0.9,PAR = 0.2,NI = 1000):
    bw1 = 6
    bw2 = 3
    n_days = 5
    n_staff = 11
    hm = initiate_hm(HMS, n_days, n_staff)
    hm = sorted(hm, key=itemgetter('score'))
    for _ in range(NI):
        harmonybaru = np.zeros(np.array(hm[0]["harmony"]).shape)
        for indexdays in range(n_days):
            for indexstaff in range(n_staff):
                harmonybaru[indexdays][indexstaff][0]=indexstaff
                for i in range(1,3):
                    if HMCR >= random.random():
                        harmonybaru[indexdays][indexstaff][i] = random.choice(hm)["harmony"][indexdays][indexstaff][i]
                        if PAR >= random.random():
                            if i == 1:
                                harmonybaru[indexdays][indexstaff][i] += random.randint(-bw1, bw1)
                                if harmonybaru[indexdays][indexstaff][i] < 0:
                                    harmonybaru[indexdays][indexstaff][i] = 0
                                elif harmonybaru[indexdays][indexstaff][i] > 23:
                                    harmonybaru[indexdays][indexstaff][i] = 23
                            else:
                                harmonybaru[indexdays][indexstaff][i] += random.randint(-bw2, bw2)
                                if harmonybaru[indexdays][indexstaff][i] < 0:
                                    harmonybaru[indexdays][indexstaff][i] = 0
                                elif harmonybaru[indexdays][indexstaff][i] > 10:
                                    harmonybaru[indexdays][indexstaff][i] = 10
                    else:
                        if i == 1:
                            harmonybaru[indexdays][indexstaff][i] = np.random.randint(0, 23)
                        else:
                            harmonybaru[indexdays][indexstaff][i] = np.random.randint(0, 10)
        hourly_planning = staffplanning_to_hourlyplanning(harmonybaru)
        new_score = cost(hourly_planning, hourlystaff_needed)
        if new_score < hm[-1]["score"]:
            hm[-1]["harmony"] = harmonybaru
            hm[-1]["score"] = new_score
            hm = sorted(hm, key=itemgetter('score'))
        # print('generations best is: {}, generations worst is: {}'.format(hm[0]["score"],hm[-1]["score"]))
    return hm[0]
listbest = []
for i in range(20):
    print(i)
    listbest.append(harmony_search(hourlystaff_needed, HMS = 20, HMCR = 0.9,PAR = 0.2,NI = 10000))
listscore = [harmony["score"] for harmony in listbest]
print("min = ",min(listscore))
print("mean = ",mean(listscore))
print("max = ",max(listscore))
print("listscore = ",listscore)
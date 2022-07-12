import numpy as np
import random
from operator import itemgetter
from statistics import mean

hourlystaff_needed = np.array([
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2],
    [0, 0, 0, 0, 0, 0, 4, 4, 4, 2, 2, 2, 6, 6, 2, 2, 2, 6, 6, 6, 2, 2, 2, 2]
])

hm=[]
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

def update_memory(hm,new_score,new_harmony,ucb,ucw):
    best = hm[0].copy()
    if new_score < hm[-1]["score"]:
        hm[-1]["harmony"] = new_harmony
        hm[-1]["score"] = new_score
        hm = sorted(hm, key=itemgetter('score'))
        ucw=0
        if best != hm[0]:
            ucb = 0
    return hm,ucb,ucw
"""
the overall function
"""


def harmony_search(hourlystaff_needed, HMS = 20, HMCR = 0.9,PARMIN = 0.0,PARMAX = 1.0,NI = 1000):
    bw1 = 6
    bw2 = 3
    ucb = 0
    ucw = 0
    ngh = 4
    fcb = 10
    fcw = 10
    n_days = 5
    n_staff = 11
    hm = initiate_hm(HMS, n_days, n_staff)
    hm = sorted(hm, key=itemgetter('score'))
    for iteration in range(NI):
        PAR = PARMIN + (PARMAX - PARMIN) / NI * iteration
        harmonybaru = np.zeros(np.array(hm[0]["harmony"]).shape).tolist()
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
        harmonybaru = harmonybaru
        hourly_planning = staffplanning_to_hourlyplanning(harmonybaru)
        new_score = cost(hourly_planning, hourlystaff_needed)
        hm,ucb,ucw = update_memory(hm,new_score,harmonybaru,ucb,ucw)
        if ucb >= fcb:
            hm_top = hm[:ngh]
            new_harmony = list()
            for indexdays in range(n_days):
                day = []
                for indexstaff in range(n_staff):
                    staff = []
                    staff.append(indexstaff)
                    for i in range(1,3):
                        listnumber = [staff[i] for hm in hm_top for days in hm["harmony"] for staff in days]
                        min_among_top = min(listnumber)
                        max_among_top = max(listnumber)
                        staff.append(round(min_among_top + (max_among_top - min_among_top) * random.random()))
                    day.append(staff)
                new_harmony.append(day)
            hourly_planning = staffplanning_to_hourlyplanning(new_harmony)
            new_score = cost(hourly_planning, hourlystaff_needed)
            hm, ucb, ucw = update_memory(hm, new_score, harmonybaru, ucb, ucw)
        if ucw >= fcw:
            copycat_harmony = hm[-1]["harmony"].copy()
            for indexdays in range(n_days):
                for indexstaff in range(n_staff):
                    for i in range(1,3):
                        copycat_harmony[indexdays][indexstaff][i] += (hm[0]["harmony"][indexdays][indexstaff][i] - hm[-1]["harmony"][indexdays][indexstaff][i]) * random.random()
            hourly_planning = staffplanning_to_hourlyplanning(copycat_harmony)
            new_score = cost(hourly_planning, hourlystaff_needed)
            hm, ucb, ucw = update_memory(hm, new_score, copycat_harmony, ucb, ucw)
        ucb+=1
        ucw+=1
        # print('generations best is: {}, generations worst is: {}'.format(hm[0]["score"],hm[-1]["score"]))
    return hm[0]

listbest = []
for i in range(20):
    print(i)
    listbest.append(harmony_search(hourlystaff_needed, HMS = 20, HMCR = 0.9,PARMIN = 0.0,PARMAX = 1,NI = 10000))
print("best harmony = ")
print(listbest[0]["harmony"])
print("best score = ")
print(listbest[0]["score"])
listscore = [harmony["score"] for harmony in listbest]
print("min = ",min(listscore))
print("mean = ",mean(listscore))
print("max = ",max(listscore))
print("listscore = ",listscore)
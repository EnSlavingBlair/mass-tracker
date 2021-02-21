from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

### Read data from file

### mass file should be plain text and structured eg:
# Date	Mass	Time
# 01/01/20	78.3	Morning
### with no trailing \n
### other files should be plain text and structured eg:
# 01/01/20
# 02/01/20
### with no trailing \n

file_lines = []
with open("mass-data", "r") as f:
    for line in f:
        file_lines.append(line)

feast_lines = []
with open("feast_holidays", "r") as f:
    for line in f:
        feast_lines.append(line)

period_lines = []
with open("period_start", "r") as f:
    for line in f:
        period_lines.append(line)

med_lines = []
with open("medication", "r") as f:
    for line in f:
        med_lines.append(line)

### Organise data into usable lists

feast_dates = []
for idx in range(len(feast_lines)):
    feast_dates.append(datetime.strptime(feast_lines[idx][:-1], '%d/%m/%y'))

period_dates = []
for idx in range(len(period_lines)):
    period_dates.append(datetime.strptime(period_lines[idx][:-1], '%d/%m/%y'))

med_dates = []
for idx in range(len(med_lines)):
    med_dates.append(datetime.strptime(med_lines[idx][:-1], '%d/%m/%y'))

date = []
mass = []
time = []
titles = []
for idx in range(len(file_lines)):
    # Get the date, mass, time and titles of each column in the mass file
    if idx == 0:
        titles.append(file_lines[idx][:-1].split('\t'))
        if titles[0][0] != "Date" or titles[0][1] != "Mass" or titles[0][2] != "Time":
            print('The format needs to be "Date \t Mass \t	Time", and is case sensitive. Please fix.')
            break
        else:
            pass
    else:
        time_sngl = file_lines[idx][:-1].split('\t')[2]
        if time_sngl == "Morning":
            time_sngl = " 9:00"
        elif time_sngl == "Midday":
            time_sngl = " 12:00"
        elif time_sngl == "Afternoon":
            time_sngl = " 15:00"
        elif time_sngl == "Evening":
            time_sngl = " 18:00"
        elif time_sngl == "Night":
            time_sngl = " 21:00"
        date.append(datetime.strptime(file_lines[idx][:-1].split('\t')[0]+time_sngl, '%d/%m/%y %H:%M'))
        mass.append(float(file_lines[idx][:-1].split('\t')[1]))

### Get date and times into usable format

yr_mnth = []
month = 0
count = 0
date_ticks = []
month_ave = []
month_mass = []
month_std = []
for elem in date:
    if elem.month != month:
        if month_mass != []:
            month_ave.append(round(np.average(month_mass),1))
            month_std.append(round(np.std(month_mass),1))
        month_mass = [mass[count]]
        yr_mnth.append(elem.strftime("%Y/%m")+"\n"+str(mass[count])+'Kg')
        month = elem.month
        date_ticks.append(date[count])
    else:
        month_mass.append(mass[count])
    count += 1

month_ave.append(round(np.average(month_mass),1))
month_std.append(round(np.std(month_mass),1))

### Calcualte BMI

height = 1.77
bmi = np.round(np.array(month_ave) / height ** 2, 1)
max_norm_bmi = 25
min_norm_bmi = 18.5

### Calculate moving average

window_size = 9
moving_averages = np.full(np.shape(mass), np.nan)
for idx in range(len(mass)):
    if idx >= window_size:
        moving_averages[idx] = np.average(mass[idx - window_size : idx])
    elif idx != 0:
        moving_averages[idx] = np.average(mass[:idx])

last_month_mass = [mass[-i] for i in range(1, 31)]

### Plot daily data

plt.plot(date, mass, label="data")
plt.plot(date, moving_averages, label=str(window_size+1)+" day ave")
plt.xticks(ticks=date_ticks, labels=yr_mnth)
plt.vlines(feast_dates, ymin = min(mass), ymax = max(mass),
           colors = 'purple', label='feast days')
plt.vlines(period_dates, ymin = min(mass), ymax = max(mass),
           colors = 'red', label='period start')
plt.vlines(med_dates, ymin = min(mass), ymax = max(mass),
           colors = 'tab:green', label='Meds taken')
plt.legend()
plt.title("Mass Measurements over time.\nLast Month Average: "+str(round(np.average(last_month_mass),1)))
plt.ylabel("Mass (Kg)")
plt.xlabel("Date (YYYY/MM)")
plt.grid(axis='y')
plt.savefig('mass_over_time.png')
# plt.show()
plt.clf()

### Plot monthly averages

fig,ax = plt.subplots()

ax.errorbar(range(len(month_ave)), month_ave, yerr=month_std)
ax.set_ylabel("Mass", color='blue')
plt.title("Monthly Averages and BMI")
plt.xticks(ticks=range(len(month_ave)), labels=yr_mnth)
plt.grid(axis='y')

ax2=ax.twinx()
ax2.plot(bmi, 'o', color='orange')
ax2.set_ylabel("BMI", color='orange')

if max(bmi) >= max_norm_bmi-0.5:
    ax2.axhline(y=max_norm_bmi, color='orange')
else:
    pass

if max(bmi) <= min_norm_bmi+0.5:
    ax2.axhline(y=min_norm_bmi, color='orange')
else:
    pass

# plt.show()

plt.savefig("monthly_averages.png")
# plt.show()
plt.clf()

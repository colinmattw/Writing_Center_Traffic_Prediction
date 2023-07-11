# Imports from longest to shortest because it looks better
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
from canvasapi import Canvas
import datetime
import math
import csv
import re


# Course class
class Course:
    def __init__(self):
        self.instructor = None
        self.section = None
        self.assignment_list = []
        self.population = 0
        self.name  = None
        self.total_points = 0

    # Set the section and instructor for the course based on the course name
    def set_section_and_instructor(self):
        instructors = ['Aaron Wilder', 'KC Chan-Brose', 'Tanisha Neely']
        self.section = int(re.search(r".*([0-7])", self.name).group(1))

        if(self.section == 2):
            self.instructor = instructors[1]
        if(self.section == 5):
            self.instructor = instructors[0]
        if(self.section == 6):
            self.instructor = instructors[2]
        if(self.section == 7):
            self.instructor = instructors[2]

    # Set amount of students in course based on the course's section
    def set_population(self):
        if(self.section == 2):
            self.population = 17
        if(self.section == 5):
            self.population = 15
        if(self.section == 7):
            self.population = 18


# Assignment class
class Assment:
    def __init__(self, name, points, date, desc, course : Course):
        self.name = name
        self.points = points
        self.course = course
        self.max_coeff = 0
        if(date):
            date_str = re.match(r"(202[0-2])-([0-9]{2})-([0-9]{2}).*", date)
            year = int(date_str.group(1))
            month = int(date_str.group(2))
            day = int(date_str.group(3))

            self.duedate = datetime.datetime(year, month, day, 1, 1, 1, 1)
        else:
            self.duedate = None
        self.description = desc
        self.instructor = self.course.instructor
        self.grade_percentage = 0

    # Set percentage of final grade assignment is worth
    def set_final_grade_percentage(self, course):
        if(self.points):
            self.grade_percentage = self.points / course.total_points

    # Coeff used for distribution function
    def set_max_coeff(self):
        if(self.grade_percentage):
            self.max_coeff = self.course.population * self.grade_percentage


# Distribution class
class Dist:
    def __init__(self, max, rate, sigma_midpoint):
        self.max = max
        self.rate = rate
        self.sigma_midpoint = sigma_midpoint

    # Logistic function for calculating demand
    def func(self, days_before_due_date):
        return self.max / (1 + math.exp(self.rate * (days_before_due_date - self.sigma_midpoint)))

    # Return array of all the days the assignment has impact on and their contribution
    def get_distribution(self, coeff):
        size = 0
        output = 1
        dist = []
        while output > 0.1:
            output = coeff * self.func(size)
            dist.append(output)
            size += 1
        return dist


# Array of distribution outputs class
class Dist_Array:
    def __init__(self, dist : Dist, assignmnet : Assment):
        self.array = dist.get_distribution(assignmnet.max_coeff)
        self.start_date = assignmnet.duedate
        self.dates = [self.start_date]
        if(self.start_date):
            next_day = self.start_date
            for _ in enumerate(self.array[:-1]):
                next_day = next_day - datetime.timedelta(days=1)
                self.dates.append(next_day)


# Distribution init
dist = Dist(1, 0.1, 1)

# Canvas API URL
API_URL = "https://marian.instructure.com"
# Canvas API key
API_KEY = "1~vZLh4UkhSzqi3c7vNLQWWC5AWG8pudf0PaElEUnCq8pjJLpPaZGCwdpIJlg0vUfq"
canvas = Canvas(API_URL, API_KEY)

# Get accounts (paginated list)
paginated_accounts = canvas.get_accounts()

# Un-paginate accounts list
accounts = []
for i in paginated_accounts:
    accounts.append(i)

# Use the first account in the list
account = accounts[0]
paginated_courses = account.get_courses()

# Init course objects
courses = []
assignmnets = []
for course in paginated_courses:
    course_obj = Course()
    course_obj.name = course.name
    course_obj.set_section_and_instructor()
    course_obj.set_population()
    course_points = 0

    # Calculate total points in course
    temp_assignment_list = course.get_assignments()
    for a in temp_assignment_list:
        if(a.points_possible):
            course_points += a.points_possible
    course_obj.total_points = course_points

    # Construct list of assignmnent objects for course object
    for a in temp_assignment_list:
        course_obj.assignment_list.append(Assment(a.name, a.points_possible, a.due_at, a.description, course_obj))

    # Use total points in course to get percentage of final grade for each
    # assignment, then add assignment to global list of assignments
    for i in course_obj.assignment_list:
        i.set_final_grade_percentage(course_obj)
        i.set_max_coeff()
        assignmnets.append(i)

    # Add course object to global list of courses
    courses.append(course_obj)

# Set first and last day of semester
first_day = datetime.datetime(2022, 8, 22, 1,1,1,1)
last_day = datetime.datetime(2022, 12, 20, 1,1,1,1)
size_in_days = (last_day - first_day).days
date_array = [[0 for _ in range(2)] for _ in range(size_in_days)]

# Make array of all days in between first and last
current_day = first_day
for i in range(size_in_days):
    date_array[i][0] = current_day
    date_array[i][1] = 0
    current_day = current_day + datetime.timedelta(days=1)

# Make the distribution arrays for each assignment, 
# then sum overlapping distributions in date_array
for a in assignmnets:
    current_dist = Dist_Array(dist, a)
    for i,_ in enumerate(current_dist.dates):
        for j,_ in enumerate(date_array):
            if(current_dist.dates[i] == date_array[j][0]):
                date_array[j][1] += current_dist.array[i]


#Get total appointments for semester
total_apts = 0
for i,_ in enumerate(date_array):
    total_apts += date_array[i][1]

print('Appointments: ', total_apts)
print('assignments: ', len(assignmnets))

#Plot appointments vs days of semester
x = []
y = []

max_coeffs_x= []
max_coeffs_y= []
for i in assignmnets:
    max_coeffs_x.append(i.duedate)
    max_coeffs_y.append(i.max_coeff)

for i,_ in enumerate(date_array):
    x.append(date_array[i][0])
    y.append(date_array[i][1])

plt.plot(x,y)
plt.show()

# Export some contents to csv
with open('101_assignments.csv', 'w', newline='') as file:
    fnames = ['Instructor', 'Name', 'Points', r'% of final grade', 'Max Coeff', 'Due', 'Description']
    writer = csv.DictWriter(file, fieldnames=fnames)
    writer.writeheader()
    for a in assignmnets:
        if(a.description):
            soup = BeautifulSoup(a.description)
        writer.writerow({
        'Instructor': a.instructor,
        'Name': a.name,
        'Points': a.points,
        r'% of final grade': a.grade_percentage,
        'Due': a.duedate,
        'Max Coeff': a.max_coeff,
        'Description': soup.get_text().replace('\n\n\n', '\n')})

print('')
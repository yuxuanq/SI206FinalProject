## Your name: Yuxuan Qiu
## The option you've chosen: Option 3

# Put import statements you expect to need here!
import unittest
import json
import sqlite3
from bs4 import BeautifulSoup
import re
import requests


try:
    COURSE_CACHE_FNAME = "math.json"
    course_file = open(COURSE_CACHE_FNAME, 'r')
    content = course_file.read()
    course_file.close()
    course_content = json.loads(content)

except:
    print("IMPORTANT: See README file for instruction to run")

PEOPLE_CACHE_FNAME = "people.html"
try:
    people_file = open(PEOPLE_CACHE_FNAME, 'r')
    people_content = people_file.read()
    people_file.close()
except:
    url = 'https://lsa.umich.edu/math/people.html'
    people_content = requests.get(url).text
    people_file = open(PEOPLE_CACHE_FNAME, 'w')
    people_file.write(people_content)
    people_file.close()

SALARY_CACHE_FILE = "salary.html"
try:
    salary_file = open(SALARY_CACHE_FILE, 'r')
    salary_content = salary_file.read()
    salary_file.close()
except:
    base_url = "http://www.umsalary.info/deptsearch.php?Dept=LSA+Mathematics&Year=0&Campus=1"
    salary_file = open(SALARY_CACHE_FILE, 'w')
    salary_content = requests.get(base_url).text
    salary_file.write(salary_content)
    salary_file.close()

conn = sqlite3.connect('final_project.db')
cur = conn.cursor()


def get_course_info():
    course_info = []
    for course in course_content:
        course_num = re.findall(r'[0-9]+', course["course_name"])[0]
        sec = re.findall(r'Section [0-9]+ \([A-Z]+\)', course["sec"][0])[0]
        if len(course["instructor"]) > 0:
            name = course["instructor"][0]
            last_name = re.findall(r'[A-z]+\-*[A-z]*', name)[0]
            first_name = re.findall(r'[A-z]+\-*[A-z]*', name)[1]
            email = course["email"][0].lstrip("mailto:")
        else:
            last_name = ""
            first_name = ""
            email = ""
        full_name = first_name + " " + last_name
        course_tuple = (course_num + sec, first_name, last_name, full_name, email)
        course_info.append(course_tuple)
    return course_info


def create_course_table():
    cur.execute('DROP TABLE IF EXISTS Course')
    table_spec = 'CREATE TABLE IF NOT EXISTS '
    table_spec += 'Course (course TEXT PRIMARY KEY, first_name TEXT REFERENCES Salary(first_name), '
    table_spec += 'last_name TEXT REFERENCES Salary(last_name), full_name TEXT, email REFERENCES People(email) )'

    cur.execute(table_spec)
    for course in get_course_info():
        statement = 'INSERT INTO Course VALUES (?, ?, ?, ?, ?)'
        cur.execute(statement, course)
    conn.commit()


def get_salary_info():
    salary_info = []
    soup = BeautifulSoup(salary_content, "html.parser")
    content = BeautifulSoup(str(soup.find_all("table", {"class": "index"})), "html.parser")
    tr = content.find_all("tr")
    for people in tr:
        td = BeautifulSoup(str(people.find_all('a', {"href": "#"})), "html.parser").text
        if len(td) > 2:
            full_name_s = td.strip("[").strip("]")
            last_name_s = re.findall(r'[A-z]+\-*[A-z]*', full_name_s)[0]
            first_name_s = re.findall(r'\,[A-z]+\-*[A-z]*', full_name_s)[0].lstrip(",")
            salary_all = re.findall(r'\$\S+\$', people.text)
            salary = salary_all[0].rstrip("$").lstrip("$")
            salary_tuple = (full_name_s, first_name_s, last_name_s, salary)
            salary_info.append(salary_tuple)
    return salary_info


def create_salary_table():
    cur.execute('DROP TABLE IF EXISTS Salary')
    table_spec = 'CREATE TABLE IF NOT EXISTS '
    table_spec += 'Salary (full_name TEXT PRIMARY KEY, first_name TEXT, '
    table_spec += 'last_name TEXT, salary INTEGER)'
    cur.execute(table_spec)
    for salary in get_salary_info():
        statement = 'INSERT OR IGNORE INTO Salary VALUES (?, ?, ?, ?)'
        cur.execute(statement, salary)
    conn.commit()


def get_people_info():
    people_info = []
    soup = BeautifulSoup(people_content, "html.parser")
    content = soup.find_all('div', {"class": "person row"})
    for people in content:
        name = BeautifulSoup(str(people.find_all('a', {"class": "name themeText themeLink"})),
                             "html.parser").text.lstrip("[").rstrip("]")
        first_name = re.findall(r'[A-z]+', name)[0]
        last_name = re.findall(r'[A-z]+', name)[-1]
        mail = BeautifulSoup(str(people.find_all('span', {"class": "email"})), "html.parser").text.lstrip("[").rstrip(
            "]")
        title = BeautifulSoup(str(people.find_all('span', {"class": "title"})), "html.parser").text.lstrip("[").rstrip(
            "]")
        people_tuple = (mail.strip(), name, first_name, last_name, title)
        people_info.append(people_tuple)
    return people_info


def create_people_table():
    cur.execute('DROP TABLE IF EXISTS People')
    table_spec = 'CREATE TABLE IF NOT EXISTS '
    table_spec += 'People (email TEXT PRIMARY KEY, name TEXT, first_name TEXT, last_name TEXT,'
    table_spec += 'title TEXT)'
    cur.execute(table_spec)
    for people in get_people_info():
        statement = 'INSERT OR IGNORE INTO People VALUES (?, ?, ?, ?, ?)'
        cur.execute(statement, people)
    conn.commit()


create_people_table()
create_course_table()
create_salary_table()


class Course():
    department = "MATH"
    semester = "2017Fall"
    all_courses = get_course_info()

    def __init__(self, num):
        self.sections = {}
        for course in self.all_courses:
            if course[0][0:3] == str(num):
                section = course[0][3:]
                instructor = [course[3], course[4]]
                self.sections[section] = instructor

    def get_all_sec(self):
        return self.sections

    def get_all_instructor(self):
        instructors = []
        for sec in self.sections.keys():
            instructors.append(self.sections[sec][0])
        return instructors

    def get_total_sec(self):
        return len(list(self.sections.keys()))


query_inst_s = "SELECT Course.full_name, Course.email, Salary.salary FROM Course INNER JOIN Salary on Salary.last_name = Course.last_name"
cur.execute(query_inst_s)
inst_s = cur.fetchall()

query_inst_t = "SELECT People.name, People.title, People.email FROM People INNER JOIN Course on Course.email = People.email"
cur.execute(query_inst_t)
inst_t = cur.fetchall()


class Instructor():
    department = "MATH"

    def __init__(self, email):
        for inst in inst_t:
            if email == inst[2]:
                self.title = inst[1]
                self.name = inst[0]
                self.email = email

    def get_name(self):
        return self.name

    def get_title(self):
        return self.title

    def get_salary(self):
        for inst in inst_s:
            if self.email == inst[1]:
                return inst[2]

    def get_course(self):
        all_courses = get_course_info()
        courses = [i[0] for i in all_courses if i[-1] == self.email]
        return courses


def distinct_course_num():
    query = "SELECT DISTINCT course from Course"
    cur.execute(query)
    sections = cur.fetchall()
    nums = set([str(i[0])[0:3] for i in sections])
    return nums


def sort_salary():
    to_num = set([(i[0], int(str(i[-1][:-3]).replace(",", ""))) for i in inst_s])
    sorted_s = sorted(to_num, key=lambda salary: salary[1])
    return sorted_s


def more_than_15k(num = 150000):
    salary = [int(str(i[-1][:-3]).replace(",", "")) for i in inst_s]
    return len(list(filter(lambda salary: salary > num, salary)))


# Write your test ses here.
class CourseTest(unittest.TestCase):
    def test_sec1(self):
        math116 = Course(116)
        self.assertEqual(type(math116.get_all_sec()), type({}))

    def test_sec2(self):
        math571 = Course(571)
        self.assertEqual(len(math571.get_all_sec()), 1)

    def test_instructor(self):
        math575 = Course(575)
        self.assertEqual(type(math575.get_all_instructor()), type([]))

    def test_instructor2(self):
        math575 = Course(575)
        self.assertEqual(math575.get_all_instructor()[0], "Kartik Prasanna")

    def test_total_sec(self):
        math116 = Course(116)
        self.assertEqual(type(math116.get_total_sec()), type(1))

    def test_total_sec2(self):
        math116 = Course(116)
        self.assertEqual(math116.get_total_sec(), 41)


class InstructorTest(unittest.TestCase):
    def test_name(self):
        DeBacker = Instructor("smdbackr@umich.edu")
        self.assertEqual(DeBacker.get_name(), "Stephen DeBacker")

    def test_title(self):
        Keller = Instructor("ckell@umich.edu")
        self.assertEqual(Keller.get_title(), "Donald J. Lewis Research Post-Doctoral Assistant Professor")

    def test_course(self):
        Roman = Instructor("romanv@umich.edu")
        self.assertEqual(len(Roman.get_course()), 2)

    def test_salary(self):
        Roger = Instructor("rogernat@umich.edu")
        self.assertEqual(Roger.get_salary(), "100,724.57")


class other_func(unittest.TestCase):
    def test_distinct(self):
        self.assertEqual(type(distinct_course_num()), type(set()))

    def test_sort(self):
        self.assertEqual(sort_salary()[0] < sort_salary()[-1], True)

    def test_15k(self):
        self.assertEqual(more_than_15k(), 9)


unittest.main(verbosity=2)

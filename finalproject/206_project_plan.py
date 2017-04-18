## Your name: Yuxuan Qiu
## The option you've chosen: Option 3

# Put import statements you expect to need here!
import unittest
import json
import sqlite3
from bs4 import BeautifulSoup
import requests
import re
try:
    COURSE_CACHE_FNAME = "math.json"
    course_file = open(COURSE_CACHE_FNAME, 'r')
    content = course_file.read()
    course_file.close()
    course_content = json.loads(content)

except:
    print("Please excute the following command: scrapy crawl math -o math.json")

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
        course_num = re.findall(r'[0-9]+',course["course_name"])[0]
        sec = re.findall(r'Section [0-9]+ \([A-Z]+\)',course["sec"][0])[0]
        if len(course["instructor"]) > 0:
            name = course["instructor"][0]
            last_name = re.findall(r'[A-z]+\-*[A-z]*', name)[0]
            first_name = re.findall(r'[A-z]+\-*[A-z]*', name)[1]
            email = course["email"][0].lstrip("mailto:")
        else:
            last_name = ""
            first_name = ""
            email = ""
        full_name = first_name+" "+last_name
        course_tuple = (course_num+sec, first_name, last_name, full_name, email)
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

create_course_table()

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
create_salary_table()

def create_people_table():
    cur.execute('DROP TABLE IF EXISTS People')
    table_spec = 'CREATE TABLE IF NOT EXISTS '
    table_spec += 'People (email TEXT PRIMARY KEY, name TEXT, first_name TEXT, last_name TEXT,'
    table_spec += 'title TEXT)'
    cur.execute(table_spec)

    soup = BeautifulSoup(people_content, "html.parser")
    content = soup.find_all('div', {"class":"person row"})
    for people in content:
        name = BeautifulSoup(str(people.find_all('a', {"class":"name themeText themeLink"})),"html.parser").text.lstrip("[").rstrip("]")
        first_name = re.findall(r'[A-z]+', name)[0]
        last_name = re.findall(r'[A-z]+', name)[-1]
        mail = BeautifulSoup(str(people.find_all('span', {"class":"email"})),"html.parser").text.lstrip("[").rstrip("]")
        title = BeautifulSoup(str(people.find_all('span', {"class":"title"})),"html.parser").text.lstrip("[").rstrip("]")
        people_info = (mail, name, first_name, last_name, title)
        statement = 'INSERT OR IGNORE INTO People VALUES (?, ?, ?, ?, ?)'
        cur.execute(statement, people_info)
    conn.commit()
create_people_table()

class course():
    subject = "MATH"
    def __init__(self, num):

# # Write your test ses here.

# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 03:41:13 2020

@author: sapta
"""

import requests
from bs4 import BeautifulSoup
from splinter.browser import Browser
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


#from selenium import webdriver
#br = Browser('Firefox')
#driver = webdriver.Firefox()
centralDB = "https://easy.nic.in/civilListIAS/YrPrev/QryProcessCL.asp" #URL of database with all IAS officers listed
centralDB2 = 'https://easy.nic.in/civilListIAS/YrPrev/ListOfQueriesCL.htm' #Base URL where selections need to be made, routing through centralDB doesn't work
#driver.get(centralDB)

#driver = webdriver.Chrome(executable_path = 'C:/Users/sapta/Downloads/software/chromedriver_win32/chromedriver.exe')
#executable_path = {'executable_path':'C:/Users/sapta/Downloads/software/chromedriver_win32/chromedriver.exe'}
driver = webdriver.Firefox(executable_path = 'C:/Users/sapta/Downloads/software/geckodriver-v0.26.0-win64/geckodriver.exe')
#Firefox will be used hereon
# get web page
driver.get(centralDB2)
link = driver.find_element_by_link_text('Name')
link.click()
#make cadre and year selections
selectcadre = Select(driver.find_element_by_name("CboCadre"))
selectcadre.select_by_visible_text("AGMUT")

selectyear = Select(driver.find_element_by_name("CboBatch"))
selectyear.select_by_visible_text("1984")
#click submit and follow on - currently using xpath
submitlink = driver.find_element_by_xpath('/html/body/form/div/center/table/tbody/tr[7]/td/input[1]')
submitlink.click()

#results = driver.find_element_by_xpath("//a[@title='Click to view ER sheet']/@href")

#time.sleep(20)
#infolink = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td[2]/a')
#infolink.click()
#time.sleep(5)
#print()

'''
delay = 100 # seconds
try:
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, 'Photo')))
    print("Page is ready!")
finally:
    print("Loading took too much time!")

# execute script to scroll down the page
#driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
# sleep for 30s
#time.sleep(30)
# driver.quit()
'''

newDB = driver.page_source #THIS IS WHERE THINGS GO WRONG
#soup_alt = BeautifulSoup(newDB, "lxml")
html_content = requests.get(newDB).text #HTML SOURCE HAS WEIRD TAGS, NOT THE SAME AS requests(URL)
soup_alt = BeautifulSoup(html_content, 'lxml')
#driver.quit()
'''
#page_central = driver.page_source
#page_central = requests.get(centralDB).text
#soup_central = BeautifulSoup(page_central, 'lxml')
print(soup_central.prettify())
a = soup_central.find_all(True)
print(a)

a = soup_central.find(lambda tag: tag.name=='table' and tag.has_attr('border') and tag['border']=="1")
print(a)
b = a.find("table")
print(b)

URL = 'https://supremo.nic.in/ERSheetHtml.aspx?OffIDErhtml=14459&PageId='
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')
print(soup)

table1_body = soup.find_all('tbody')
print(table1_body)

result_1 = soup.find(id = 'one-column-emphasis')
print(result_1.prettify())
'''

########################
#Code for scraping once biodata sheet is obtained
URL = 'https://supremo.nic.in/ERSheetHtml.aspx?OffIDErhtml=14583&PageId='
html_content = requests.get(URL).text
soup_alt = BeautifulSoup(html_content, 'lxml')
print(soup_alt.prettify())

#print(soup.title) #prints title
#print(soup.title.text) #prints title text only

#head = soup_alt.contents[0].parent

#print(head.next)

#########################get introduction table
introtable = soup_alt.find("table", attrs = {"id": "one-column-emphasis"})
introtable_data = introtable.tbody.find_all("tr") #should extract all the rows
i=0
while(introtable_data[i].text != "None"):
    print(introtable_data[i].text)
    i+=1

for x in introtable_data: #seems to work
    col = x.find_all("td")
    for y in col:
        print(y.text) #perfectly extracts all the required introductory information

###############################################
        
####### details of central deputation
centraldep = soup_alt.find("table", attrs = {"id": "rounded-corner2"})
#extract all rows
centraldep_data = centraldep.find_all("tbody")
for x in centraldep_data:
    y = x.find_all("tr")
    for z in y:
        col = z.find_all("td")
        for i in col:
            print(i.text)
#####################################
            
#################large list of tables education + work ex + training 
all_tables = soup_alt.find_all("table", attrs = {"id" : "rounded-cornerA"})
#print(all_tables)
################education table
table_educ = all_tables[0]

#print(table_educ.text)
heading = table_educ.find_all("th") #stores the heading names
for i in heading: 
    print(i.text)
#extract education details under the headings
educ_details = table_educ.find("tbody")
educ_details = educ_details.find_all("tr")
for x in educ_details:
    col = x.find_all("td")
    for y in col:
        print(y.text)

#################

######################## experience table
table_exp = all_tables[1]
heading = table_exp.find_all("th") #stores all the heading names for experience
for i in heading:
    print(i.text)
exp_details = table_exp.find("tbody")
exp_details = exp_details.find_all("tr")
for x in exp_details: #all experience details
    col = x.find_all("td")
    for y in col:
        print(y.text)

###############################
        
############################### mid career training details
table_midcareer = all_tables[2]
heading = table_midcareer.find_all("th") #stores the heading names for mid career training details
for i in heading: 
    print(i.text)
mctraining_details = table_midcareer.find("tbody")
#print(mctraining_details)
mctraining_details = mctraining_details.find_all("tr")
for x in mctraining_details: #all experience details
    col = x.find_all("td")
    for y in col:
        print(y.text)
####################################
        
########################## in service training details 
table_inservice = all_tables[3]
heading = table_inservice.find_all("th") #stores the heading names for in service training details
for i in heading: 
    print(i.text)
istraining_details = table_inservice.find("tbody")    
istraining_details = istraining_details.find_all("tr")
#print(istraining_details)   
for x in istraining_details: #table content
    col = x.find_all("td")
    for y in col:
        print(y.text)
        
############################ domestic training details

table_domtraining = all_tables[4]
heading = table_domtraining.find_all("th") #stores the heading names for in service training details
for i in heading:
    print(i.text)
domtraining_details = table_domtraining.find("tbody")
domtraining_details = domtraining_details.find_all("tr")
#print(domtraining_details)
for x in domtraining_details: #table content
    col = x.find_all("td")
    for y in col:
        print(y.text)
##########################

######################### foreign training details

table_foreigntraining = all_tables[5]
heading = table_foreigntraining.find_all("th") #stores the heading names for foreign training details
for i in heading:
    print(i.text)
fortraining_details = table_foreigntraining.find("tbody")
fortraining_details = fortraining_details.find_all("tr")
#print(fortraining_details)
for x in fortraining_details: #table content
    col = x.find_all("td")
    for y in col:
        print(y.text)
####################################
        
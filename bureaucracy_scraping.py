#!/usr/bin/env python3
"""
Created on Sun Apr 26 03:41:13 2020

@author: sapta
"""

import requests
from bs4 import BeautifulSoup
#from splinter.browser import Browser
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import concurrent.futures

name = [] #1
id_no = [] #2
service_cadre_year = [] #2
gender = [] #6
exp_no = []
cadre_list = []
hrefs = []

exp_no_dict = {}
designation_dict = {}
dept_dict = {}
org_dict = {}
exp_dict = {}
period_dict = {}
name_dict = {} #1
service_cadre_year_dict = {} #2
gender_dict = {} #6
experience_details = {}
hrefs_dict = {}
hrefs_dict_backup = {}

def scrape(URL):
    exp_no.clear()
    html_content = requests.get(URL).text
    soup_alt = BeautifulSoup(html_content, 'lxml')
    #print(soup_alt.prettify())  
    #getting introtable
    introtable = soup_alt.find("table", attrs = {"id": "one-column-emphasis"})
    introtable_data = introtable.tbody.find_all("tr") #should extract all the rows
    i=0
    for x in introtable_data: #seems to work
        col = x.find_all("td")
        for index, i in enumerate(col):
            if(i.text == "Name : "):
                name.append(col[index+1].text)
            if(i.text == "Identity No. : "):
                id_no.append(col[index+1].text)
            if(i.text == "Service/ Cadre/ Allotment Year : "):
                service_cadre_year.append(col[index+1].text)
            if(i.text == "Gender : "):
                gender.append(col[index+1].text)
    name_dict[id_no[-1]] = name[-1]
    service_cadre_year_dict[id_no[-1]] = service_cadre_year[-1]
    gender_dict[id_no[-1]] = gender[-1]
    # so far: name, id_no _service_cadre_year and gender lists capture the respective entries
######################## experience table
# CODE OPTIMISATION NOTES
#1. DS - dictionary based, easier to merge when converting to DF 
    all_tables = soup_alt.find_all("table", attrs = {"id" : "rounded-cornerA"})
    table_exp = all_tables[1]
    exp_details = table_exp.find("tbody")
    exp_details = exp_details.find_all("tr")
    for x in exp_details: #all experience details
        col = x.find_all("td")
        exp_no.append(str(col[0].text))
        designation_dict[str(id_no[-1]) , str(col[0].text)] = col[1].text
        dept_dict[str(id_no[-1]) , str(col[0].text)] = col[2].text
        org_dict[str(id_no[-1]) , str(col[0].text)] = col[3].text
        exp_dict[str(id_no[-1]) , str(col[0].text)] = col[4].text
        period_dict[str(id_no[-1]) , str(col[0].text)] = col[5].text
    exp_no_dict[str(id_no[-1])] = list(exp_no)
# Only scraping experience and id-details here - rest of the script is commented further down if needed    


def create_df(dict_func, colname):
    base_df = pd.DataFrame.from_dict(dict_func, orient = "index").sort_index().stack().reset_index(level = 1, drop = True).reset_index()       
    base_df.columns = ["ID", str(colname)]
    return(base_df)

def create_tupledf(dict_func, colname):
    df = pd.Series(dict_func).rename_axis(["ID", "exp_no"]).reset_index(name = str(colname))
    return(df)
    
def scrape_URLlist(cadre_name):  
    driver = webdriver.Firefox(executable_path = 'C:/Users/sapta/Downloads/software/geckodriver-v0.26.0-win64/geckodriver.exe')
    driver.get(centralDB2)
    link = driver.find_element_by_link_text('Name')
    link.click()
    selectcadre = Select(driver.find_element_by_name("CboCadre"))
    selectcadre.select_by_visible_text(str(cadre_name.strip()))
    selectyear = Select(driver.find_element_by_name("CboBatch"))
    selectyear.select_by_visible_text("---All---")    
    submitlink = driver.find_element_by_xpath('/html/body/form/div/center/table/tbody/tr[7]/td/input[1]')
    submitlink.click()
    #so far, we click through to get list    
    time.sleep(60) #to allow page to fully load before getting source HTML
    #next steps - extract links of biodata pages
    newDB = driver.page_source
    soup_main = BeautifulSoup(newDB, "lxml")
    hrefs_dict[str(cadre_name)] = soup_main.find_all('a')
    driver.quit()
    print(f'scraped {cadre_name} state')
    return f'scraped {cadre_name} state'

    

#from selenium import webdriver
#br = Browser('Firefox')
#driver = webdriver.Firefox()
#centralDB = "https://easy.nic.in/civilListIAS/YrPrev/QryProcessCL.asp" #URL of database with all IAS officers listed
centralDB2 = 'https://easy.nic.in/civilListIAS/YrPrev/ListOfQueriesCL.htm' #Base URL where selections need to be made, routing through centralDB doesn't work
driver = webdriver.Firefox(executable_path = 'C:/Users/sapta/Downloads/software/geckodriver-v0.26.0-win64/geckodriver.exe')
driver.get(centralDB2)

link = driver.find_element_by_link_text('Name')
link.click()

intermediate_clickthrough = driver.page_source
soup_inter = BeautifulSoup(intermediate_clickthrough, "lxml")

#to select lists by cadre
options_all = soup_inter.find_all('option')

for i in options_all:
    if(i.text == "All Cadres"):
        continue
    if(i.text == "---All---"):
        break
    else:
        cadre_list.append(str(i.text).strip())
driver.quit()
# identify if hreps are valid links, and then send them to scrape function
for cadre_name in cadre_list:
    scrape_URLlist(cadre_name)
    
#hrefs_dict_backup = hrefs_dict

#valuelist = lambda x: x.
#map(valuelist, hrefs_dict.values())
#
#text_retriever = lambda x: x.attrs['href']
#hrefs = list(map(text_retriever, hrefs_list))
    
for key in hrefs_dict.keys():
    hrefs += hrefs_dict[key][2:-2]

link_retriever = lambda x: x.attrs['href']
hrefs = list(map(link_retriever, hrefs))

with concurrent.futures.ThreadPoolExecutor() as executor:
    interlist = executor.map(scrape, hrefs)
    results = []
    for i in concurrent.futures.as_completed(interlist):
        results.append(i)

base_df = create_df(name_dict, "Name") 
cadre_df = create_df(service_cadre_year_dict, "Cadre")
gender_df = create_df(gender_dict, "Gender")
exp_key_df = create_df(exp_no_dict, "exp_no")

designation_df = create_tupledf(designation_dict, "Designation")
dept_df = create_tupledf(dept_dict, "Department")
org_df = create_tupledf(org_dict, "Organisation")
div_df = create_tupledf(exp_dict, "Division")
period_df = create_tupledf(period_dict, "Period")


#merges dataframes to give final result
dflist = [cadre_df, gender_df, exp_key_df]
final_df = base_df
for i in dflist:
    final_df = pd.merge(final_df, i, on = "ID")

tuple_dflist = [designation_df, dept_df, org_df, div_df, period_df]
for i in tuple_dflist:
    final_df = pd.merge(final_df, i, on = ["ID", "exp_no"])

final_df.to_csv(r'C:/Users/sapta/OneDrive/Desktop/Documents/codes/bureaucrat_scraping/IASexecutiverecords.csv', encoding = 'utf-8')













###################
###   CODE ROUGHWORK 
##################
'''

########################
#Code for scraping once biodata sheet is obtained
#URL = 'https://supremo.nic.in/ERSheetHtml.aspx?OffIDErhtml=14583&PageId='
#html_content = requests.get(URL).text
#soup_alt = BeautifulSoup(html_content, 'lxml')
#print(soup_alt.prettify())

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
        
'''
        

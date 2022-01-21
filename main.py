import requests
from bs4 import BeautifulSoup
import csv
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
# import time
from pytz import timezone 
import base64
from github import Github
from github import InputGitTreeElement
import os
os.system('pip install -r requirements.txt')

# while True:
def fun():
  try:
    print("\nAPI Task Execution Started\n")
    print(datetime.datetime.now(timezone("Asia/Kolkata")).strftime("%A, %d. %B %Y %I:%M:%S%p"))
    url= r"https://www.worldometers.info/coronavirus/"

    response = requests.get(url)
    html_page = response.text

    soup = BeautifulSoup(html_page, 'html.parser')
    #find <table>
    tables = soup.find_all("table")
    print(f"Total {len(tables)} Table(s)Found on page {url}")

    for index, table in enumerate(tables):
        # print(f"\n-----------------------Table{index+1}-----------------------------------------\n")
        
        #find <tr>
        table_rows = table.find_all("tr")

        #open csv file in write mode
        with open(f"Table{index+1}.csv", "w", newline="") as file:

            #initialize csv writer object
            writer = csv.writer(file)

            for row in table_rows:
                row_data= []

                #<th> data
                if row.find_all("th"):
                    table_headings = row.find_all("th")
                    for th in table_headings:
                        row_data.append(th.text.strip())
                #<td> data
                else:
                    table_data = row.find_all("td")
                    for td in table_data:
                        row_data.append(td.text.strip())
                #write data in csv file
                writer.writerow(row_data)

                # print(",".join(row_data))
        # print("--------------------------------------------------------\n")
    # time.sleep()
    print(datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M:%S%p"))
    token = os.environ['token']
    g = Github(token)
    repo = g.get_user().get_repo('Worldometer-Covid-Data-API') # repo name
    file_list = [
        'Table1.csv',
        'Table2.csv',
        'Table3.csv'
    ]
    file_names = [
        'Table1.csv',
        'Table2.csv',
        'Table3.csv'
    ]
    commit_message = 'auto commit'
    master_ref = repo.get_git_ref('heads/main')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)

    element_list = list()
    for i, entry in enumerate(file_list):
        with open(entry) as input_file:
            data = input_file.read()
        if entry.endswith('.png'): # images must be encoded
            data = base64.b64encode(data)
        element = InputGitTreeElement(file_names[i], '100644', 'blob', data)
        element_list.append(element)

    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)
    print("\nAPI Task Execution Ended\n")
  except Exception as e:
    print(e)

scheduler = BlockingScheduler(timezone='Asia/Kolkata')
scheduler.add_job(fun, "interval", hours=6)
print("====================== Starting API ===============================")
scheduler.start()
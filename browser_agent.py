from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from io import StringIO
import time
import json


'''TEST VARIABLES
employer_info = [{"company": "ADVANTAGE, powered by JMFA", "industry": ["Finance", "Financial Services"]}, 
                {"company": "Army Medical", "industry": [""]},
                {"company": "Baylor College of Medicine", "industry": ["Other"]}
                ] 

employer_pages = [{"url": "https://nsm-uh-csm.symplicity.com/events/cbf740da9548efa0b72f80dd5e384a4a/employers/f6eff2042f5df2963b8182292ae06935", "id": "f6eff2042f5df2963b8182292ae06935"}, 
         {"url":"https://nsm-uh-csm.symplicity.com/events/cbf740da9548efa0b72f80dd5e384a4a/employers/69957ef711b577a7b2345afca74af505", "id": "69957ef711b577a7b2345afca74af505"}, 
         {"url": "https://nsm-uh-csm.symplicity.com/events/cbf740da9548efa0b72f80dd5e384a4a/employers/5118d820ec80600f2d9611044dfd1ded", "id": "5118d820ec80600f2d9611044dfd1ded"}]
'''


# Setup Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

career_fair_url = "https://nsm-uh-csm.symplicity.com/events/cbf740da9548efa0b72f80dd5e384a4a/employers"

# Open the career fair page
driver.get(career_fair_url)


# wait for employer list selector is rendered
try:
    company_elements = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.lst-rpp label > select"))
) 
except Exception as e: 
    print(f"Error loading all companies selector {e}")
    driver.quit()

# find the selector to show all employers and select it
employer_list_selector = driver.find_element(By.CSS_SELECTOR, "span.lst-rpp label > select")
show_all_employers_btn = Select(employer_list_selector)
show_all_employers_btn.select_by_value("250")
time.sleep(1.5)

employers_pages = [] # employers page links on college listing
employer_info = [] # employers data

# # loop through websites api requests
for req in driver.requests:
    if not req.response:
        continue
    # requests for employers data
    if "registrations?page=1&perPage=250" in req.url:
        body = req.response.body
        text = body.decode("utf-8")
        data = json.loads(text)

        # loop through each employers data
        for employer_data in data["models"]:
            employers_pages.append({"url": f"https://nsm-uh-csm.symplicity.com/events/cbf740da9548efa0b72f80dd5e384a4a/employers/{employer_data["registration_id"]}", "id": employer_data["registration_id"]})
            employer_info.append({"company": employer_data["name"], "industry": [ind["_label"] for ind in employer_data["industry"]]})
        break

for idx, employer in enumerate(employers_pages):
    driver.requests.clear()  # Clear previous requests
    driver.get(employer["url"])
    time.sleep(2)
    try:
        company_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "cf-event-attending-employer-view div.list-item.list_rows"))
    ) 
    except Exception as e: 
        print(f"Error loading all companies selector: {e}")
        driver.quit()
    try:
        # loop through each request on the current page
        for req in driver.requests:   

            if not req.response:  
                continue

            content_type = req.response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                continue
            
            # look for request with employer registration id in it
            if employer["id"] in req.url:
                body = req.response.body
                text = body.decode("utf-8")
                data = json.loads(text)

                employer_info[idx].update({"overview": data["overview"], "website": data["website"], 
                             "majors": [major for major in data["majors"]], 
                             "work_authorization": [auth for auth in data["work_authorization"]], 
                             "degree": [degree for degree in data["degree_level"]], 
                             "positions": [pos for pos in data["position_types"]]  })

                break
        
    except Exception as e:
        print(f"Error getting employer data: {e}")

print(f"{len(employer_info)} employers")
time.sleep(5)

# convert employer data into JSON string
json_str = json.dumps(employer_info)
# pandas converts it into a dataframe
df = pd.read_json(StringIO(json_str))

# list out the list values and separate with semicolon
df = df.map(lambda x: "; ".join(x) if isinstance(x, list) else x)

# converts dataframe to a csv file
df.to_csv("output.csv", index=False, encoding="utf-8")
print("CSV created successfully")

driver.quit()

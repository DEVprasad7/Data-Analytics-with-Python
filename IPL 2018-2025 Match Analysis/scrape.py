from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

website = "https://www.espncricinfo.com/ci/engine/series/index.html?search=ipl;season=2018;view=season"

options = Options()

# Suppress unnecessary logs
options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get(website)

c = input("Press Enter To Start.......")

print("Scraping Started...")

containers = driver.find_elements(by="xpath", value='//section[@class="matches-day-block"]/section')


# date = //section[@class="matches-day-block"]/section/div[@class="match-info"]/span[@class="bold"]
# link = //section[@class="matches-day-block"]/section/div[@class="match-info"]/span[@class="match-no"]/a
# first_inn_team = //section[@class="matches-day-block"]/section/div[@class="innings-info-1"]
# first_inn_sc = //section[@class="matches-day-block"]/section/div[@class="innings-info-1"]/span
# second_inn_team = //section[@class="matches-day-block"]/section/div[@class="innings-info-2"]
# second_inn_sc = //section[@class="matches-day-block"]/section/div[@class="innings-info-2"]/span
# match_result = //section[@class="matches-day-block"]/section/div[@class="match-status"]/span

match_dates = []
match_links = []
first_inn_teams = []
first_inn_scs = []
second_inn_teams = []
second_inn_scs = []
match_results = []

patch = 1
for container in containers:
    print(f"Scraping Data Patch {patch}...")
    match_date = container.find_element(by="xpath", value='./div[@class="match-info"]/span[@class="bold"]').text
    match_link = container.find_element(by="xpath", value='./div[@class="match-info"]/span[@class="match-no"]/a').get_attribute("href")
    first_inn_team = container.find_element(by="xpath", value='./div[@class="innings-info-1"]').text
    first_inn_sc = container.find_element(by="xpath", value='./div[@class="innings-info-1"]/span').text
    second_inn_team = container.find_element(by="xpath", value='./div[@class="innings-info-2"]').text
    second_inn_sc = container.find_element(by="xpath", value='./div[@class="innings-info-2"]/span').text
    match_result = container.find_element(by="xpath", value='./div[@class="match-status"]/span').text
    
    match_dates.append(match_date)
    match_links.append(match_link)
    first_inn_teams.append(first_inn_team)
    first_inn_scs.append(first_inn_sc)
    second_inn_teams.append(second_inn_team)
    second_inn_scs.append(second_inn_sc)
    match_results.append(match_result)
    print(f"Data Patch {patch} Scraped.")
    patch += 1


print("Scraping Completed.")
print("Creating CSV File...")

my_dict = {
    'match_date': match_dates,
    'match_link': match_links,
    'first_inn_team': first_inn_teams,
    'first_inn_score': first_inn_scs,
    'second_inn_team': second_inn_teams,
    'second_inn_score': second_inn_scs,
    'match_result': match_results
}

df = pd.DataFrame(my_dict)
df.to_csv('ipl_2018.csv')
print("CSV File Created.")

input("Press Enter to close browser...")
driver.quit()

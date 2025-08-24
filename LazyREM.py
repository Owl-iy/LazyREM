from tkinter import *
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium import webdriver
import undetected_chromedriver as uc
import time
from malwarebazaar import Bazaar
import re
import os
import sys
import threading
MALWARE_BAZAAR_KEY = "YOURKEYHERE"

#TODO
#  1. Windows portable executable (.EXE)
# 2. GUI
# 3. User enters a string of alphanumeric characters into a field
# 4. Upon hitting the ENTER key or a button labeled "Search" it will perform the following actions:
# a. perform a Google search for the string
# b. return links to intelligence reports in a field
# c. scrape the page for SHA-256 hashes
# d. upon finding SHA-256 hashes, query MalwareBazaar (https://bazaar.abuse.ch/browse/)
# e. return links to malware samples in a field 
# f. display a button to save the results to a file
# i. defaults to the ~/Downloads fold

#chrome Profile Setup
chrome_options = Options()
# chrome_options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
# search_query = "pokemon"
# if __name__ == '__main__':
#     driver = uc.Chrome(headless=False,use_subprocess=False)

#     # #Input the keys to search the inputs up


#     driver.get(f"https://www.google.com/search?q={search_query}")
#     time.sleep(3)
#     page_html = driver.page_source

#     soup = BeautifulSoup(page_html,'html.parser')
#     obj={}
#     links=[]
#     driver.save_screenshot('test2.png')
#     allData = soup.find("div",{"class":"dURPMd"}).find_all("div",{"class":"Ww4FFb"})
#     print(len(allData))
#     driver.save_screenshot('test.png')
#     for i in range(0,len(allData)):
#         #Object is a dictionary and title is the section


#         try:
#             obj["link"]=allData[i].find("a").get('href')
#         except:
#             obj["link"]=None
#     #Adding the link to the links object
#         links.append(obj)
#         #Clearing the object
#         obj={}

#     # df = pd.DataFrame(links)
#     # df.to_csv('google.csv', index=False, encoding='utf-8')

#     print(links)

#     driver.quit()
def log_error(message):
    with open("error_log.txt", "a") as f:
        f.write(f"{message}\n")

def Button_search():
    # Start background thread for actual search work
    threading.Thread(target=_search_worker, daemon=True).start()

def _search_worker():
    try:
        print("Launching Chrome (primary driver)...")
        driver = uc.Chrome(headless=False, use_subprocess=False)
        print("Chrome launched successfully")

        search_query = input.get('1.0', 'end').strip()
        print(f"Search query obtained: '{search_query}'")
        driver.get(f"https://www.google.com/search?q={search_query}")
        input.delete('1.0', 'end')
        time.sleep(2)  # wait for page to load

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')

        container = soup.find("div", {"class": "dURPMd"})
        allData = container.find_all("div", {"class": "Ww4FFb"}) if container else []
        numberOfLinks = len(allData)
        print(f"Found {numberOfLinks} links in Google results")

        links = []
        for i, item in enumerate(allData):
            try:
                link = item.find("a").get('href')
            except Exception as e:
                print(f"Error extracting link #{i}: {e}")
                log_error(f"Error extracting link #{i}: {e}")
                link = None
            links.append(link)

        driver.quit()
        print("Primary Chrome driver quit successfully")

        # Insert number of links into output_links safely from main thread
        output_links.after(0, lambda: output_links.insert('end', f"{numberOfLinks} Links have been Generated:\n"))

        for url in links:
            if not url:
                output_links.after(0, lambda: output_links.insert('end', "No link found in one of the results\n"))
                continue

            print(f"Processing link: {url}")
            try:
                seconddriver = uc.Chrome( headless=False, use_subprocess=False)
                seconddriver.get(url)
                time.sleep(2)
                element = seconddriver.find_element(By.TAG_NAME, "body")
                text_content = element.text
                pattern = r"\b[a-fA-F0-9]{64}\b"
                matches = re.findall(pattern, text_content)

                if not matches:
                    mblinks.after(0, lambda: mblinks.insert('end', f"No SHA-256 matches found on the website,\n {url} \n\n"))

                for match in matches:
                    print(f"Found SHA-256 hash: {match}, from :{url}")
                    try:
                        b = Bazaar(api_key=MALWARE_BAZAAR_KEY)
                        response = b.query_hash(match)
                        mallinks = response['data'][0]['file_information'][0]['value']

                        def insert_mblinks():
                            mblinks.insert('end', f"Found Sha-256 hash:\n {mallinks}\n from: {url}\n\n")
                            mblinks.update_idletasks()

                        mblinks.after(0, insert_mblinks)
                        print(f"MalwareBazaar link: {mallinks}")
                    except Exception as e_mb:
                        print(f"Error querying MalwareBazaar for hash {match}: {e_mb}")
                        log_error(f"Error querying MalwareBazaar for hash {match}: {e_mb}")

                seconddriver.quit()
                print("Secondary Chrome driver quit successfully")

            except Exception as e_link:
                print(f"Error processing link {url}: {e_link}")
                log_error(f"Error processing link {url}: {e_link}")
                try:
                    seconddriver.quit()
                except:
                    pass

            output_links.after(0, lambda url=url: output_links.insert('end', f"{url}\n\n"))

    except Exception as e:
        print(f"Fatal error in search worker: {e}")
        log_error(f"Fatal error in search worker: {e}")
        
        
            
    
def clear_output():
    output_links.delete('1.0', END)    



def save_button():
    
    downloads_folder_os = os.path.join(os.path.expanduser("~"), "Downloads")
    output_file_path = os.path.join(downloads_folder_os, 'outputlinks.txt')
    malbazlinks = mblinks.get('1.0', END)
    with open(output_file_path, 'w') as f:
            f.write(f"{malbazlinks}\n")
   

   
if __name__ == '__main__':
        import multiprocessing
        multiprocessing.freeze_support()
        try:

            #TODO MAKe it so the input gets searched by google and then the top 10 link are printed in a field below
            #TODO ADd a clear button to both boxes

                window = Tk()
                window.minsize(1400, 900)
                

                #Text inputs

                input = Text(height = 10, width=50)
                input.place(x=525, y=100)

                #Output for Links Box

                output_links = Text(height=20, width=60)
                output_links.place(x=150, y=500)


                #Clear output links button

                clear = Button(height= 1, width= 20, text="Clear Output", command=clear_output)
                clear.place(x=330, y=450)


                # Search Button

                search = Button(height = 1, width = 20, text = "Search", command=Button_search)
                search.place(x=639 , y=300)

                #Output Malbazaar links

                mblinks = Text(height=20, width= 60)
                mblinks.place(x=787, y=500)

                # Saving the malbazzar links button

                save = Button(height=1, width=20, text="Save", command=save_button)
                save.place(x=950, y=450)

                window.mainloop()
        except Exception as e:
            log_error(f"Fatal error in main: {e}")
        

# b = Bazaar(api_key = MALWARE_BAZAAR_KEY)
# response = b.query_hash("17df6d8f63eed3a7a46dd13c8e87c748a2b31c0838125f6582d2792b4139eac4")
# print(response['data'][0]['file_information'][0]['value'])
# count = 0 
# if testing == True:
#     if __name__ == "__main__":
#         seconddriver = uc.Chrome(headless=False, use_subprocess=False)
#         seconddriver.get("https://osintteam.blog/repeat-offenders-lummastealer-malware-analysis-8335683eaa0c")
#         time.sleep(2)
#         element = seconddriver.find_element(By.TAG_NAME, "body")
#         text_content = element.text
#         pattern = r"\b[a-fA-F0-9]{64}\b"

#         matches = re.findall(pattern, text_content)
#         count = len(matches)

#         print(f"{count} SHA-256 hash(es) found:")
#         for match in matches:
#             print(match)
        
#         seconddriver.close()



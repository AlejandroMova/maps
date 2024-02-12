import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import csv
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

driver = webdriver.Chrome()



def wait_for_element(time, by, key): 
    # wait for an element
    wait_for = WebDriverWait(driver, time).until(
        EC.presence_of_element_located((by, key))
    )

    return wait_for

def scroll_down(amount): 
    # Scroll down the responses that maps gives
    frame = wait_for_element(10, By.CLASS_NAME, "tTVLSc")

    scroll_origin = ScrollOrigin.from_element(frame)

    ActionChains(driver).scroll_from_origin(scroll_origin, 0, amount).perform()


def searchbar(search): 
    # Use the google maps searchbar
    searchbar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div[8]/div[3]/div[1]/div[1]/div/div[2]/form/input"))
    )

    searchbar.send_keys(search)
    searchbar.send_keys(Keys.RETURN)

def get_places(query):
    # get the google maps places, returned in a dict with key name and value list of attributes
    
    driver.get('https://www.google.com/maps/')
    # query is what to search for
    places = []

    try: 
        
        searchbar(query)
        # wait for cards to appear
        wait_for_element(10, By.CLASS_NAME, "hfpxzc")

        # scroll to generate more responses
        for i in range(5): 
            scroll_down(10000)
            time.sleep(1)

        # get the google maps responses
        cards = (driver.find_elements(By.CLASS_NAME, "hfpxzc"))
        names = []
        links = []
        for card in cards:
            names.append(card.get_attribute('aria-label'))
            links.append(card.get_attribute('href'))
        for i in range(len(links)):
            # get information of each card

            if i > 3: 
                break
            # open new window
            try: 
                driver.execute_script('window.open('');')
                driver.switch_to.window(driver.window_handles[i])
                driver.get(links[i])
                location = driver.find_element(By.CLASS_NAME, 'Io6YTe').text
                closes = driver.find_element(By.CLASS_NAME, "ZDu9vd").text
                places.append({'name': names[i], 'link': links[i], 'location': location, 'closes': closes})
            except Exception as e: 
                print('Element not found')
                continue

        driver.quit()

        
    except Exception as e: 
        print(e)

    return places


@app.get('/{query}')
def get_query(query: str): 
    # to run the program
    
    print('Searching ', query)
    titles = ["name", "link", "location", "closes"]

    places = get_places(query)

    
    with open(f'{query}.csv', 'w', encoding='UTF-8') as f: 
        writer = csv.DictWriter(f, fieldnames=titles)
        writer.writeheader()
        
        for place in places: 
            try: 
                writer.writerow(place)
            except UnicodeEncodeError as e: 
                print('Character not recognized')
                continue
    
    return FileResponse(f'{query}.csv')

if __name__ == "__main__": 
    uvicorn.run(app, port=8000, host="0.0.0.0")


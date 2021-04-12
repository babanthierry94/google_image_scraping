import os
import time
import requests
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, ElementClickInterceptedException
from glob import glob
import csv

def download_from_google(search_terms_list, output_path: str, max_number_of_images: int):
    # Get terms already recorded.
    dirs = glob(output_path + "*")
    dirs = [dir.split("/")[-1].replace("_", " ") for dir in dirs]
    # Exclude terms already stored.
    search_terms = [term for term in search_terms_list if term not in dirs]

    for term in search_terms:
        search_and_download(term, output_path, max_number_of_images)


def search_and_download(query: str, target_path: str, max_number_images: int):

    count = 0
    max = max_number_images
    download_results = []
    download_results.append(["No", "URL", "Status"])

    target_folder = os.path.join(target_path, "_".join(query.lower().split(" ")))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    wd = webdriver.Chrome()
    search_url = "https://www.google.com/search?q={q}&ijn=0&start=0&tbs=&tbm=isch"
    # load the page
    wd.get(search_url.format(q=query))

    #Scroll and charge the entire page
    for __ in range(10):
        # multiple scrolls needed to show all 400 images
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # to load next 400 images
        #wd.find_element_by_class_name("mye4qd")
        button_more =  wd.find_element_by_css_selector("input.mye4qd")
        wd.execute_script("document.querySelector('.mye4qd').click();")

    #search all images thumbmails
    elements = wd.find_elements_by_css_selector("img.rg_i.Q4LuWd")

    if max > len(elements):
        max = len(elements)
        print("max = ", max)

    # if max==0 then we download all the images of the page
    if max == 0:
        max = len(elements)

    while count <= max:
        #Click on the image thumbmail
        try :
            elements[count].click()
            count += 1
            print(count)
            time.sleep(10)
        except ElementClickInterceptedException as e:
            print(format(e))
            pass

        try:
            src = wd.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div/div[2]/a/img').get_attribute('src')
            print(src)

            #Download the image
            reponse = requests.get(src)
            download_result = "False"
            if reponse.status_code == 200:
                with open(target_folder + f"/{count}.jpg", "wb") as file:
                    file.write(reponse.content)
                    download_result = "True"
                    print("success for file:", count)

            download_results.append([count, src, download_result])
        except:
            pass



    with open(output_path + "/Log_csv_files/log_" + "_".join(query.lower().split(" "))+".csv", 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(download_results)

    wd.quit()


# Max images = 0 to download all images
max_images = 10
# Change to your suitable folder path
output_path = "C:/Users/BABAN/Desktop/MyFoodDataset"
search_terms = [
    "Okok",
    "Okok cameroun",
    "Okok food",
    "Taro sauce jaune",
    "Achu yellow soup",
    "Eru cameroun",
    "Eru cameroon",
    "Eru food",
    "Eru water fufu"
    "Eru nourriture",
    "Sauce gombo",
    "Okra soup",
    "Koki cameroun",
    "Koki cameroon",
    "Koki food",
    "Koki nourriture",
    "Ekwang",
    "Ekwang food",
    "Ekwang cameroon",
    "Corn chaff",
    "Corn tchap"
]
download_from_google(search_terms, output_path, max_images)

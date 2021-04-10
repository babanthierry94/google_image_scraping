import os
import time
import requests
import re
import base64
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, ElementClickInterceptedException
from glob import glob


def download_from_google(search_terms_list, output_path: str, max_number_of_images: int):
    # Get terms already recorded.
    dirs = glob(output_path + "*")
    dirs = [dir.split("/")[-1].replace("_", " ") for dir in dirs]
    # Exclude terms already stored.
    search_terms = [term for term in search_terms_list if term not in dirs]

    for term in search_terms:
        search_and_download(term, output_path, max_number_of_images)


def search_and_download(query: str, target_path: str, max_number_images: int):

    #images_urls = []
    #images_base64 = []
    count = 0
    max = max_number_images

    target_folder = os.path.join(target_path, "_".join(query.lower().split(" ")))
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    wd = webdriver.Chrome()
    #search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    search_url = "https://www.google.com/search?q={q}&ijn=0&start=0&tbs=&tbm=isch"
    # load the page
    wd.get(search_url.format(q=query))

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

        #find image
        actual_image = wd.find_element_by_css_selector("img.n3VNCb")
        actual_image_src = actual_image.get_attribute("src")

        if find_url(actual_image_src):
            # images_urls.append(actual_image_src)
            # write image to file
            reponse = requests.get(actual_image_src)
            if reponse.status_code == 200:
                with open(target_folder + f"/{count}.jpg", "wb") as file:
                    file.write(reponse.content)
                print("Image HTTP downloaded")
        else:
            # images_base64.append(actual_image_src)
            # write image to file
            # Separate the metadata from the image data
            head, data = actual_image_src.split(',', 1)
            # Get the file extension (gif, jpeg, png)
            file_ext = head.split(';')[0].split('/')[1]
            imgdata = base64.b64decode(data)
            filename = 'some_image.jpg'  # I assume you have a way of picking unique filenames
            with open(target_folder + f"/{count}."+file_ext, "wb") as file:
                file.write(imgdata)

            print("Image BASE64 downloaded")

    wd.quit()


def find_url(string):
    # search() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.search(regex, string)
    return url


max_images = 100
output_path = "User_path"
search_terms = [
    "pilé haricot cameroun"
]
download_from_google(search_terms, output_path, max_images)


# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import csv
import pandas as pd

import urllib.request
#def save_images(count, image):

comments_row = []

def save_comments(driver, pre_path, pre_pages, page):

    # Fetch the comments and write them to local files one by one.
    #num_comment = 0

    # click the "unfold" to fetch all content if the comment is too long

    print("Unfolding all comments!")
    unfold_btns = driver.find_elements_by_xpath("//div/p/a[@action-type='fl_unfold']")
    for unfold_btn in unfold_btns:
        unfold_btn.click()
        sleep(3)   # if click too fast, some may not work
    if len(unfold_btns) != 0 and len(unfold_btns) != len(driver.find_elements_by_xpath("//a[@action-type='fl_fold']")):  # test if all the comments were unfold!
	    print(len(unfold_btns))
	    print(len(driver.find_elements_by_xpath("//a[@action-type='fl_fold']")))
	    quit("Some comments were unfolded!")


    # End

    print("Writing comments to local files!")
    main_post = driver.find_elements_by_xpath("//div[@class='feed_content wbcon']")
    dates = driver.find_elements_by_xpath("//div[@class='feed_from W_textb']/a[@class='W_textb'][last()]")
    phones = driver.find_elements_by_xpath("//div[@class='feed_from W_textb']/a[2][last()]")

    share_cnts = driver.find_elements_by_xpath("//ul[@class='feed_action_info feed_action_row4']/li[2]/a/span/em")
    comment_cnts = driver.find_elements_by_xpath("//ul[@class='feed_action_info feed_action_row4']/li[3]/a/span/em")
    like_cnts = driver.find_elements_by_xpath("//ul[@class='feed_action_info feed_action_row4']/li[4]/a/span/em")

    for i in range(len(main_post)):
        #path = pre_path + "/" + str(pre_pages + i + 1) + ".txt"
        #file = open(path, "w+", encoding = "utf-8")
        #file.write(comments[i].text)
        #file.close()
        name = main_post[i].find_elements_by_tag_name("a")[0].get_attribute('nick-name')
        print(name)
        #print(names_list[i].get_attribute('nick-name'))
        try:
            #images = images_list[i].find_elements_by_tag_name("li")
            images = main_post[i].find_elements_by_tag_name("div")[0].find_elements_by_tag_name("div")[0].find_elements_by_tag_name("li")
            for ci, image in enumerate(images):
                image_url = image.find_elements_by_tag_name("img")[0].get_attribute("src")
                print(image_url)
                urllib.request.urlretrieve(image_url, "images/pg" + str(page+1) + "pst" + str(i) + "pic"+ str(ci) +".jpg")
        except Exception as e:
            print(str(e))
            #print("Could Not find Image")
        post = main_post[i].find_elements_by_tag_name("p")[0].text
        print(post)
        try:
            date = dates[i].text
            print(date)
        except:
            print("Could Not match date")
        try:
            phone = phones[i].text
            print(phone)
        except:
            print("Could Not find phone")
        try:
            share_cnt = share_cnts[i].text
            print(share_cnt)
        except:
            print("NaN")
        try:
            comment_cnt = comment_cnts[i].text
            print(comment_cnt)
        except:
            print("NaN")
        try:
            like_cnt = like_cnts[i].text
            print(like_cnt)
        except:
            print("NaN")
        #print(images[i])
        comments_row.append([name, post, date, phone, share_cnt, comment_cnt, like_cnt])

    return(pre_pages + len(main_post))

def fetch_userinfo(driver, pre_path):

    # Fetch user info

    print("Fetching userinfo!")

    # Fetch user nick name

    names = []
    name_nodes = driver.find_elements_by_xpath("//div[@class='feed_content wbcon']/a[@class='W_texta W_fb']")
    for name_node in name_nodes:
        names.append(name_node.text)

    # Fetch weibo approved type

    approves = []
    approve_nodes_parents = driver.find_elements_by_xpath("//div[@class='feed_content wbcon']")
    for approve_node_parent in approve_nodes_parents:
        try:
            approve_node = approve_node_parent.find_element_by_xpath("./a[2]")
            approve = approve_node.get_attribute("title").replace(" ", "")
        except NoSuchElementException:
            approve = ""
        approves.append(approve)

    # Fetch published date

    dates = []
    date_nodes = driver.find_elements_by_xpath("//div[@class='content clearfix']/div[@class='feed_from W_textb'][1]/a[@class='W_textb']")
    for date_node in date_nodes:
        date = date_node.get_attribute("title")[0:10]
        dates.append(date)

    # Fetch platform

    platforms = []
    platform_node_parents = driver.find_elements_by_xpath("//div[@class='content clearfix']")
    for platform_node_parent in platform_node_parents:
        try:
            platform_node = platform_node_parent.find_element_by_xpath("./div[@class='feed_from W_textb'][1]/a[2]")
            platform = platform_node.text
        except NoSuchElementException:
            platform = ""
        platforms.append(platform)

    # End

    print("Writing userinfo to local file!")
    info = [names, approves, dates, platforms]
    path = pre_path + "/records.csv"
    with open(path, "a+", newline = "", encoding = "utf-8") as csvfile:
        info_writer = csv.writer(csvfile)
        info_writer.writerows(info)
    csvfile.closed


# Open a web page

# Login to weibo in firefox, search with some key words and copy the url.

url = "http://s.weibo.com/weibo/%25E6%25B8%2585%25E8%25BF%2588&Refer=STopic_box"
fp = webdriver.FirefoxProfile("C:/Users/philanderz/AppData/Roaming/Mozilla/Firefox/Profiles/fc152m46.default")  # This is the firefox profile in my computer, type in yours.
browser = webdriver.Firefox(fp)
browser.get(url)
main_window = browser.current_window_handle
#assert "Python" in browser.title
print("Wetsite opened!")

# End

pages = 10 # Number of pages you get from the search result.
pre_path = "D:/GitHub/ICDI Project/web-scraping-restaurants/output/"
fetched_pages = 0
for page in range(pages):

    # wait a few seconds

    sleep(8)

    # wait until the "next page" button present except the last page

    if page + 1 < pages:
        print("Fetching")
        try:
            next_page = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, "//a[@class='page next S_txt1 S_line1']")))
            print("Page " + str(page + 1) + " opened successfully!")
        except TimeoutException:
            print("Page loading time out!")
            break
    else:
        try:
            page_list = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, "//span[@class='list']/a[@class='page S_txt1']")))
            print("Page " + str(page + 1) + " opened successfully!")
        except TimeoutException:
            print("Page loading time out!")
            break

    fetched_pages = save_comments(browser, pre_path, fetched_pages, page)
    fetch_userinfo(browser, pre_path)

    # click the "next page" button except the last page

    if page + 1 < pages:
        next_page.click()
        print("Directing to next page!")

print("Fetching finish!")

# Create pandas dataframe and convert to csv
column_name = ['Name', 'Post', 'Date', 'Phone', 'Share Counts', 'Comment Counts', 'Like Counts']
df = pd.DataFrame(comments_row, columns=column_name)
df.to_csv('output/WeiboPosts.csv', encoding='utf-8-sig')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
from django.utils import timezone
from .models import Post, DonationLocation
import logging


logger = logging.getLogger(__name__)

def scrape_blood_donation_posts():
    # ตั้งค่า Selenium
    options = Options()
    # options.add_argument("--headless")  # ไม่แสดงผลเบราว์เซอร์
    service = Service("C:/Program Files/chromedriver-win64/chromedriver.exe")  # ระบุที่อยู่ของ ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # เข้าไปที่หน้า Facebook ที่ค้นหาด้วยแฮชแท็ก
        driver.get("https://www.facebook.com/hashtag/บริจาคเลือด")
        time.sleep(5)  # รอให้หน้าโหลดเสร็จ

        try:
            # รอให้ป๊อปอัปปรากฏ
            time.sleep(5)  # รอป๊อปอัปโหลดก่อน

            # คลิกปุ่มปิดป๊อปอัป
            close_button = driver.find_element("xpath", "//div[contains(@class, 'x1i10hfl') and contains(@aria-label, 'Close')]")
            close_button.click()
            print("success")
            time.sleep(10)
        except NoSuchElementException:
            print("button not found")
            time.sleep(10)
            
        time.sleep(5)
        # ดึง source code ของหน้า
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print("soup")
        time.sleep(5)
        

        # หาโพสต์ที่ต้องการ
        posts = soup.find_all('span', {'class': 'x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h'})
        print(posts)
        time.sleep(5)

        for post in posts[:5]:
            # ดึงข้อความของโพสต์
            time.sleep(5)
            try:
                detail = post.find('div').text
                print(f"content=: {detail}")  # ตรวจสอบเนื้อหาโพสต์
            except AttributeError:
                print("content not found")
                continue


            # Post.objects.create(detail=detail)
            # print("create success")

    except Exception as e:
        print(f"error: {e}")
    finally:
        driver.quit()

# def extract_location(post_content):
#     match = re.search(r'โรงพยาบาล\S*', post_content)
#     if match:
#         return match.group(0)  # คืนค่าชื่อโรงพยาบาลที่พบ
#     return None  # หากไม่พบโรงพยาบาล
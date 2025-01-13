import time
import random
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


def random_sleep():
    """Tạm dừng ngẫu nhiên trong khoảng 2-5 giây."""
    time.sleep(random.uniform(2, 5))


def open_webpage_with_selenium(url):
    """Mở trình duyệt và thu thập dữ liệu CV từ trang web."""
    # Cấu hình trình duyệt
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Khởi tạo trình duyệt với ChromeDriverManager
    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=options)

    try:
        # Mở trang web
        driver.get(url)
        print(f"Đã mở trang web: {url}")

        wait = WebDriverWait(driver, 10)
        random_sleep()

        # Đăng nhập
        gmail = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Email"]')))
        gmail.send_keys("hr@mcna.vn")
        random_sleep()

        pwd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Mật khẩu"]')))
        pwd.send_keys("McTu@2025")
        random_sleep()

        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        login_button.click()
        print("Đăng nhập thành công.")
        random_sleep()

        # Xử lý trang chủ
        button = wait.until(EC.element_to_be_clickable((By.ID, "topcv-popover-allow-button")))
        button.click()
        print("Đã nhấn nút 'Không, cảm ơn'.")
        random_sleep()

        # Chuyển tới mục "Quản lý CV"
        menu_item = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Quản lý CV')]")))
        menu_item.click()
        print("Đã nhấn vào 'Quản lý CV'.")
        random_sleep()
        
        # Thu thập dữ liệu CV
        target_date = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        stop_date = (datetime.now() - timedelta(days=2)).strftime("%d/%m/%Y")
        print(f"Ngày cần tìm: {target_date}")
        print(f"Ngày dừng: {stop_date}")
        all_data = []
        ktra = True
        while ktra:
            # Lấy HTML của bảng dữ liệu
            table_html = driver.find_element(By.CSS_SELECTOR, ".table.mb-0.border-0").get_attribute("outerHTML")
            soup = BeautifulSoup(table_html, "html.parser")
            rows = soup.select("tr.cv")

            for row in rows:
                # Lấy thông tin CV
                application_date = row.select_one(".fa-clock").next_sibling.strip()
                print(f"Ngày ứng tuyển: {application_date}")
                
                # Kiểm tra ngày ứng tuyển
                if stop_date in application_date:
                    print("Đã dừng thu thập vì gặp ngày dừng.")
                    ktra = False
                    break
                
                if target_date in application_date:
                    fullname = row.select_one(".fullname a").text.strip()
                    email = row.select_one(".fa-envelope").next_sibling.strip()
                    phone = row.select_one(".fa-circle-phone").next_sibling.strip()
                    job_title = row.select_one(".text-gray.text-truncate").text.strip()
                    cv_status = row.select_one(".cv-status").text.strip()

                    download_link_tag = row.select_one('a[href*="/download-cv"]')
                    download_link = download_link_tag['href'] if download_link_tag else "N/A"

                    data = {
                        "Họ và Tên": fullname,
                        "Email": email,
                        "Số Điện Thoại": phone,
                        "Vị Trí Ứng Tuyển": job_title,
                        "Ngày Ứng Tuyển": application_date,
                        "Trạng Thái CV": cv_status,
                        "Link Download CV": download_link
                    }
                    all_data.append(data)

            # Chuyển sang trang tiếp theo
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[href="#next"] i.fa-angle-right')
            next_button.click()
            print("Đã chuyển sang trang tiếp theo.")
            random_sleep()

    finally:
        driver.quit()
        print("Trình duyệt đã đóng.")
        return all_data

def fill_google_form(data):
    """Điền thông tin từ dữ liệu vào form Google."""
    # Cấu hình trình duyệt
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(ChromeDriverManager().install()), options=options)

    form_url = "https://forms.gle/Kvxm6ALvLNBgYwpX8"

    try:
        # Mở form Google
        driver.get(form_url)
        print(f"Đã mở form: {form_url}")

        wait = WebDriverWait(driver, 10)
        random_sleep()

        # Điền thông tin vào các trường
        fullname_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-labelledby="i1 i4"]')))
        fullname_input.send_keys(data["Họ và Tên"])
        random_sleep()

        job_title_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[8]/div/div/div/div/div[1]/input')))
        job_title_input.send_keys(data["Vị Trí Ứng Tuyển"])
        random_sleep()

        recruitment_site = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Trang web tuyển dụng TopCV')]")))
        recruitment_site.click()
        random_sleep()

        status_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[4]/div/div/div[2]/div/div[1]/div/div[1]/input')))
        status_input.send_keys("Chưa có")
        random_sleep()

        location_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[5]/div/div/div[2]/div/div/span/div/div[3]/div/span/div/div/div[1]/input')))
        location_input.send_keys("trong CV")
        random_sleep()

        phone_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-labelledby="i85 i88"]')))
        phone_input.send_keys(data["Số Điện Thoại"])
        random_sleep()

        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-labelledby="i90 i93"]')))
        email_input.send_keys(data["Email"])
        random_sleep()

        cv_link_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[aria-labelledby="i95 i98"]')))
        cv_link_input.send_keys(data["Link Download CV"])
        random_sleep()

        submitter_name_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[9]/div/div/div[2]/div/div/span/div/div[4]/div/span/div/div/div[1]/input')))
        submitter_name_input.send_keys("KienLT")
        random_sleep()

        cv_location_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[10]/div/div/div[2]/div/div/span/div/div[4]/div/span/div/div/div[1]/input')))
        cv_location_input.send_keys("trong CV")
        random_sleep()

        interview_status = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Chưa phỏng vấn')]")))
        interview_status.click()
        random_sleep()

        additional_info = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[12]/div/div/div[2]/div/div[1]/div[2]/textarea')))
        additional_info.send_keys("Không")
        random_sleep()

        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Gửi')]")))
        submit_button.click()
        random_sleep()

        print("Form đã được gửi thành công.")

    finally:
        driver.quit()
        print("Trình duyệt đã đóng.")


# Thực hiện với từng kết quả trong danh sách kết quả thu được
if __name__ == "__main__":
    website = "https://tuyendung.topcv.vn/app/login"
    results = open_webpage_with_selenium(website)
for result in results:
    print(result)
    fill_google_form(result)

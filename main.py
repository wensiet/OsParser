from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait


class OzonParse:
    url = "https://www.ozon.ru/category/smartfony-15502/?page={}&sorting=rating"

    driver = webdriver.Chrome("chromedriver")
    parsed = []

    def get_elements(self) -> list:
        for page_number in range(1, 100):
            if len(self.parsed) >= 100:
                break
            self.driver.get(self.url.format(page_number))
            elements = wait(self.driver, 2).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ok9")))
            while True:
                self.driver.execute_script('arguments[0].scrollIntoView(true);', elements[-1])
                try:
                    wait(self.driver, 2).until(lambda driver: len(
                        wait(driver, 2).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ok9')))) > len(
                        elements))
                    elements = wait(self.driver, 2).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ok9")))
                except:
                    break
            self.driver.delete_all_cookies()
            result = []
            text_result = []
            for element in elements:
                if element.text not in text_result:
                    result.append(element)
                    text_result.append(element.text)
            for element in result:
                link = str(element.get_attribute("href"))
                slash_count = 0
                for char in range(len(link)):
                    slash_count += 1 if link[char] == "/" else 0
                    if slash_count == 5:
                        link = link[:char]
                        break
                self.parsed.append({
                    "name": element.text,
                    "link": link + '/features/',
                    "os": None,
                })

    def get_os(self):
        for element in self.parsed:
            self.driver.get(element["link"])
            try:
                if "iphone" in element["link"]:
                    os_element = self.driver.find_elements(By.CLASS_NAME, "ly6")
                    for elem in os_element:
                        if "ios" in elem.text.lower():
                            element["os"] = elem.find_elements(By.TAG_NAME, "dd")[1].text
                else:
                    os_element = self.driver.find_elements(By.CLASS_NAME, "ly6")
                    for elem in os_element:
                        if "android" in elem.text.lower():
                            wwe = elem.find_elements(By.TAG_NAME, "dd")
                            left = []
                            for ss in wwe:
                                if "android" in ss.text.lower():
                                    left.append(ss.text)
                            element["os"] = left[-1]
            except Exception as e:
                print(e)
            self.driver.delete_all_cookies()

    def close(self):
        self.driver.quit()

    def get_parsed_data(self):
        return self.parsed


if __name__ == '__main__':
    ozon = OzonParse()
    ozon.get_elements()
    ozon.get_os()
    data = ozon.get_parsed_data()
    links = {}
    for link in data:
        try:
            links[link["os"]] += 1
        except:
            links.update({link["os"]: 1})
    links = sorted(links.items(), key=lambda x: x[1], reverse=True)
    for link in links:
        print("{} - {}".format(link[0], link[1]))
    ozon.close()

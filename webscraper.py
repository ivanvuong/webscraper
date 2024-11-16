from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import json, logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'mcdonalds_scraper_{datetime.now().strftime("%Y%m%d")}.log'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

class McDonaldsScraper():
    def __init__(self) -> None:
        '''Initializes the McDonaldsScraper class, setting up the driver and links to scrape from, as well as the jobs array to store the scraped data'''
        self.driver = self.setup_driver()
        self.links = self.mcdonalds_links()
        self.jobs = []

    def setup_driver(self) -> webdriver.Chrome:
        '''Sets up the Chrome driver for web scraping with options'''
        for attempt in range(3):
            try:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                driver = webdriver.Chrome(options=options)
                driver.implicitly_wait(10)
                return driver
            except WebDriverException as e:
                if attempt == 2:
                    logging.error(f"Error setting up Chrome driver: {e}")
                    raise
                logging.warning(f"Driver setup attempt {attempt + 1} failed: {e}. Retrying...")
    
    def mcdonalds_links(self) -> list:
        '''Returns a list of links to scrape from the McDonalds job site, equal to approximately 5000 records'''
        return [f"https://jobs.mchire.com/jobs?page_size=10&page_number={i}&sort_by=headline&sort_order=ASC" for i in range(1,510)]
    
    def get_job_details(self, link: str) -> tuple:
        '''Scrape the job details from the given link, including the description, hourly rate and types of job. 
        Returns a tuple of the description, hourly rate and types, given the link of the specific job listing
        Specifically, it opens the link of the job listing in a new tab, and then scrapes the details from that tab 
        by parsing specific keywords and elements from the page then closing the tab and returning the details'''
        for attempt in range(3):
            try:
                description, hourly_rate, types = "", "", []
                self.driver.execute_script("window.open(arguments[0])", link)
                self.driver.switch_to.window(self.driver.window_handles[1])
                WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "p")))
                elements = self.driver.find_elements(By.CSS_SELECTOR, 'p')
                for i in range(len(elements)):
                    try:
                        text = elements[i].text
                        if ".00" in text.lower():
                            index = text.lower().index("$")
                            end_index = text.lower().index(".00") + 3
                            hourly_rate = text[index:end_index]
                        elif ".50" in text.lower():
                            index = text.lower().index("$")
                            end_index = text.lower().index(".50") + 3
                            hourly_rate = text[index:end_index]

                        keywords = ["at least", "job duties", "cook", "cashier"]
                        if any(keyword in text.lower() for keyword in keywords):
                            description = text + " "
                        elif "requirements" in text.lower():
                            index = i + 1
                            while index < len(elements) and ("additional info" not in elements[index].text.lower()):
                                description += elements[index].text
                                index += 1
                        elif "vital" in text.lower():
                            while index < len(elements) and ("day in the life" not in elements[index].text.lower()):
                                description += elements[index].text
                                index += 1
                        elif "your role is vital to the operations within the restaurant" in text.lower():
                            index = i + 1
                            while index < len(elements) and ("to be a successful" not in elements[index].text.lower()):
                                description += elements[index].text
                                index += 1
                        if ("full time" in text.lower() or "full-time" in text.lower()) and "Part Time" not in types:
                            types.append("Part Time")
                        if ("full time" in text.lower() or "full-time" in text.lower()) and "Full Time" not in types:
                            types.append("Full Time")
                        if "manager" in text.lower() and "Full Time" not in types:
                            types.append("Full Time")
                    except Exception as e:
                        logging.warning(f"Error parsing job details: {e}")
                        continue
                try:
                    title = self.driver.find_element(By.XPATH, "//h1[@class='_6c7f10']").text
                    if ".00" in title.lower():
                        index = title.lower().index("$")
                        end_index = title.lower().index(".00") + 3
                        hourly_rate = title[index:end_index]
                        hourly_rate = hourly_rate.replace(" ", "")
                    elif ".50" in title.lower():
                        index = title.lower().index("$")
                        end_index = title.lower().index(".50") + 3
                        hourly_rate = title[index:end_index]
                        hourly_rate = hourly_rate.replace(" ", "")
                    
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                except ValueError:
                    pass
                except Exception as e:
                    logging.warning(f"Error parsing job details: {e}")  
                return description.strip(), hourly_rate, types
            except (TimeoutException, NoSuchElementException) as e:
                if attempt == 2:  
                    logging.error(f"Failed to get job details after 3 attempts: {e}")
                    return "", "", []
                logging.warning(f"Failed for job details at {link}: {e}")
            finally:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

    def scrape_mcdonalds_jobs(self) -> None:
        '''Scrape all the given Mcdonalds job links, including their location, link, title, description, hourly rate and types and
        append that information as a dictionary of many values to the jobs array. Specifically, it finds each of the elements in the 
        job list board, parses the information given such as the location, href link, and title of the job, then calls the get_job_details
        to get the description, hourly rate and types of the job, and appends that information to the jobs array'''
        logging.info(f"Starting web scrape of {len(self.links)} McDonalds job listing pages, with {len(self.links) * 10} job listings")
        for link in self.links:
            for attempt in range(3):
                self.driver.get(link)
                try:
                    WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='results-list front']/li[@class='results-list__item']")))
                    job_list = self.driver.find_elements(By.XPATH, "//ul[@class='results-list front']/li[@class='results-list__item']")

                    for job in job_list:
                        try:
                            location = job.find_element(By.XPATH, ".//span[@class='results-list__item-street--label']").text
                            header = job.find_element(By.XPATH, ".//a[@class='results-list__item-title']")
                            href_link = header.get_attribute("href")
                            title = header.text
                            description, hourly_rate, types = self.get_job_details(href_link)
                            self.jobs.append({
                                "address": location,
                                "jobs": [
                                    {
                                        "jobLink": href_link,
                                        "title": title,
                                        "description": description,
                                        "hourlyRate": hourly_rate,
                                        "types": types,
                                    }
                                ]
                            })
                        except NoSuchElementException as e:
                            logging.warning(f"Missing data in job listing: {e}")
                except TimeoutException as e:
                    if attempt == 2:
                        logging.error(f"Timeout while loading page {link} after 3 attempts: {e}")
                        break
                    logging.warning(f"Timeout while loading page {link}. Retrying...")
                except WebDriverException as e:
                    if attempt == 2:
                        logging.error(f"Error loading the job list page {link} after 3 attempts: {e}")
                        break
                    logging.warning(f"Error loading the job list page {link}. Retrying...")
        logging.info(f"Completed scraping McDonald's job listings. {len(self.jobs)} jobs found")

    def save_array_to_json(self, filename: str) -> None:
        '''Saves the array of jobs to a json file, taking in the file name as a parameter'''
        for attempt in range(3):
            try:
                with open(filename, 'w', encoding="utf-8") as json_file:
                    json.dump(self.jobs, json_file, indent=4)
                    logging.info(f"Successfully saved to {filename}")
                    break
            except Exception as e:
                if attempt == 2:
                    logging.error(f"Error saving to json file, {str(e)}")
                    raise
                logging.warning(f"Error saving to json file, {str(e)}. Retrying...")


    def __enter__(self) -> 'McDonaldsScraper':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.driver.quit()
        if exc_type:
            logging.error(f"Error during scraping execution: {str(exc_val)}")

if __name__ == "__main__":
    scraper = McDonaldsScraper()
    scraper.scrape_mcdonalds_jobs()
    scraper.save_array_to_json("mcdjobs.json")
    print(len(scraper.jobs))
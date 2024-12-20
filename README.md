Unibui Webscraper Take Home Assignment 

My approach to this Web Scraper assignment was to examine how each different job website was formatted and find pieces of information that I could
utilize. Prior to programming, I chose McDonalds as my data source to be scraped, and I spent time inspecting elements such as paths, 
class names, hrefs, and links to understand how to access the specified data. I decided to design a class in order to hold the Selenium driver,
links, and parsed job data. I setup my driver to parse information from the general job board such as the title and href link, then opened
new windows for each of them in order to get their description, hourly rates, and types of job. Since many of the jobs were formatted differently on 
each page, I attempted to parse information based off key words and patterns in order to get as much information as possible. I then saved the information
to JSON and returned it in the Unibui JSON format. 

A challenge I faced was parsing specific information from the web postings that did not explicitly have description, hourly rates and types of jobs.
Specifically, some of the information was hard coded with keywords in order to fit a large amount of web scraping from different websites. I also faced another challenge with  
maintaining scope of the Selenium driver when going into another link. If I opened another link with the same driver without opening another 
window, it would have raised errors in losing the initial window containing information such as the job link that I was using. I ended up
solving this by utiizing another window in order to open the new link, then closing that for each job listing. 

# Importing Dependencies
import pandas as pd
import requests
import warnings
import logging
import yaml
import time
import bs4
import os

# Filtering out potential warnings
warnings.filterwarnings(action="ignore")

# Defining the directory path for the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Getting the absolute path based on the script's path
LOG_DIR = os.path.join(SCRIPT_DIR, "../Logs")

# Getting the absolute path based on the script's path
CONFIG_PATH = os.path.join(SCRIPT_DIR, "../Configuration/config.yml")

# Getting the absolute path based on the script's path
DATA_DIR = os.path.join(SCRIPT_DIR, "../Data")

# Creating a log file using the dynamic path
logging.basicConfig(filename=os.path.join(LOG_DIR, "scraper.log"),
                    filemode="w",
                    format="%(asctime)s - %(message)s - %(levelname)s",
                    level=logging.INFO)

# Loading the configuration file using the dynamic path
with open(file=CONFIG_PATH) as yaml_file:
    config=yaml.safe_load(stream=yaml_file)
    
# Extracting the list of target URLS
target_urls=config.get("target_urls")

# Extracting the base URL
base_url=config.get("base_url")

# Defining a custom class to scrape data
class ArxivScraper:
    # Defining instance attributes
    def __init__(self, base_url: str):
        # Instantiating the base URL
        self.base_url=base_url

    # Defining an instance method to build a parser
    def build_parser(self, url: str):
        # Sending request to the target URL
        response=requests.get(url=url)

        # Asserting the status code
        assert response.status_code==200

        # Configuring parser
        soup=bs4.BeautifulSoup(markup=response.content, features="html.parser")

        # Returning the parser
        return soup

    # Defining an instance method to scrape data
    def scrape_data(self):
        # Defining the total number of articles
        total_articles=0
        
        # Calling the instance method to build the parser
        soup=self.build_parser(url=self.base_url)
        
        # Extracting the fields
        fields=soup.find_all(name="ul")
        
        # Looping through each subject
        for field in fields:
            # Extracting the IDs for topics
            topics=[i.get("href") for i in field.find_all(name="a")]

            # Filtering the topics to get the topic links
            topics=[self.base_url+i for i in topics if i.startswith("/list")]
            
            # Looping throug each target URL
            for target_url in topics:
                # Calling the instance method to build the parser
                soup=self.build_parser(url=target_url)

                # Creating an object for articles
                articles=soup.find(name="dl", attrs={"id": "articles"})

                # Extracting the IDs for abstracts
                abstract_ids=[article.find(name="a", attrs={"title": "Abstract"}).get("href") for article in articles.find_all(name="dt")]

                # Creating a link based on abstract IDs
                abstract_links=[self.base_url+abstract_id for abstract_id in abstract_ids]

                # Creating an empty list to store data frame
                abstract_list=[]

                # Looping through each abstract link
                for link in abstract_links:
                    # Configuring parser
                    nested_soup=self.build_parser(url=link)

                    # Extracting the title
                    title=nested_soup.find(name="h1", attrs={"class": "title mathjax"}).text.split("Title:")[1]

                    # Extracting the abstract
                    abstract=nested_soup.find(name="blockquote", attrs={"class": "abstract mathjax"}).text.strip().replace("Abstract:", "")

                    # Submission date
                    submission_date=nested_soup.find(name="div", attrs={"class": "dateline"}).text.strip().replace("[", "").replace("]", "")

                    # Extracting the author(s)
                    authors=[author.text for author in nested_soup.find(name="div", attrs={"class": "authors"}).find_all(name="a")]

                    # Extracting categories
                    category=nested_soup.find(name="div", attrs={"class": "subheader"}).text.strip()

                    # Storing the data in a dictionary
                    scraped_data={"title": title, 
                                  "abstract": abstract,
                                  "category": category,
                                  "submission_date": submission_date,
                                  "authors": [authors]}

                    # Appending the dictionary to the list
                    abstract_list.append(scraped_data)
                    
                    # Logging the information
                    logging.info(msg=f"{title} article has been scraped!")
                    
                    # Printing output to the terminal
                    print(f"{title} article has been scraped!")

                # Converting the dictionaries into a data frame
                topic_df=pd.DataFrame(data=abstract_list)

                # Removing potential duplicates
                topic_df.drop_duplicates(subset=["title", "abstract"], inplace=True, ignore_index=True)
                
                # Extracting the number of articles
                n_articles=topic_df.shape[0]
                
                # Defining the filepath
                filepath=os.path.join(DATA_DIR, "arxiv_articles.parquet.brotli")
                
                # Creating a condition based on the existence of a path
                path_exists=os.path.exists(path=filepath)
                
                # Creating a condition
                if path_exists:
                    # Loading the data frame
                    existing_df=pd.read_parquet(path=filepath, engine="fastparquet")
                    
                    # Concatenating the data frames
                    topic_df=pd.concat(objs=[topic_df, existing_df], ignore_index=True)
                    
                # Removing potential duplicates
                topic_df.drop_duplicates(subset=["title", "abstract"], inplace=True, ignore_index=True)
                    
                # Saving the data frame to the specified path
                topic_df.to_parquet(path=filepath,
                                    engine="fastparquet",
                                    compression="brotli",
                                    index=False)
                
                # Updating the number ot total articles scraped
                total_articles += n_articles
                
                # Logging the information
                logging.info(msg=f"{total_articles} abstracts in total have been scraped successfully!")
                
                # Pausing for 5 seconds
                time.sleep(5)

# Running the script
if __name__ == "__main__":
    # Defining the start time
    start_time=time.time()
    
    # Logging the information
    logging.info(msg="Web scraping process started!")
       
    # Instantiating the class
    scraper=ArxivScraper(base_url=base_url)

    # Calling the function to scrape data
    scraper.scrape_data()
    
    # Defining the end time
    end_time=time.time()
    
    # Calculating the scraping time
    total_time=(end_time-start_time)/60
    
    # Logging the information
    logging.info(msg=f"Web scraping process finished in {total_time:.0f} minutes")
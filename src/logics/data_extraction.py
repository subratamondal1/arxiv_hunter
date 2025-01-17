"""Data Extraction from arxiv api"""

import os.path
import json
import argparse
from datetime import datetime
from typing import Dict, List
import requests
import feedparser
from tqdm import tqdm
import fitz  # this is pymupdf

STANDARD_SEARCH_QUERY: str = (
    "cat:cs.CV OR cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.NE OR cat:stat.ML OR cat:cs.IR"
)


class ArxivParser:
    """Extract & Parse data from the Arxiv API"""

    base_url = "http://export.arxiv.org/api/query"

    def __init__(self, data_path="../data/"):
        self.extracted_data: List[Dict[str, str]] = (
            []
        )

        if not os.path.exists(data_path):
            os.makedirs(data_path)
        self.data_path = data_path

    def get_results(
        self,
        max_results: int = 5,
        days: int = 60,
        search_query: str = STANDARD_SEARCH_QUERY,
    ) -> List[Dict[str, str]]:

        """Get results from the Arxiv API"""

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = self.base_url + "?" + requests.compat.urlencode(params)

        
        response = requests.get(url, timeout=15)
        
        entries = feedparser.parse(response.text).entries

        downloaded_data: List[Dict[str, str]] = (
            []
        ) 

       
        for entry in tqdm(entries):
            published_date = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
            current_date = datetime.now()
            date_diff = (current_date - published_date).days

           
            if date_diff <= days:
                link = entry.link              
                pdf_link = link.replace("abs", "pdf")
                pdf_content = requests.get(pdf_link, timeout=15).content
                pdf_file = fitz.open(stream=pdf_content, filetype="pdf")
                
                pdf_text = ""
                for page in pdf_file:
                    pdf_text += page.get_text()
                
                downloaded_data.append(
                    {
                        "id": entry.id,
                        "title": entry.title,
                        "summary": entry.summary,
                        "published_date": str(published_date),
                        "pdf_link": pdf_link,
                        "pdf_text": pdf_text,
                    }
                )
        
        self.extracted_data.extend(downloaded_data)
        
        return self.extracted_data

    def store_data(
        self,
        save_file_name: str = "master_data.json",
        max_results: int = 10,
        days: int = 60,
    ) -> None:
        """Store the Extracted data in Json format"""
        self.extracted_data = self.get_results(max_results, days)

        assert len(self.extracted_data) > 0, "Got no results with the search query"
        
        for data in self.extracted_data:
            data["published_date"] = data["published_date"].strftime("%Y-%m-%d")
       
        save_location = os.path.join(self.data_path, save_file_name)
        with open(save_location, "w", encoding="utf-8") as f:
            json.dump(self.extracted_data, f, indent=4)

    def get_stored_data(self):
        """Return the self.extracted_data attribute"""

        assert len(self.extracted_data) != 0, "Please store data first"
        return self.extracted_data


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A recommender system based on tf-idf and cosine similarity"
    )

    # Add an argument for the query
    parser.add_argument(
        "-m",
        "--max_results",
        type=str,
        help="Maximum results to store",
        nargs="?",
        default=5,
    )
    parser.add_argument(
        "-d",
        "--days",
        type=str,
        help="Store only for these many past days",
        nargs="?",
        default=50,
    )

    # Parse the arguments
    args = parser.parse_args()

    new_max_results = args.max_results
    new_days = args.days

    # initialize parser
    parser = ArxivParser()

    # store the past data
    parser.store_data(max_results=new_max_results, days=new_days)

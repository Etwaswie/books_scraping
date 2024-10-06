# Book Scraping Project

This repository contains a web scraping project designed to extract book information from a specified website. The primary goal of this project is to gather data on various books, 
including ISBN, titles, authors, genres, year of release, age restrictions, number of pages, publishers, ratings, number of ratings, type of paper and binding, as well as descriptions to facilitate analysis and insights into book trends.

## Data Collection Methods

The project utilizes two different methods for data collection:

1. **Selenium**: 
   - This method is used for scraping dynamic content from the website. While it is more comprehensive and can handle JavaScript-rendered pages, it is slower compared to the other method.
   - Selenium simulates a web browser, allowing us to navigate through the site as a human user would.

2. **Requests**:
   - This method is faster and is used for scraping static content. It sends HTTP requests to the server and retrieves the HTML content directly.
   - This approach is ideal for pages that do not require JavaScript for rendering the content.

## Data Storage

The scraped data is stored in two formats:

- **CSV File**: The data is recorded in a CSV file, making it easy to analyze and visualize using tools like Excel or Pandas.
- **ClickHouse Database**: The project also supports saving the data into a ClickHouse database, allowing for efficient querying and analysis of large datasets.

## Datasets

The datasets generated from the scraping processes are stored in Google Drive. You can access the datasets using the following link:

[Access Datasets](https://drive.google.com/your_dataset_link)

*Note: Make sure you have the necessary permissions to access the datasets.*

## Installation and Usage

To run the scraping scripts, you will need to have Python installed on your machine along with the required libraries. Here are the steps to get started:

1. Clone this repository:
   ```bash
   git clone https://github.com/Etwaswie/books_scraping.git
   cd book-scraping
   
2. Install the required packages:
    ```bash
    pip install -r requirements.txt 
    ```
3. Choose your preferred scraping method and run the corresponding script:
   
    For Selenium:
    ```bash
    python selenium_parser.py
    ```
    
    For Requests:
    ```bash
    python requests_parser.py
    ```

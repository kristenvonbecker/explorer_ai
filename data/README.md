## Explorer AI's knowledgebase

Explorer AI's knowledgebase was amassed through a combination of web scraping and API queries. The data pipeline 
consists of the following steps:

1. Web scraping, of exhibit-level data at [exploratorium.edu/exhibits](https://www.exploratorium.edu/exhibits)
   (see `web_scraping/exploratorium/`)
2. Data processing and loading (see `processing/`)
    - Clean and validate data 
    - Use Chat GPT to generate new exhibit-level features (specifically, keywords)
    - Load processed data into a database
3. API queries, to obtain the full text of Encyclopaedia Britannica articles relevant to exhibit keywords (see `get_articles/`)
    - Use pre-trained word embeddings and Faiss indexing to efficiently look up relevant article titles
    - Query the Britannica Syndication API for the contents of each relevant article by title
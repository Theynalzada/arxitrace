# 🌌 ArxiTrace: arXiv Topic Modeling & Clustering

ArxiTrace is an end-to-end Natural Language Processing pipeline that scrapes scientific abstracts from arXiv and uses advanced clustering to discover and map latent research topics. Developed by Kenan Zeynalzade, this project transforms thousands of unstructured abstracts into clean, human-readable research themes using a multi-stage machine learning architecture.

## ✨ Pipeline Architecture

### 1. Data Collection (`scraper.py`)
* Operates via a custom `ArxivScraper` class, utilizing `requests` and `bs4` (BeautifulSoup) to parse targeted arXiv HTML pages[cite: 2].
* Systematically extracts crucial article metadata, including the title, abstract, submission date, authors, and category[cite: 2].
* Saves the scraped output incrementally into a compressed Parquet file (`arxiv_articles.parquet.brotli`) stored in the `Data` directory[cite: 2].
* Employs deduplication logic to ensure previously scraped abstracts are not appended multiple times[cite: 2].
* Tracks execution progress and article counts, writing runtime events to a `scraper.log` file in the `Logs` directory[cite: 2].
* Dynamically loads scraping targets and base URLs from a centralized `config.yml` file[cite: 2].

### 2. Topic Modeling & Clustering (`Modeling.ipynb`)
* **Semantic Embeddings:** Loads the scraped Parquet dataset and translates the textual abstracts into dense vector representations using the `SentenceTransformer` library[cite: 1].
* **Dimensionality Reduction:** Compresses the high-dimensional embeddings into a tightly grouped topology using `UMAP`[cite: 1].
* **Density-Based Clustering:** Identifies dense clusters of related research vectors using the `HDBSCAN` algorithm[cite: 1].
* **Multi-Aspect Representation:** Constructs a sophisticated `BERTopic` model customized with a multi-aspect representation dictionary[cite: 1].
* **Keyword Diversification:** Extracts highly representative keywords using `KeyBERTInspired`, followed by `MaximalMarginalRelevance` to filter out redundant synonyms[cite: 1].
* **Generative Labeling:** Passes representative abstracts and keywords into a Hugging Face `TextGeneration` pipeline, prompting the LLM to output a highly concise categorical label for each topic[cite: 1].
* **Interactive Visualizations:** Generates comprehensive visualizations, such as document scatter plots and topic word score bar charts, directly in the notebook[cite: 1].

## 🛠️ Configuration & Security
* **YAML Management:** Core hyperparameters—including the embedding model ID, language model settings (temperature, top-k, top-p), UMAP components, and HDBSCAN cluster sizes—are decoupled from the code and managed inside `Configuration/config.yml`[cite: 1].
* **Secret Handling:** Access tokens required for downloading models, such as the `HUGGINGFACE_API_KEY`, are securely authenticated by loading a `.env` file via `python-dotenv`[cite: 1].
# PDF Chatbot with Vertex AI

**Engage with your PDF documents like never before!** This application provides an intuitive chat interface, allowing you to ask questions and receive accurate, contextually relevant answers directly from your uploaded PDF files using the power of Google Vertex AI and LangChain.

## Features

* **Intelligent Q&A**: Ask natural language questions about your PDF content and get precise answers.
* **Large Document Support**: Seamlessly process and chat with extensive PDF documents, including those 200+ pages long.
* **Contextual Conversations**: The chatbot remembers previous turns, allowing for natural follow-up questions and a coherent dialogue.
* **Powered by Google Vertex AI**: Leverages Google's cutting-edge AI models for robust text embeddings (`text-embedding-004`) and advanced language understanding (`gemini-2.5-pro`).
* **Robust & Observable**: Integrated with comprehensive error handling and a rotating file-based logging system, making it easy to monitor and debug.

## Project Structure

```text
pdf-chatbot/
├── app.py                  # Main Streamlit web application interface
├── requirements.txt        # Python package dependencies
├── .env                    # Environment variables for Google Cloud configuration
├── logs/                   # Directory for application logs (automatically created upon run)
│   └── app.log             # Primary rotating log file
├── src/
│   ├── pdf_processor.py    # Handles PDF loading, text extraction, and document chunking
│   ├── vector_store.py     # Manages vector embedding creation (Vertex AI) and FAISS index
│   ├── config.py           # Centralized Google Cloud project and model configuration
│   ├── chatbot.py          # Implements the LangChain conversational retrieval chain
│   ├── logger_config.py    # Configures the application's logging system
└── run.sh                  # Shell script for robust environment variable loading and app launch
```

## Setup and Installation

Follow these steps to get the PDF Chatbot up and running on your local machine:

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd pdf-chatbot
    ```
    (Replace `<repository_url>` with the actual URL of your Git repository)

2.  **Create and Activate a Python Virtual Environment**:
    It's highly recommended to use a virtual environment to isolate project dependencies.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install Python Dependencies**:
    Install all required libraries using pip.
    ```bash
    pip install -r requirements.txt
    ```
    *(If `requirements.txt` is not yet generated, you can create it after installing necessary packages using `pip freeze > requirements.txt`)*

4.  **Configure Google Cloud Credentials**:
    This application requires access to Google Vertex AI services.
    * **Create a Service Account**: In your Google Cloud project, create a new service account.
    * **Assign Roles**: Grant the service account necessary roles, such as "Vertex AI User" and "Service Account Token Creator".
    * **Generate Key**: Create and download a JSON key file for this service account.
    * **Update `.env`**: Create or update a `.env` file in the root directory of your project with the following details:

    ```dotenv
    GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
    PROJECT_ID="your-google-cloud-project-id"
    LOCATION="us-central1" # Or your preferred Vertex AI region
    MODEL_NAME="gemini-2.5-pro" # Language model for responses
    EMBEDDING_MODEL="text-embedding-004" # Embedding model for document chunks
    TEMPERATURE=0 # Controls randomness of model output (0 for deterministic)
    MAX_OUTPUT_TOKENS=4096 # Maximum length of generated responses
    ```
    *Ensure the `GOOGLE_APPLICATION_CREDENTIALS` path is absolute or relative to where you run the `run.sh` script.*

5.  **Make `run.sh` Executable and Run the Application**:
    You can run the application using the `run.sh` script for robust environment variable loading, or directly with `streamlit run app.py` if your environment variables are already set.

    **Option 1: Using `run.sh` (Recommended for robust environment setup)**
    ```bash
    chmod +x run.sh # Make the script executable (Linux/macOS)
    ./run.sh
    ```

    **Option 2: Using `streamlit run app.py` (If environment variables are already set)**
    ```bash
    # On Linux/macOS (set variables in current shell session)
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
    export PROJECT_ID="your-google-cloud-project-id"
    export LOCATION="us-central1"
    export MODEL_NAME="gemini-2.5-pro"
    export EMBEDDING_MODEL="text-embedding-004"
    export TEMPERATURE=0
    export MAX_OUTPUT_TOKENS=4096
    streamlit run app.py

    # On Windows (Command Prompt)
    set GOOGLE_APPLICATION_CREDENTIALS="path\to\your\service-account-key.json"
    set PROJECT_ID="your-google-cloud-project-id"
    set LOCATION="us-central1"
    set MODEL_NAME="gemini-2.5-pro"
    set EMBEDDING_MODEL="text-embedding-004"
    set TEMPERATURE=0
    set MAX_OUTPUT_TOKENS=4096
    streamlit run app.py
    ```

## Usage

1.  **Access the App**: After running the application, it will typically open automatically in your default web browser. If not, copy the local URL displayed in your terminal (e.g., `http://localhost:8501`).
2.  **Upload PDF**: Use the "Upload your PDF" file uploader in the Streamlit interface.
3.  **Process Document**: The application will display "Processing PDF..." and "Creating embeddings..." spinners. For large documents, this step can take some time. A "PDF processed successfully!" message will confirm completion.
4.  **Start Chatting**: Once the PDF is processed, a chat input box will appear. Type your questions about the document's content.
5.  **Review Logs**: Observe the terminal where you launched the app for real-time log messages, and check the `logs/` directory for stored log files (`app.log` and its rotations).

## Technologies Used

* **Streamlit**: The open-source app framework used to build the interactive web user interface.
* **LangChain**: A powerful framework that simplifies the development of LLM-powered applications, handling document loading, chunking, retrieval, and conversational memory.
* **Google Vertex AI**: Google Cloud's enterprise-grade machine learning platform, providing:
    * **`gemini-2.5-pro`**: A highly capable large language model for generating human-like text responses based on the retrieved context.
    * **`text-embedding-004`**: A state-of-the-art text embedding model used to convert text into numerical vectors for efficient similarity search.
* **FAISS**: Facebook AI Similarity Search, an open-source library used here as an efficient in-memory vector store for quick retrieval of relevant document chunks.
* **Google Cloud Platform**: The foundational cloud infrastructure providing the necessary API
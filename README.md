# PDF Chatbot with Vertex AI

**Engage with your PDF documents like never before!** This application provides an intuitive chat interface, allowing you to ask questions and receive accurate, contextually relevant answers directly from your uploaded PDF files using the power of Google Vertex AI and LangChain.

## Features

* **Intelligent Q&A**: Ask natural language questions about your PDF content and get precise answers.

* **Large Document Support**: Seamlessly process and chat with extensive PDF documents, including those 200+ pages long.

* **Contextual Conversations**: The chatbot remembers previous turns, allowing for natural follow-up questions and a coherent dialogue.

* **Powered by Google Vertex AI**: Leverages Google's cutting-edge AI models for robust text embeddings (`text-embedding-004`) and advanced language understanding (`gemini-2.5-pro`).

* **Robust & Observable**: Integrated with comprehensive error handling and a rotating file-based logging system, making it easy to monitor and debug.

## Project Structure


pdf-chatbot/
├── app.py                              # Main Streamlit web application interface
├── requirements.txt                    # Python package dependencies
├── .env                                # Environment variables for local Google Cloud configuration (IGNORED by Git)
├── .env.example                        # Example file for .env (COMMITTED to Git)
├── logs/                               # Directory for application logs (automatically created upon run)
│   └── app.log                         # Primary rotating log file
├── .streamlit/                         # Streamlit Cloud configuration directory
│   ├── secrets.toml                    # Encrypted secrets for Streamlit Cloud deployment (IGNORED by Git)
│   └── secrets.toml.example            # Example file for secrets.toml (COMMITTED to Git)
├── src/
│   ├── pdf_processor.py                # Handles PDF loading, text extraction, and document chunking
│   ├── vector_store.py                 # Manages vector embedding creation (Vertex AI) and FAISS index
│   ├── config.py                       # Centralized Google Cloud project and model configuration
│   ├── chatbot.py                      # Implements the LangChain conversational retrieval chain
│   └── logger_config.py                # Configures the application's logging system
└── local_cloud_simulation_run.py       # Python script for local simulation of Streamlit Cloud (Base64 credentials)


## Setup and Installation

Follow these steps to get the PDF Chatbot up and running on your local machine or deployed to Streamlit Cloud.

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

### Local Development Setup

For local development, you now have two clear options for handling Google Cloud credentials:

#### Option A: Standard Local Development (Recommended for daily local use)

This is the simplest way to run locally, relying on `python-dotenv` to load credentials from a file path.

1.  **Download Service Account Key**: Ensure you have your Google Cloud service account key JSON file downloaded (e.g., `service-account-key.json`) to a secure location on your machine.

2.  **Create `.env` file**: In the **root directory** of your project, copy the `.env.example` file to `.env`.
    ```bash
    cp .env.example .env
    ```
    Then, open the newly created `.env` file and **replace the placeholder values with your actual configuration.**

    ```dotenv
    # .env (for standard local development)

    # Path to your Google Cloud service account key JSON file
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

    # Your Google Cloud project ID
    PROJECT_ID=your-google-cloud-project-id

    # Google Cloud region for Vertex AI (us-central1 is recommended)
    LOCATION=us-central1

    # Vertex AI model configuration
    MODEL_NAME=gemini-2.5-pro
    EMBEDDING_MODEL=text-embedding-004

    # Optional: Model parameters
    TEMPERATURE=0
    MAX_OUTPUT_TOKENS=4096
    ```

3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

#### Option B: Local Simulation of Cloud Behavior (For advanced debugging/testing)

This method uses Base64 encoded credentials loaded from `.streamlit/secrets.toml`, precisely mimicking how Streamlit Cloud passes secrets.

1.  **Download Service Account Key**: Ensure you have your Google Cloud service account key JSON file downloaded (e.g., `service-account-key.json`) to a secure location on your machine.

2.  **Create `secrets.toml`**: In the **`.streamlit/` directory** of your project, copy the `secrets.toml.example` file to `secrets.toml`.
    ```bash
    cp .streamlit/secrets.toml.example .streamlit/secrets.toml
    ```

3.  **Generate Base64 Credentials**: Open your terminal and run the following command to generate the Base64 encoded string of your service account JSON. **Replace `path/to/your/service-account-key.json` with the actual path to your file.**
    ```bash
    cat path/to/your/service-account-key.json | base64 | tr -d '\n' > creds.b64
    ```
    This command will save the Base64 string into a file named `creds.b64` in your current directory. You can then open `creds.b64` to copy its content.

4.  **Populate `secrets.toml`**: Open the newly created `.streamlit/secrets.toml` file and paste the copied Base64 string from `creds.b64`, replacing `"PASTE_YOUR_BASE64_ENCODED_JSON_STRING_HERE"` for `GOOGLE_CREDENTIALS_B64`. Fill in your actual `PROJECT_ID`, `LOCATION`, etc.

5.  **Run the application**:
    ```bash
    python local_cloud_simulation_run.py
    ```

### Deployment to Streamlit Cloud

1.  **Configure Secrets in Streamlit Cloud UI**:
    Since `secrets.toml` is ignored by Git for security reasons, you will need to manually input your secrets directly into the Streamlit Cloud dashboard.

    * Go to your Streamlit Cloud app dashboard.

    * Navigate to **"Settings"** (usually a gear icon) and then **"Secrets"**.

    * **Paste the entire content of your populated `.streamlit/secrets.toml` file directly into the text area provided in the Streamlit Cloud Secrets UI.** Streamlit Cloud is designed to parse this TOML content directly.

    * Save the secrets.

2.  **Deploy the Application**:

    * Go to your Streamlit Cloud dashboard.

    * Select your repository and branch.

    * Streamlit Cloud will automatically pick up your code from the repository.

    * **Clear Cache and Redeploy**: After configuring secrets, it's crucial to force a fresh deployment. Use the **"Clear cache and redeploy"** or **"Hard reboot"** option on your app's settings page to ensure your application picks up the newly configured secrets.

## Usage

1.  **Access the App**: After running the application (locally or deployed), it will typically open automatically in your web browser. If not, copy the local URL displayed in your terminal (e.g., `http://localhost:8501`).

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

* **Google Cloud Platform**: The foundational cloud infrastructure providing the necessary APIs and ser
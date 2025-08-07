# 🔦 AI Blueprint Analyzer

This project is a full-stack application designed to analyze electrical blueprint PDFs. It uses a combination of a Flask backend for AI processing and a Streamlit frontend for user interaction. The system identifies emergency lighting fixtures, extracts their symbols, and summarizes them using information from the lighting schedule.

-----

## ✨ Core Technologies

  * **Backend:** Python, Flask
  * **Frontend:** Streamlit
  * **AI / ML Models:**
      * **Google Gemini Pro Vision:** For detecting light fixtures from images.
      * **Google Gemini Pro:** For summarizing and grouping results.
      * **Hugging Face `nougat-small`:** For advanced OCR to extract tables and notes.
  * **Core Libraries:** `pdf2image`, `requests`, `pandas`

-----

## 📂 Project Structure

The repository is organized into a backend API and a frontend UI, with core AI logic separated for clarity.

```
.
├── core/
│   ├── __init__.py
│   ├── config.py           # Manages environment variables (API keys)
│   ├── llm.py              # Logic for Gemini text model (summarization)
│   ├── ocr.py              # Logic for Hugging Face OCR (rulebook extraction)
│   └── vision.py           # Logic for Gemini Vision model (detection)
│
├── uploads/                # Temporary directory for uploaded files
│
├── main.py                  # The Flask backend API
├── app.py        # The Streamlit frontend UI
├── requirements.txt        # Python dependencies
└── .env           
```

-----

## ⚙️ How It Works

The application follows a simple yet powerful pipeline:

1.  **Upload:** The user uploads a blueprint PDF via the **Streamlit** web interface.
2.  **API Call:** Streamlit sends the file to the **Flask backend**'s `/process` endpoint.
3.  **PDF Conversion:** The Flask app converts the PDF pages into high-resolution images.
4.  **Parallel AI Processing:**
      * **OCR Task:** The `nougat` model scans the images to find and parse the **Lighting Schedule** and **General Notes**, creating a "rulebook".
      * **Vision Task:** **Gemini Vision** analyzes the images, identifying all shaded emergency light fixtures and their corresponding text symbols.
5.  **Summarization:** **Gemini Pro** receives the list of detected lights and the rulebook. It then intelligently groups the lights by symbol, counts them, and matches them with their descriptions from the rulebook.
6.  **Display Results:** The final, structured JSON summary is sent back to the Streamlit UI, where it's displayed as a clean table and raw data.

-----

## 🚀 Setup and Installation

Follow these steps to get the project running on your local machine.

### 1\. Prerequisites

  * **Python 3.9+**

  * **Git** for cloning the repository.

  * **Poppler:** A system-level dependency required by `pdf2image`.

      * **On macOS (using Homebrew):**
        ```bash
        brew install poppler
        ```
      * **On Debian/Ubuntu:**
        ```bash
        sudo apt-get update && sudo apt-get install -y poppler-utils
        ```
      * **On Windows:** Download the [Poppler binaries](https://github.com/oschwartz10612/poppler-windows/releases/), unzip them, and add the `bin/` directory to your system's PATH.

### 2\. Clone the Repository

```bash
git clone https://github.com/Anidipta/palcode
cd palcode
```

### 3\. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 4\. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5\. Configure Environment Variables

You need a Google API key to use the Gemini models.

  * Create a file named `.env` in the root of the project.
  * Copy the content from `.env.example` into it.
  * Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
  * Add your key to the `.env` file:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

-----

## ▶️ Running the Application

You need to run the backend and frontend in two separate terminals.

**Terminal 1: Start the Flask Backend API**

```bash
flask --app app run
```

This will start the API server, typically on `http://127.0.0.1:5000`.

**Terminal 2: Start the Streamlit Frontend**

```bash
streamlit run app.py
```

This will open the web interface in your browser, typically at `http://localhost:8501`.

You can now open the Streamlit URL in your browser and start uploading blueprints\!

-----

## 🔌 API Endpoint

The project exposes a single, simple API endpoint for processing.

### `POST /process`

  * **Description:** Uploads a PDF file for full analysis. The request is synchronous and will wait until all AI processing is complete.
  * **Request Body:** `multipart/form-data` with a single field:
      * `file`: The PDF file to be processed.
  * **Success Response (200 OK):**
    ```json
    {
      "A1E": {
        "count": 15,
        "description": "2'X4' RECESSED LED LUMINAIRE W/ EMERGENCY BATTERY"
      },
      "W": {
        "count": 4,
        "description": "WALLPACK WITH BUILT IN PHOTOCELL"
      }
    }
    ```
  * **Error Response (4xx/5xx):**
    ```json
    {
      "error": "A description of the error that occurred."
    }
    ```

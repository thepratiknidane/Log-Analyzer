# Log Analyzer

A lightweight Flask-based web application for analyzing application log files through a clean browser interface. The project accepts uploaded log files or pasted raw log text, processes the content on the backend, and returns structured insights such as log counts, categorized errors, time-based error trends, and SQL slow-query detection.

This repository is intentionally simple in architecture while still presenting a production-style developer experience: a clear API boundary, modular parsing logic, and a readable frontend with visual charts.

## Features

- Upload `.log` and `.txt` files for analysis
- Paste raw log text directly into the web interface
- Count total logs and summarize `ERROR`, `INFO`, and `WARNING` entries
- Categorize common errors using keyword-based grouping
- Analyze errors over time by hour and identify the peak error period
- Detect SQL slow queries above 5 seconds
- Highlight the worst SQL query by duration
- Return structured JSON from the Flask backend
- Visualize results with Chart.js using:
  - error type distribution pie chart
  - errors over time line chart

## Tech Stack

- Python 3
- Flask
- HTML5
- CSS3
- Vanilla JavaScript
- Chart.js

## Project Structure

```text
Log Analyzer/
├─ app.py
├─ parser.py
├─ requirements.txt
├─ README.md
├─ templates/
│  └─ index.html
└─ static/
   └─ style.css
```

## How It Works

### Backend

- `app.py` handles HTTP routes, input validation, and JSON responses
- `parser.py` contains all log parsing and analysis logic

### Frontend

- `templates/index.html` provides the upload form, paste area, results view, and chart containers
- `static/style.css` keeps the interface clean and readable
- Vanilla JavaScript sends requests to the Flask backend using the `fetch` API and updates the page dynamically with the JSON response

## API Response Example

```json
{
  "source": "sample.log",
  "total_logs": 42,
  "error_counts": {
    "ERROR": 18,
    "INFO": 20,
    "WARNING": 4
  },
  "categorized_errors": {
    "Database": 10,
    "Timeout": 5,
    "Network": 3
  },
  "sql_analysis": {
    "slow_queries": 2,
    "worst_query": "SELECT * FROM users (12s)"
  },
  "time_analysis": {
    "errors_by_hour": {
      "10:00": 5,
      "11:00": 13
    },
    "peak_error_time": "11:00"
  }
}
```

## Run Locally

### 1. Clone or download the project

```powershell
git clone <your-repository-url>
cd "Log Analyzer"
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start the Flask development server

```powershell
python app.py
```

### 5. Open the application

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Usage

1. Upload a `.log` or `.txt` file, or paste raw logs into the text area
2. Click `Analyze Logs`
3. Review:
   - total log volume
   - error counts
   - categorized error groups
   - SQL slow-query insights
   - hourly error patterns
   - pie and line chart visualizations

## Sample Screenshots

Replace the placeholder images below with real screenshots when available.

### Dashboard

![Dashboard Placeholder](https://via.placeholder.com/1200x700?text=Log+Analyzer+Dashboard)

### Charts View

![Charts Placeholder](https://via.placeholder.com/1200x700?text=Log+Charts+View)

## Future Improvements

- Support larger log files with streamed processing
- Add filtering by log level, date range, or keyword
- Export results as JSON or CSV
- Add authentication for multi-user deployments
- Improve SQL detection with richer query pattern analysis
- Add automated tests for parser rules and API routes
- Persist uploaded analysis history

## Development Notes

- The current design keeps responsibilities separated:
  - `app.py` is the API and request layer
  - `parser.py` is the analysis engine
- The parser is intentionally rule-based and extendable without introducing unnecessary complexity

## License

This project is available for educational and internal use. Add a formal license file if you plan to distribute it publicly.

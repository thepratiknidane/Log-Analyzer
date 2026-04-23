from flask import Flask, jsonify, render_template, request

from parser import is_allowed_file, parse_log, read_log_file


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    uploaded_file = request.files.get("log_file")
    raw_log_text = request.form.get("log_text", "").strip()

    if uploaded_file and uploaded_file.filename:
        if not is_allowed_file(uploaded_file.filename):
            return jsonify(
                {"error": "Unsupported file type. Please upload a .log or .txt file."}
            ), 400

        log_text = read_log_file(uploaded_file)
        source_name = uploaded_file.filename
    elif raw_log_text:
        log_text = raw_log_text
        source_name = "Pasted text"
    else:
        return jsonify(
            {"error": "Please upload a file or paste log text to analyze."}
        ), 400

    parsed_result = parse_log(log_text)

    response_data = {
        "source": source_name,
        "total_logs": parsed_result["total_logs"],
        "error_counts": parsed_result["levels"],
        "categorized_errors": parsed_result["error_categories"],
        "sql_analysis": parsed_result["sql_analysis"],
        "time_analysis": {
            "errors_by_hour": parsed_result["errors_by_hour"],
            "peak_error_time": parsed_result["peak_error_time"],
        },
    }
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)

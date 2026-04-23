import re


ALLOWED_EXTENSIONS = {".log", ".txt"}
ERROR_CATEGORY_KEYWORDS = {
    "Database": ("database", "db", "sql"),
    "Timeout": ("timeout", "timed out"),
    "Authentication": ("auth", "login", "unauthorized", "forbidden"),
    "Network": ("network", "connection", "socket", "dns"),
    "File": ("file", "filesystem", "permission denied", "not found"),
}
SLOW_QUERY_THRESHOLD_SECONDS = 5
SLOW_QUERY_PATTERN = re.compile(
    r"query took\s+(?P<duration>\d+(?:\.\d+)?)s:\s*(?P<query>.+)",
    re.IGNORECASE,
)
ERROR_INDICATOR_PATTERN = re.compile(
    r"\b(error|exception|failed|failure|fatal|crit|critical)\b",
    re.IGNORECASE,
)


def parse_log(log_text):
    """
    Parse raw log text into a structured summary.
    """
    log_lines = [line.strip() for line in log_text.splitlines() if line.strip()]
    levels = {"ERROR": 0, "INFO": 0, "WARNING": 0}
    timestamps = []
    error_categories = {}
    errors_by_hour = {}
    slow_query_count = 0
    worst_query = None
    worst_query_duration = 0.0

    for line in log_lines:
        timestamp, level, message = parse_log_line(line)
        hour_bucket = extract_hour_bucket(timestamp)
        normalized_level = normalize_level(level, message)

        print(
            f"DEBUG parse_log_line: timestamp={timestamp!r}, "
            f"level={level!r}, normalized_level={normalized_level!r}, "
            f"message={message!r}"
        )

        if timestamp:
            timestamps.append(timestamp)

        if normalized_level in levels:
            levels[normalized_level] += 1

        if normalized_level == "ERROR":
            category = categorize_error(message)
            error_categories[category] = error_categories.get(category, 0) + 1
            if hour_bucket:
                errors_by_hour[hour_bucket] = errors_by_hour.get(hour_bucket, 0) + 1

        query_duration, query_text = extract_slow_query_details(message)
        if query_duration is not None and query_duration > SLOW_QUERY_THRESHOLD_SECONDS:
            slow_query_count += 1

            if query_duration > worst_query_duration:
                worst_query_duration = query_duration
                worst_query = format_worst_query(query_text, query_duration)

    return {
        "total_logs": len(log_lines),
        "levels": levels,
        "timestamps": timestamps,
        "error_categories": error_categories,
        "errors_by_hour": errors_by_hour,
        "peak_error_time": find_peak_error_time(errors_by_hour),
        "sql_analysis": {
            "slow_queries": slow_query_count,
            "worst_query": worst_query,
        },
    }


def parse_log_line(line):
    """
    Extract timestamp, level, and message from a log line.
    """
    parts = line.split(maxsplit=3)

    if len(parts) >= 4 and "-" in parts[0] and ":" in parts[1]:
        timestamp = f"{parts[0]} {parts[1]}"
        level = parts[2].strip("[]")
        message = parts[3]
        return timestamp, level, message

    bracket_parts = re.findall(r"\[([^\]]+)\]", line)
    if len(bracket_parts) >= 2:
        timestamp = bracket_parts[0]
        level = bracket_parts[1]
        message_parts = line.split("] ", maxsplit=3)
        message = message_parts[-1] if message_parts else line
        return timestamp, level, message

    if len(parts) >= 2:
        level = parts[0].strip("[]")
        message = " ".join(parts[1:])
        return None, level, message

    return None, None, line


def normalize_level(level, message):
    """
    Normalize different log-level variants into ERROR, INFO, or WARNING.
    """
    if level:
        normalized_level = level.strip("[]").upper()

        if normalized_level in {"ERROR", "ERR", "CRIT", "CRITICAL", "FATAL"}:
            return "ERROR"
        if normalized_level in {"WARN", "WARNING"}:
            return "WARNING"
        if normalized_level == "INFO":
            return "INFO"

    if ERROR_INDICATOR_PATTERN.search(message):
        return "ERROR"

    return None


def categorize_error(error_message):
    """
    Group similar error messages using simple keyword rules.
    """
    normalized_message = error_message.lower()

    for category, keywords in ERROR_CATEGORY_KEYWORDS.items():
        if any(keyword in normalized_message for keyword in keywords):
            return category

    return "Other"


def extract_hour_bucket(timestamp):
    """
    Convert a full timestamp like '2026-04-20 10:15:32' into '10:00'.
    """
    if not timestamp:
        return None

    parts = timestamp.split()
    if len(parts) != 2:
        return None

    time_part = parts[1]
    time_sections = time_part.split(":")
    if len(time_sections) < 2:
        return None

    return f"{time_sections[0]}:00"


def extract_slow_query_details(message):
    """
    Find SQL queries whose execution time is included in the log message.
    """
    match = SLOW_QUERY_PATTERN.search(message)
    if not match:
        return None, None

    duration = float(match.group("duration"))
    query = match.group("query").strip()
    return duration, query


def format_worst_query(query, duration):
    """
    Format the slowest query with its duration.
    """
    if duration.is_integer():
        duration_text = str(int(duration))
    else:
        duration_text = str(duration)

    return f"{query} ({duration_text}s)"


def find_peak_error_time(errors_by_hour):
    """
    Return the hour bucket with the highest error count.
    """
    if not errors_by_hour:
        return None

    return max(errors_by_hour, key=errors_by_hour.get)


def is_allowed_file(filename):
    """
    Check whether the uploaded file uses a supported extension.
    """
    if not filename:
        return False

    lower_name = filename.lower()
    return any(lower_name.endswith(extension) for extension in ALLOWED_EXTENSIONS)


def read_log_file(uploaded_file):
    """
    Read uploaded file content as text using safe decoding.
    """
    file_bytes = uploaded_file.read()
    return file_bytes.decode("utf-8", errors="replace")


def count_total_lines(log_text):
    """
    Count all lines in the uploaded log content.
    """
    return parse_log(log_text)["total_logs"]

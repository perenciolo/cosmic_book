import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "loirinha")
    user = os.environ.get("DB_USER", "marcelinhodelimaecamargo")
    db_name = os.environ.get("DB_NAME", "app")

    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5005 if host == "localhost" else os.environ.get("API_PORT", 80)

    if port is 80:
        return f"http://{host}"

    return f"http://{host}:{port}"

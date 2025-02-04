from vanna.flask import VannaFlaskApp
from vanna.remote import VannaDefault
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('VANNA_API_KEY')
vanna_model_name = os.getenv('VANNA_MODEL')
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT", "5432")  # default to 5432 if not set

vn = VannaDefault(model=vanna_model_name, api_key=api_key)

vn.connect_to_postgres(
    host=db_host,
    dbname=db_name,
    user=db_user,
    password=db_password,
    port=db_port
)

# Create Flask app
app = VannaFlaskApp(vn, title="FreshBus AI ChatBot", allow_llm_to_see_data=False, sql=False, csv_download=False,summarization=False, followup_questions=False)

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
import functions_framework

from google.cloud import bigquery
from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
import os
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor


project = os.environ["GCP_PROJECT"]
dataset = os.environ["BQ_DATASET"]
gcp_credentials = os.environ["GCP_CREDENTIALS"]
open_ai_model = os.environ["OPEN_AI_MODEL"]
sqlalchemy_url = f'bigquery://{project}/{dataset}?credentials_base64={gcp_credentials}'

db = SQLDatabase.from_uri(sqlalchemy_url)
llm = ChatOpenAI(
    model=open_ai_model,
    temperature=0,
    max_tokens=None,    
    timeout=None,
    max_retries=2,
    # api_key="...",  # if you prefer to pass api key in directly instaed of using env vars
    # base_url="...",
    # organization="...",
    # other params...
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
llm=llm,
toolkit=toolkit,
verbose=True,
max_iterations=20,
top_k=1000,
agent_type="tool-calling"
)

instruction = """You are a knowledgeable data analyst. Answer questions correctly, do not delete or alter any data and provide concise (no more than 10 words) commentary and analysis where appropriate. Do not include markdown-style triple backticks in the SQL you generate and try to use or validate. Question is: """

@functions_framework.http
def hello_http(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With'
    }

    if request.method == "OPTIONS":
        return ('', 204, headers)
    
    request_json = request.get_json(silent=True)
    request_args = request.args

    question = instruction + (request_json or request_args).get('question')

    if not question or not isinstance(question, str) or len(question) == 0:
        return ("Invalid question", 400, headers)

    answer = agent_executor.run(question)
    response = {
        "response": answer
    }
    return (answer, 200, headers)
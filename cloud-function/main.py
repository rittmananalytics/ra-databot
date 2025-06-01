import functions_framework

import os
from langchain_openai import ChatOpenAI
from langchain_looker_agent import (
    LookerSQLDatabase,
    LookerSQLToolkit,
    create_looker_sql_agent,
)
import datetime

open_ai_model = os.environ["OPEN_AI_MODEL"]
looker_instance_url = os.environ["LOOKER_INSTANCE_URL"]
lookml_model_name = os.environ["LOOKML_MODEL_NAME"]
looker_client_id = os.environ["LOOKER_CLIENT_ID"]
looker_client_secret = os.environ["LOOKER_CLIENT_SECRET"]
jdbc_driver_path = os.environ["LOOKER_JDBC_DRIVER_PATH"]

db = LookerSQLDatabase(
    looker_instance_url=looker_instance_url,
    lookml_model_name=lookml_model_name,
    client_id=looker_client_id,
    client_secret=looker_client_secret,
    jdbc_driver_path=jdbc_driver_path,
    sample_rows_in_table_info=0,
)
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

toolkit = LookerSQLToolkit(db=db)
agent_executor = create_looker_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
)

today = datetime.datetime.now()
this_year = today.year

instruction = """You are a knowledgeable data analyst and here to answer data and analytical questions. Todays date is """+ str(today) + """ and the year is """ + str(this_year) + """. 
Do not delete or alter any data and provide concise (no more than 10 words) commentary and analysis where appropriate. 
Do not use any offensive or hateful language.
Do not include markdown-style triple backticks in the SQL you generate and try to use or validate"""


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

    question = instruction + """ and filter results by user_id = """ + (request_json or request_args).get('user_id') + """ if that column is present in the table being queried. Question is: """ + (request_json or request_args).get('question')

    if not question or not isinstance(question, str) or len(question) == 0:
        return ("Invalid question", 400, headers)

    response = agent_executor.invoke({"input": question, "chat_history": []})
    answer = response.get("output")
    return (answer, 200, headers)

# ra-databot
 
# RA Databot Cloud Function

This is a Google Cloud Function that uses LangChain and OpenAI to provide answers to specific data-related questions.

## Prerequisites

- Google Cloud SDK
- Python 3.10+
- A Google Cloud project with billing enabled
- A BigQuery dataset
- Environment variables set in Google Cloud Secrets Manager. 

## Environment Variables

#### Secrets Manager
- The package uses [Google Cloud Secrets Manager](https://cloud.google.com/security/products/secret-manager) to store environment variables.  
- Functions in the config.py will to get the values for the Cloud Function to run.  
- A sample .env template is included in the root of the package (.env_local_environment_template) for local development.  
- See the Google Cloud [Quickstart](https://cloud.google.com/secret-manager/docs/create-secret-quickstart) documentation for further details.

#### OpenAI API Key
To obtain an API key for your OpenAI API account, follow these steps:

1. Log in to OpenAI:
- Go to the OpenAI website.
- Click on "Sign In" and enter your credentials to log in to your account.

2. Navigate to API Keys:
- Once logged in, select the API menu (rather than ChatGPT).

3. Generate a New API Key:
- Navigate to the API Keys section, click on "Create new secret key".
- Enter a name for your key to identify it later and click "Create key".
- Your new API key will be displayed. Make sure to copy it and store it in a secure place because you won't be able to view it again.

4. Use the API Key in Your Application:
- You can now use this API key to authenticate requests to the OpenAI API. 
- Set the key in your environment variables in Google Cloud Secrets Manager as 'OPENAI_API_KEY' and add the key to your local '.env' file if needed for local development.

## Setup

1. Clone the repository:

    ```sh
    git clone https://github.com/YOUR_USERNAME/ra-databot.git
    cd ra-databot
    ```

2. Deploy the Cloud Function:

    ```sh
    gcloud functions deploy ra-databot \
    --gen2 \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --region YOUR_REGION \
    --set-env-vars GCP_PROJECT=$GCP_PROJECT,BQ_DATASET=$BQ_DATASET,GCP_CREDENTIALS=$GCP_CREDENTIALS,OPEN_AI_MODEL=$OPEN_AI_MODEL,
    OPENAI_API_KEY=$OPENAI_API_KEY
    ```

3. Test the cloud function by using cURL to send a question:

    ```sh
    curl -X POST -H "Content-Type: application/json"  \
    --data '{"question":"and what was it in April 2024?"}' \
    https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/ra-databot
    ```

4. Within the chatbot-plugin directory, edit the chatbot.js file and add your cloud function endpoint:

    ```sh
     fetch('https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/ra-databot', requestOptions)
      .then((response) => response.text())
      .then((data) => {
        console.log('Received data:', data);
        tempBubble.innerHTML = data; // Replace the temporary bubble content with the actual response
        chatHistory += `Bot: ${data}\n`; // Append bot response to chat history
      })
      .catch((error) => {
        console.error('Error:', error);
        tempBubble.innerHTML = 'Sorry, I could not get the answer. Please try again later.';
      });
        }
    });
    ```

5. To test the chatbot front-end, open the index.html file with your browser and click on the chatbot icon in the bottom right-hand corner of the screen. 

<img src="images/chatbot.png" width="300">

The chatbot dialog will then be displayed and you can start asking questions of your data.

6. To deploy the chatbot front-end, copy the following files to your website:

-   chatbot.css
-   chatbot.js
-   images/agent.png
-   images/go.png
-   images/user.png

    Then add to the <head></head> section of the web pages you want the chatbot to be available on the following HTML code:

    ```
    <link rel="stylesheet" href="https://path/to/your/chatbot.css">
    <script src="https:////path/to/your/chatbot.js">
    ```
# How does it work?

![architecture](images/architecture.png)

1. User types in a question into the chatbot pop-up dialog interface, for example “How much were our sales in May 2024?”
2. Chatbot Javascript sends the question to the chatbot back-end service via a REST API call
3. Back-end service is a serverless Google Cloud Function which then takes the question and passes it to a LangChain SQL Agent which in-turn passes the question to OpenAI’s GPT4-Turbo LLM, prefixed with the prompt below (change this to be appropriate for your data) to come-up with a strategy to answer the user’s question:

```
    “You are a knowledgeable data analyst working for Rittman Analytics. Answer questions correctly, do not delete or alter any data and provide concise (no more than 10 words) commentary and analysis where appropriate. Use the 

    ra-development.analytics_wide.monthly_company_metrics for monthly summary KPI questions, 
    ra-development.analytics_wide.sales_leads for questions about sales leads,
    ra-development.analytics_wide.website_traffic for questions about website performance,
    ra-development.analytics_wide.sales_deals for sales pipeline and sales activity questions 

    to answer this question, and no other tables. Do not include markdown-style triple backticks in the SQL you generate and try to use or validate. Question is:”
```

4. The GPT4-Turbo LLM then sends back to the LangChain SQL agent running within the Cloud Function a series of SQL Agent tool invocations
5. Those tool invocations first read the database data dictionary, then choose the most suitable table or tables to query, then sample those tables’ contents and then write, test and then execute the correct SQL query to return the answer to the user’s query
6. The results of the SQL query are then sent-back to the GPT4-Turbo LLM so that it can add commentary around the query results
7. Those results are then sent-back to the Javascript app plugin as the REST API response
8. The results are then displayed in the chatbot UI as the answer to the users’ question. If the user asks  further questions as follow-ups to their first question, the Chatbot javascript app appends the results of previous questions in this chat to those follow-up questions so that the LLM has the context of the conversation available to it when formulating its answer.

# Update 11-07-2024

To enable the chatbot to return results scoped, for example, to a particular user ID, we added the following optional functionality:

1. To filter the results returned by the chatbot by a user ID (example), for the web page that is hosting the chatbot button and dialog, we add the following example code that sets the user ID. In-practice for Howler this would be more involved but we can simulate a user ID being passed to the chatbot in this way:

```
<div id="chatbot-button" data-user-id="Mark Rittman"></div>
```

2. The chatbot.js code has the following line added to it, which retrieves the user ID from the data attribute of the chatbot button

```
const userId = document.getElementById('chatbot-button').getAttribute('data-user-id'); // Retrieve user ID from data attribute
```

3. When the chatbot.js code then calls the back-end REST API to send across the user's question, this user ID is then added to the request body

```
const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, question: `${chatHistory}User: ${question}` })  // Include user ID in the request body
    };
```

4. Then in the cloud function back-end we include the request to filter the results by that user ID for tables that have a column for user ID; in this example I have a table that contains author names and we apply the filter to that table's queries:

```
    question = instruction + """ and filter results by authorName = """ + (request_json or request_args).get('user_id') + """ if that column is present in the table being queried. Question is: """ + (request_json or request_args).get('question')
```

# Update 12-07-2024

The code has been updated to secure access to the underlying REST API now, using an API_KEY value that you store securely in Google Cloud Secret Manager, assumption for now is that there's a single key value.

Now if you try and access the REST API and return an answer, like this:
```
curl -X POST \
  https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/ra-databot \
  -H "Content-Type: application/json" \
  -d '{"user_id":"Mark Rittman","question":"What was our sales in May 2024?"}'
```
you get the response:
```
Unauthorized% 
```

If you include the API key in the X-API-KEY header, it now works:
```
curl -X POST \
  https://YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/ra-databot \
  -H "Content-Type: application/json" \
  -H "X-API-Key: API_KEY" \
  -d '{"user_id":"Mark Rittman","question":"What was our sales in May 2024?"}'
```
you get the response:
```
Sales in May 2024 were GBP 138,671.78.% 
```

The way we implemented this was as follows:

1. We added the following to the cloud function code:
```
from google.cloud import secretmanager

def validate_api_key(request):
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return False
    
    # Retrieve the valid API key from Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.environ['GCP_PROJECT']}/secrets/API_KEY/versions/latest"
    response = client.access_secret_version(request={"name": name})
    valid_api_key = response.payload.data.decode("UTF-8")
    
    return api_key == valid_api_key
```

and then the code to return the cloud function reponse makes this additional check (the "if not validate_api_key(request)..." part)

```
@functions_framework.http
def hello_http(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, X-API-Key'
    }

    if request.method == "OPTIONS":
        return ('', 204, headers)

    if not validate_api_key(request):
        return ("Unauthorized", 401, headers)
    
    request_json = request.get_json(silent=True)
    request_args = request.args

    question = instruction + """ and filter results by authorName = """ + (request_json or request_args).get('user_id') + """ if that column is present in the table being queried. Question is: """ + (request_json or request_args).get('question')

    if not question or not isinstance(question, str) or len(question) == 0:
        return ("Invalid question", 400, headers)

    answer = agent_executor.run(question)
    response = {
        "response": answer
    }
    return (answer, 200, headers)
```

To create the API_KEY secret, we followed these steps:

1. Create a secure, random string to use as your API key.
2. Go to the Secret Manager in the Google Cloud Console.
3. Create a new secret named "API_KEY" and store your generated API key as its value.

The chatbot.jss file was updated to call the cloud function REST API:

```
function submitQuestion(question) {
  const tempBubble = addMessage('', 'bot', true);

  const requestOptions = {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'X-API-Key': 'API_KEY' 
    },
    body: JSON.stringify({ user_id: userId, question: `${chatHistory}User: ${question}` })
  };

  fetch('YOUR_REGION-YOUR_PROJECT_ID.cloudfunctions.net/ra-databot', requestOptions)
    .then((response) => response.text())
    .then((data) => {
      console.log('Received data:', data);
      tempBubble.innerHTML = data;
      chatHistory += `Bot: ${data}\n`;
    })
    .catch((error) => {
      console.error('Error:', error);
      tempBubble.innerHTML = 'Sorry, I could not get the answer. Please try again later.';
    });
}
```

Note that to securely use the X-API-Key with the JavaScript chatbot dialog, you should not include the API key directly in the client-side JavaScript.

Instead, you should set up a server-side proxy or a backend API that will add the X-API-Key to the request before forwarding it to the Cloud Function, by
1. Setting up a server-side API (e.g., using Node.js, Python, etc.) that will act as a proxy between your frontend and the Cloud Function.
2. Modifing the Javascript client-side code to send requests to your proxy server instead of directly to the Cloud Function.
3. On the proxy server, add the X-API-Key to the request headers before forwarding it to the Cloud Function.

There are other methods to secure access to a Google Cloud Function REST API but they are really outside the scope of this code example (and something you'd really want to discuss and have implemented by your dev team).


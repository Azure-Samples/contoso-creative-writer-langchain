import json
import os 
from dotenv import load_dotenv 
from pathlib import Path
from langchain_openai import AzureChatOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_prompty import create_chat_prompt

load_dotenv()

def edit(article, feedback):


    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    llm = AzureChatOpenAI(
        azure_endpoint = f"https://{os.getenv('AZURE_OPENAI_NAME')}.cognitiveservices.azure.com/", 
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        azure_ad_token_provider=token_provider,
        deployment_name=os.environ["AZURE_OPENAI_4_EVAL_DEPLOYMENT_NAME"],
    )

    PROMPT_DIR = Path(__file__).parent
    prompt_path = PROMPT_DIR /"editor.prompty"
    editor_prompt = create_chat_prompt(str(prompt_path))
    prompt = editor_prompt.invoke(input={'article':article, 'feedback':feedback})

    # Get product queries
    response = llm.invoke(prompt.messages)
    result = response.content
    
    
    return result


if __name__ == "__main__":

    result = edit(
        "Satya Nadella: A Symphony of Education",
        "no feedback"
    )
    # parse string to json
    # result = json.loads(result)
    print(result)
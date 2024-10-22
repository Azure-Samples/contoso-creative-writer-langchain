import os
import json
from pathlib import Path
import prompty
from prompty.tracer import trace
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_openai import AzureChatOpenAI
from langchain_prompty import create_chat_prompt



@trace
def write(researchContext, research, productContext, products, assignment, feedback="No Feedback"):
    # TODO: Update this once we have the logic to parse http error codes
    try:

        token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        llm = AzureChatOpenAI(
            azure_endpoint = f"https://{os.getenv('AZURE_OPENAI_NAME')}.cognitiveservices.azure.com/", 
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            azure_ad_token_provider=token_provider,
            deployment_name=os.environ["AZURE_OPENAI_4_EVAL_DEPLOYMENT_NAME"], 
            streaming=True
        )

        PROMPT_DIR = Path(__file__).parent
        prompt_path = PROMPT_DIR /"writer.prompty"
        writer_prompt = create_chat_prompt(str(prompt_path))
        prompt = writer_prompt.invoke(
            input={
                "researchContext": researchContext,
                "research": research,
                "productContext": productContext,
                "products": products,
                "assignment": assignment,
                "feedback": feedback,
            })
        
        # result = llm.stream(prompt.messages)
        # result = llm.invoke(prompt.messages).content
        for result in llm.stream(prompt.messages):
            yield result.content

    except Exception as e:
        result = {
            f"An exception occured: {str(e)}"
        }
    # return result

def process(writer):
    # parse string this chracter --- , article and feedback
    result = writer.split("---")
    article = str(result[0]).strip()
    if len(result) > 1:
        feedback = str(result[1]).strip()
    else:
        feedback = "No Feedback"

    return {
        "article": article,
        "feedback": feedback,
    }


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    
    base = Path(__file__).parent

    researchContext = (
        "Can you find the latest camping trends and what folks are doing in the winter?"
    )
    research = json.loads(Path(base / "research.json").read_text())
    productContext = "Can you use a selection of tents and backpacks as context?"
    products = json.loads(Path(base / "products.json").read_text())
    assignment = "Write a fun and engaging article that includes the research and product information. The article should be between 800 and 1000 words."
    result = write(researchContext, research, productContext, products, assignment)
    print(result)

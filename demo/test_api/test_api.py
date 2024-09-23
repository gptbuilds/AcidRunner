import aiohttp
import os
from groq import AsyncGroq
from acidrunner.decorators import use_bucket, in_files
from acidrunner.types.custom_types import AcidBoolResult

client = AsyncGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

async def fetch_transactions(query):
    url = 'https://site.com'
    params = {
        'query': query
    }
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
    }
    
    cookies = {
        'token': 'token',
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params, cookies=cookies) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {'error': f'Status code {response.status}'}

def contains_sentence_case_insensitive(text, sentence):
    return sentence.lower() in text.lower()

@use_bucket('bucket_1')
@in_files(['bool_tests.yaml'])
async def _bench_pushed_to_data_table(query) -> AcidBoolResult:
    api_res = await fetch_transactions(query)

    res = False
    if api_res['generated_text'] == 'Answer pushed to data table!':
        res = True

    return AcidBoolResult(res, meta_data={"api_data": api_res})

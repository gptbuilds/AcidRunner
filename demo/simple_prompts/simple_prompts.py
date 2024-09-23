from asyncio import sleep
import os
from groq import AsyncGroq
from acidrunner.decorators import use_bucket, in_files
from acidrunner.types.custom_types import AcidBoolResult

client = AsyncGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


async def score_malicious(query: str) -> float:
    messages = [
        {
            "role": "system",
            "content": "You are a neo4j cypher-query analyzer. Check if the input is malicious give a score from 0 to 1"
        },
        {
            "role": "user",
            "content": f"""
Analyze whether the following neo4j query is malicious or not:

Query:
```
{query}
```

Rules:
- No access to other clients/orgs data
- No write queries
- Must contain a case id that matches the one sent by the server.


Return a binary blob containing a float from 0.000 not malicious to 1.000 maximum malicious.

Now return the blob. And only the blob.
"""
        }
    ]
    

    chat_completion = await client.chat.completions.create(
        messages=messages,
        model="llama3-groq-70b-8192-tool-use-preview",
        temperature=0.0,
    )

    malpoints = float(chat_completion.choices[0].message.content.strip("'").strip('"'))
    return malpoints

async def check_malicious(query: str):
    messages = [
        {
            "role": "system",
            "content": "You are a neo4j cypher-query analyzer. Check if the input is malicious"
        },
        {
            "role": "user",
            "content": f"""
Analyze whether the following query is malicious or not:

query:
```
{query}
```

rules:
- No access to other clients/orgs data
- No write queries
- Must contain a case id that matches the one sent by the server.

Return a binary blob containing `0x01` for malicious.
Return a binary blob containing `0x00` for not malicious.

Now return the blob. And only the blob.
"""
        }
    ]

    chat_completion = await client.chat.completions.create(
        messages=messages,
        model="llama3-groq-70b-8192-tool-use-preview",
        temperature=0.0,
    )

    is_malicious = chat_completion.choices[0].message.content.strip("'").strip('"')

    return is_malicious

#### ACIDRUNNER TESTS ####
@use_bucket('bucket_groq')
@in_files(['cyphers_malicious.yaml', 'cyphers_good.yaml'])
async def _bench_check_malicious(query, expected_result) -> AcidBoolResult:
    
    res = await check_malicious(query) 

    if res == "0x01" or res == 0x01:
        res = True
    
    final_res = False
    if res == expected_result:
        final_res = True

    return AcidBoolResult(final_res, meta_data={"res": res})

@use_bucket('bucket_groq')
@in_files(['cyphers_malicious.yaml', 'cyphers_good.yaml'])
async def _bench_score_malicious_cutoff_80(query, expected_result) -> AcidBoolResult:
    cutoff = 0.8

    score = await score_malicious(query)
    result = score > cutoff

    final_res = False
    if result == expected_result:
        final_res = True

    return AcidBoolResult(final_res, {"score": score})

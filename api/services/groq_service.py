import requests
import json
from groq import Groq
from decouple import config

# URLS AND LLM MODEL
foursquare_details_url = 'https://api.foursquare.com/v3/places/'
foursquare_search_url = 'https://api.foursquare.com/v3/places/search'
groq_meta_model = "meta-llama/llama-4-scout-17b-16e-instruct"

# API KEYS
ALLOWED_KEYS = {'query', 'near', 'open_now', 'max_price', 'hours'}
GROQ_CONTEXT = 'you are an ai agent thats going to parse customer query looking for a restaurant, please restrict your response to a json with no explaination on how you achieved the result, return a json from their prompt in the following format, with max_price being a range between 1 and 4, with 4 being the most expensive: "action": "restaurant_search", "parameters": ["query": "sushi", "near": "downtoan Los Angeles", "max_price": "1". "open_now": true"]'
FOURSQUARE_API_KEY = config('FOURSQUARE_API_KEY')
GROQ_API_KEY = config('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)


def get_cuisine_string(categories):
    if not categories:
        return 'Unknown'
    return ', '.join([cat.get('name', 'Unknown') for cat in categories])

# GET MORE DETAILS FROM SPECIFIC FSQ_ID
def fetch_details(fsq_id, field):
    headers = {
        "accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    response = requests.get(url=foursquare_details_url+fsq_id+field, headers=headers)
    data = response.json()
    return data

# GET BASIC RESTAURANT DETAILS
def resto_search(data):
    
    params_raw = data.get("parameters", {})
    params = {k: v for k, v in params_raw.items() if k in ALLOWED_KEYS}
    print('params: ', params)

    headers = {
        "accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }

    try:
        response = requests.get(url=foursquare_search_url, headers=headers, params=params)
        response.raise_for_status
        foursq_results = response.json()
        # print(foursq_results)

        results = foursq_results.get("results", [])
        if not results:
            print("Foursquare returned no results.")
            return

    except requests.exceptions.RequestException as e:
        print('Error fetching data from Foursquare: ', e)
    except ValueError as ve:
        print('Error decoding JSON: ', ve)

    restaurants = []
    for result in results:
        name = result.get('name')
        address = result.get('location', {}).get('formatted_address', 'Unknown address')
        cuisine = get_cuisine_string(result.get('categories', []))
        rating = fetch_details(result.get('fsq_id'), '?fields=rating').get('rating')
        price = fetch_details(result.get('fsq_id'), '?fields=price').get('price')
        hours = fetch_details(result.get('fsq_id'), '?fields=hours').get('hours')
        # categories = result.

        print(f"Name: {name}\nAddress: {address}\nCuisine: {cuisine}\nRating: {rating}\nPrice: {price}\nHours: {hours}\n{'-'*40}")

        restaurants.append({
            "name": name,
            "address": address,
            "cuisine": cuisine,
            "rating": rating,
            "price": price,
            "hours": hours
        })

    return {"restaurants": restaurants}

def draft_message(content, role='user'):
    return {
        "role": role,
        "content": content
    }

# CALL GROQ TO PARSE USER PROMPT
def groq_call(prompt):
    messages = [
        {
            'role': 'system',
            'content': GROQ_CONTEXT
        }
    ]

    messages.append(draft_message(prompt))

    chat_completion = client.chat.completions.create(
        temperature = 1.0,
        n = 1,
        model = groq_meta_model,
        max_tokens = 1000,
        messages = messages
    )

    chat_completion.usage.total_tokens

    response = chat_completion.choices[0].message.content
    try: 
        data = json.loads(response.replace("```", "").strip())
    except json.JSONDecodeError as e:
        print("Failed to decode response as JSON: ", response)
    
    print(data)
    # print(data["parameters"]["query"])
    return resto_search(data)



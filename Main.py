import os
import random
from pyrogram import Client, filters
from pyrogram.types import Message
import wolframalpha
import wikipedia
import requests
from PIL import Image, ImageDraw, ImageFont

wolfram_app_id = "J6PGKG-GRT9RAP4X6"
API_ID = 6067591
API_HASH = "94e17044c2393f43fda31d3afe77b26b"
TOKEN = "8022539593:AAFeCi9zs-OAE7w3Iv_feEQjBDqGR3bptCc"

app = Client(
    name="Player", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN
)

def solve_numerical_problem(query: str) -> str:
    client = wolframalpha.Client(wolfram_app_id)
    try:
        res = client.query(query)
        return next(res.results).text
    except StopIteration:
        return "No solution found."

def get_wikipedia_summary(query: str) -> str:
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found for this query."
    except Exception as e:
        return f"Error fetching Wikipedia data: {e}"

def get_duckduckgo_answer(query: str) -> str:
    url = f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1"
    response = requests.get(url)
    data = response.json()
    
    try:
        return data["AbstractText"] or "No detailed answer found."
    except KeyError:
        return "No instant answer found."

def get_pubchem_chemical_info(query: str) -> str:
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query}/JSON"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('PropertyTable'):
            compound_info = data['PropertyTable']['Properties'][0]
            return f"Name: {compound_info.get('IUPACName', 'N/A')}\n" \
                   f"Formula: {compound_info.get('MolecularFormula', 'N/A')}\n" \
                   f"Mass: {compound_info.get('MolecularWeight', 'N/A')}\n" \
                   f"SMILES: {compound_info.get('SMILES', 'N/A')}"
        else:
            return "No information available for this compound."
    else:
        return "Failed to retrieve data from PubChem."

def generate_image_response(text: str) -> str:
    img = Image.new('RGB', (600, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.text((10, 10), text, font=font, fill=(0, 0, 0))

    file_name = f"response_{random.randint(1000, 9999)}.png"
    img.save(file_name)
    
    return file_name

@app.on_message(filters.command("doubt") & filters.private)
async def handle_doubt(client: Client, message: Message):
    question = message.text.split(maxsplit=1)[1]

    if "math" in question or "physics" in question:
        answer = solve_numerical_problem(question)
    elif "chemistry" in question:
        answer = get_pubchem_chemical_info(question)
    else:
        wikipedia_answer = get_wikipedia_summary(question)
        if wikipedia_answer == "No Wikipedia page found for this query.":
            answer = get_duckduckgo_answer(question)
        else:
            answer = wikipedia_answer

    response_img = generate_image_response(answer)

    await message.reply_photo(photo=response_img)

    os.remove(response_img)

app.run()

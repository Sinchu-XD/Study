import os
import asyncio
import random
from pyrogram import Client, filters, idle
from pyrogram.types import Message
import wolframalpha
import wikipedia
import requests
from PIL import Image, ImageDraw, ImageFont

wolfram_app_id = "J6PGKG-GRT9RAP4X6"
API_ID = 6067591
API_HASH = "94e17044c2393f43fda31d3afe77b26b"
TOKEN = "8022539593:AAFeCi9zs-OAE7w3Iv_feEQjBDqGR3bptCc"

app = Client("DoubtSolverBot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

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
        return data.get("AbstractText", "No detailed answer found.")
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
    img = Image.new('RGB', (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    lines = []
    words = text.split()
    line = ""
    for word in words:
        if len(line + word) < 70:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)
    y = 10
    for line in lines:
        draw.text((10, y), line, font=font, fill=(0, 0, 0))
        y += 20
    file_name = f"response_{random.randint(1000, 9999)}.png"
    img.save(file_name)
    return file_name

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text(
        "👋 Hello! I’m your NEET/JEE Doubt Solver Bot.\n\n"
        "Send any doubt using:\n"
        "`/doubt your question`\n\n"
        "I’ll answer it with proper solutions and concepts!"
    )

@app.on_message(filters.command("doubt") & filters.private)
async def handle_doubt(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Please ask a doubt like:\n`/doubt What is H2O?`")
        return
    question = message.text.split(maxsplit=1)[1].strip().lower()
    if any(x in question for x in ["math", "physics", "+", "-", "*", "/", "integrate", "derive", "solve"]):
        answer = solve_numerical_problem(question)
    elif any(x in question for x in ["chemistry", "compound", "element", "acid", "base"]):
        answer = get_pubchem_chemical_info(question)
    else:
        wiki = get_wikipedia_summary(question)
        answer = wiki if "No Wikipedia page found" not in wiki else get_duckduckgo_answer(question)
    image_path = generate_image_response(answer)
    await message.reply_photo(image_path)
    os.remove(image_path)

async def main():
    await app.start()
    print("✅ Bot is running...")
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
    

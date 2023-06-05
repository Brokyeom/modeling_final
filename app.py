import gradio as gr
import openai
import os
import geocoder
import requests
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
API_KEY = os.getenv("WEATHER_SERVICE_KEY")

def get_weather(lat, long):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&lang=kr&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    city = data['name']
    weather = data['weather'][0]['main']
    temp = data['main']['temp']

    return city, weather, temp

def get_location():
    try:
        g = geocoder.ip('me')
        return g.lat, g.lng
    except Exception as e:
        print("Can't find you. No weather for you.")

def chat_with_gpt(input_text, city, weather, temp):
    messages = [
        {"role": "system", "content": "오늘 기온에 맞춰 오늘 작물에게 맞는 행동을 추천해야 합니다. 사용자가 특정 작물과 현재 기온에 대한 정보를 제공하면, 해당 기온에서의 작물 관리에 대한 오늘 하루 관리법을 제공해야 합니다."},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "user", "content": f'나는 {input_text} 를 기르고 있어. 여기는 {city}이고, 날씨는 {weather}하며, 기온은 섭씨{temp}도야 오늘 하루 {input_text}가 잘 자라게 하는 방법에는 무엇이 있을까?'}
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1
    )

    assistant_content = completion.choices[0].message['content'].strip()

    return assistant_content

def handle_chat(input_text):
    lat, lon = get_location()  # 사용자의 위도와 경도를 얻습니다.
    city, weather, temp = get_weather(lat, lon)  # 사용자의 위치에서의 현재 기온을 얻습니다.
    assistant_reply = chat_with_gpt(input_text, city, weather, temp)  # GPT와 대화를 합니다.

    return assistant_reply

iface = gr.Interface(
    fn=handle_chat, 
    inputs=gr.inputs.Textbox(label="작물 이름을 입력하세요"),
    outputs=gr.outputs.Textbox(label="답변"), 
    title="오늘의 관리법",
)

iface.launch()

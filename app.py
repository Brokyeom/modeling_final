import gradio as gr # gradio 라이브러리
import openai # openai 라이브러리
import os # 환경변수를 읽기위한 os 라이브러리
import geocoder # 위도 경도 정보를 받아오기 위한 라이브러리
import requests # api에게 요청을 보내기 위한 requests 라이브러리
from dotenv import load_dotenv # 디렉토리 내 .env 파일을 불러오기 위한 라이브러리

load_dotenv() # .env 파일 불러오기

openai.api_key = os.getenv("OPENAI_API_KEY") # openai api key 가져오기
API_KEY = os.getenv("WEATHER_SERVICE_KEY") # 날씨 api key 가져오기

# 위도, 경도 정보를 가져오는 함수
def get_location():
    try:
        g = geocoder.ip('me')
        return g.lat, g.lng
    except Exception as e:
        print("Error : 위치를 찾지 못했습니다.")

# 날씨 정보를 가져오는 함수
def get_weather(lat, long): # 인자로 위도, 경도를 받습니다.
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&lang=kr&appid={API_KEY}&units=metric" # api 호출 엔드포인트
    response = requests.get(url) # 해당 엔드포인트로 GET 요청
    data = response.json() # 받아온 data 를 json 형식의 딕셔너리로 변환
    city = data['name'] # data 딕셔너리의 'name' key 의 value 를 city 에 저장
    weather = data['weather'][0]['main'] # data 딕셔너리의 'weather' key의 첫 번째 값의 'main' key 의 value 를 weahter 에 저장.
    temp = data['main']['temp'] # data 딕셔너리의 'main' 'temp' key의 value 를 temp 에 저장.

    return city, weather, temp # 저장한 값들을 튜플 형식으로 return.

# LLM 적용 함수
def chat_with_gpt(input_text, city, weather, temp):
    # LLM 에게 역할 부여, 답변 양식 학습, 사용자의 질문을 딕서녀리 형태의 prompt로 학습시킵니다.
    messages = [
        # LLM 에게 역할을 부여하는 system role.
        {"role": "system", "content": "오늘 기온에 맞춰 오늘 작물에게 맞는 행동을 추천해야 합니다. 사용자가 특정 작물과 현재 기온에 대한 정보를 제공하면, 해당 기온에서의 작물 관리에 대한 오늘 하루 관리법을 제공해야 합니다."},
        # LLM 의 답변 형식을 학습시키는 assistant role.
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        {"role": "assistant", "content": f'오늘 {city}의 날씨는 {weather}하며 가온은 {temp}도입니다. 오늘같은 날씨는 {input_text}에게 ~~ 한 날씨입니다. 오늘 하루 다음과 같이 행동하는 것을 추천합니다: 1. ~~ 2. ~~ 3. ~~'},
        # user 의 답변을 LLM 에게 부여하는 딕셔너리 형태의 질문.
        {"role": "user", "content": f'나는 {input_text} 를 기르고 있어. 여기는 {city}이고, 날씨는 {weather}하며, 기온은 섭씨{temp}도야 오늘 하루 {input_text}가 잘 자라게 하는 방법에는 무엇이 있을까?'}
    ]

    # LLM 을 생성하는 함수.
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", # chatGPT 3.5 turbo 모델을 사용합니다.
        messages=messages,
        temperature=1 # 답변의 다양성을 최대로 설정합니다.(0에서 1로 갈수록 답변의 엔트로피가 높아집니다.)
    )

    # LLM 의 답변을 받아 변수에 저장합니다.
    assistant_content = completion.choices[0].message['content'].strip()

    return assistant_content # 답변을 return 합니다.

# 위에서 정의한 함수를 모두 실행하여 채팅 로직을 구현하는 함수.
def handle_chat(input_text):
    lat, lon = get_location()  # 사용자의 위도와 경도를 얻습니다.
    city, weather, temp = get_weather(lat, lon)  # 사용자의 현재 위치, 오늘 날씨, 기온 정보를 위도 경도를 통해 얻습니다.
    assistant_reply = chat_with_gpt(input_text, city, weather, temp)  # GPT와 대화를 합니다.

    return assistant_reply # 답변을 return 합니다.

# 위에서 작성한 로직을 gradio interface 에서 보여지게 하는 메서드
iface = gr.Interface(
    fn=handle_chat, # 인터페이스 내에서 사용되는 함수. handle_chat 을 사용하여 로직을 실행하도록 합니다.
    inputs=gr.inputs.Textbox(label="작물 이름을 입력하세요"), # input 값을 받습니다.
    outputs=gr.outputs.Textbox(label="답변"), # handle_chat 함수의 return 값 즉, assistant_reply 를 출력합니다.
    title="오늘의 관리법", # 인터페이스의 제목을 설정합니다.
)

iface.launch() # gradio interface 실행.

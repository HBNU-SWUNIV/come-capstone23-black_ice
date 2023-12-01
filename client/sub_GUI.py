import paho.mqtt.client as mqtt
import json
import tkinter as tk
from datetime import datetime


mqtt_scheme = "***"  # 프로토콜 선택 (mqtt 또는 tcp)
mqtt_host = "***.***.***.***"  # 브로커 주소
mqtt_port = ****  # 브로커 포트
mqtt_topic = "********"  # 기본 토픽 설정
mqtt_qos = 1  # QoS 레벨 설정
mqtt_topics_vector = '*********#'  # 벡터 토픽 설정
mqtt_username = "**********"  # 사용자명
mqtt_password = "*******************"  # 비밀번호



def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    data = json.dumps(msg.payload.decode("utf-8"))
    data = eval(json.loads(data))
    daytime = datetime.now().strftime('%Y%m%d%H%M')
    if data['device_name'] != '보조 분류AI용 USB카메라 이미지':
        if data['edge_time']!= None:
            daytime = data['edge_time'][:12]
        else:
            if data['API_time'] == None:
                pass
            else:
                daytime = data['API_time']
        del data['device']
        del data['edge_time']
        print(daytime)
        print(*data.keys())
        print(*data.values())
        print()
    
    update_gui(daytime, data, data['device_name'])
    


def update_gui(daytime, data, category):
    dt = datetime.strptime(daytime, '%Y%m%d%H%M')
    label_date.config(text = dt.strftime('%Y.%m.%d.(%a)  %H:%M'))

    if category == 'Envsensor':
        label_result_atm_temp.config(text = data['temperature'])
        label_result_humid.config(text = data['humidity'])
        label_result_rain.config(text = data['rain_level'])
        label_result_wind.config(text = data['wind_velocity'])
        label_result_light.config(text = data['uva'])
        
    elif category == 'GroundTemperature':
        label_result_surf_temp.config(text= data['surface_temperature_3'])

    elif category == '기상청API(날씨)':
        #label_surface.config(text=_msg(column, value))
        pass

    elif category == 'AI 예측':
        dt = data['temperature_1h']
        dh = data['humidity_1h']
        ds = data['surface_temperature_1h']
        dw = data['weather_1h']
        label_result_AI_onehour.config(text = f'대기온도:{dt} / 습도:{dh}\n노면온도:{ds} / 날씨:{dw}')

        dt = data['temperature_2h']
        dh = data['humidity_2h']
        ds = data['surface_temperature_2h']
        dw = data['weather_2h']
        label_result_AI_twohour.config(text = f'대기온도:{dt} / 습도:{dh}\n노면온도:{ds} / 날씨:{dw}')
        pass

    elif category == 'AI 빙결분류':
        ##label_AI.config(text=_msg(column, value))
        label_result_state_now.config(text= data['frozen_classification_0h'])
        label_result_state_onehour.config(text= data['frozen_classification_1h'])
        label_result_state_twohour.config(text= data['frozen_classification_2h'])
        pass

    elif category == '보조 분류AI용 USB카메라 이미지':
        #label_surface.config(text=_msg(column, value))
        pass

    elif category == '이미지 기반 보조 AI 빙결분류':
        #label_surface.config(text=_msg(column, value))
        pass




# MQTT setup
client = mqtt.Client()
client.username_pw_set(username=mqtt_username, password=mqtt_password)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message

client.connect(mqtt_host, mqtt_port)# 로컬 아닌, 원격 mqtt broker에 연결
client.subscribe(mqtt_topics_vector, mqtt_qos)# 토픽 구독





# Tkinter GUI setup
window = tk.Tk()
window.title("MQTT Data Display")
window.geometry("1200x700")


## PLACE
left_top=tk.Frame(window, relief="solid", bd=2, width=600, height=350)
left_top.pack(side="left", fill="both", expand=True)
left_top.place(x=0,y=0)

left_bottom=tk.Frame(window, relief="solid", bd=2, width=600, height=350)
left_bottom.pack(side="left", fill="both", expand=True)
left_bottom.place(x=0,y=350)

right_top=tk.Frame(window, relief="solid", bd=2, width=600, height=350)
right_top.pack(side="right", fill="both", expand=True)
right_top.place(x=600,y=0)

right_bottom=tk.Frame(window, relief="solid", bd=2, width=600, height=350)
right_bottom.pack(side="right", fill="both", expand=True)
right_bottom.place(x=600,y=350)



# 날짜/시간 정보
label_date = tk.Label(left_top, text="날짜/시간 정보", bd=3, width=42, height=1, font=("Helvetica", 17, "bold"), bg='gray19', fg='gray90')
label_date.place(x=0,y=0)

# - 날짜/시간
result_date = datetime.now().strftime('%Y.%m.%d  %H:%M')

label_date = tk.Label(left_top, text=result_date, width=35, font=("Helvetica", 20), fg='gray1')
label_date.place(x=15,y=75)



# 위치 정보
label_env = tk.Label(left_top, text="위치 정보", bd=3, width=42, height=1, font=("Helvetica", 17, "bold"), bg='gray19', fg='gray90')
label_env.place(x=0,y=160)

# - 위도
label_lat = tk.Label(left_top, text="위도", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_lat.place(x=0,y=210)

result_lat = "샘플 텍스트1"

label_result_lat = tk.Label(left_top, text=result_lat, width=25, font=("Helvetica", 20), fg='gray1')
label_result_lat.place(x=100,y=220)

# - 경도
label_long = tk.Label(left_top, text="경도", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_long.place(x=0,y=270)

result_long = "샘플 텍스트2"

label_result_long = tk.Label(left_top, text=result_long, width=25, font=("Helvetica", 20), fg='gray1')
label_result_long.place(x=100,y=280)



# 센서 데이터
label_surface = tk.Label(left_bottom, text="센서 데이터", bd=3, width=42, height=1, font=("Helvetica", 17, "bold"), bg='gray19', fg='gray90')
label_surface.place(x=0,y=0)

# - 대기온도
label_atm_temp = tk.Label(left_bottom, text="대기온도", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_atm_temp.place(x=0,y=50)

result_atm_temp = "샘플 텍스트3"

label_result_atm_temp = tk.Label(left_bottom, text=result_atm_temp, width=10, font=("Helvetica", 21), fg='gray1')
label_result_atm_temp.place(x=100,y=80)

# - 노면온도
label_surf_temp = tk.Label(left_bottom, text="노면온도", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_surf_temp.place(x=300,y=50)

result_surf_temp = "샘플 텍스트4"

label_result_surf_temp = tk.Label(left_bottom, text=result_surf_temp, width=10, font=("Helvetica", 21), fg='gray1')
label_result_surf_temp.place(x=400,y=80)

# - 습도
label_humid = tk.Label(left_bottom, text="습도", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_humid.place(x=0,y=140)

result_humid = "샘플 텍스트5"

label_result_humid = tk.Label(left_bottom, text=result_humid, width=10, font=("Helvetica", 21), fg='gray1')
label_result_humid.place(x=100,y=170)

# - 강수
label_rain = tk.Label(left_bottom, text="강수레벨", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_rain.place(x=300,y=140)

result_rain = "샘플 텍스트6"

label_result_rain = tk.Label(left_bottom, text=result_rain, width=10, font=("Helvetica", 21), fg='gray1')
label_result_rain.place(x=400,y=170)

# - 풍속
label_wind = tk.Label(left_bottom, text="풍속", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_wind.place(x=0,y=230)

result_wind = "샘플 텍스트7"

label_result_wind = tk.Label(left_bottom, text=result_wind, width=10, font=("Helvetica", 21), fg='gray1')
label_result_wind.place(x=100,y=260)

# - 광량
label_light = tk.Label(left_bottom, text="자외선(UV)", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_light.place(x=300,y=230)

result_light = "샘플 텍스트8"

label_result_light = tk.Label(left_bottom, text=result_light, width=10, font=("Helvetica", 21), fg='gray1')
label_result_light.place(x=400,y=260)



# AI 예측 데이터
label_AI = tk.Label(right_top, text="AI 예측 데이터", bd=3, width=42, height=1, font=("Helvetica", 17, "bold"), bg='gray19', fg='gray90')
label_AI.place(x=0,y=0)

# - 1시간 후
label_AI_onehour = tk.Label(right_top, text="1시간 후", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_AI_onehour.place(x=0,y=50)

result_AI_onehour = "샘플 텍스트9"

label_result_AI_onehour = tk.Label(right_top, text=result_AI_onehour, height=3, width=37, font=("Helvetica", 18), fg='gray1')
label_result_AI_onehour.place(x=36,y=80)

# - 2시간 후
label_AI_twohour = tk.Label(right_top, text="2시간 후", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_AI_twohour.place(x=0,y=190)

result_AI_twohour = "샘플 텍스트10"

label_result_AI_twohour = tk.Label(right_top, text=result_AI_twohour, height=3, width=37, font=("Helvetica", 18), fg='gray1')
label_result_AI_twohour.place(x=36,y=220)



# 노면 상태 분류
label_state = tk.Label(right_bottom, text="노면 상태 분류", bd=3, width=42, height=1, font=("Helvetica", 17, "bold"), bg='gray19', fg='gray90')
label_state.place(x=0,y=0)

# - 현재 상태
label_state_now = tk.Label(right_bottom, text="현재 상태", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_state_now.place(x=0,y=50)

result_state_now = "샘플 텍스트11"

label_result_state_now = tk.Label(right_bottom, text=result_state_now, width=13, font=("Helvetica", 30), fg='gray1')
label_result_state_now.place(x=150,y=80)

# - 1시간 후 상태
label_state_onehour = tk.Label(right_bottom, text="1시간 후 상태", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_state_onehour.place(x=0,y=140)

result_state_onehour = "샘플 텍스트12"

label_result_state_onehour = tk.Label(right_bottom, text=result_state_onehour, width=13, font=("Helvetica", 30), fg='gray1')
label_result_state_onehour.place(x=150,y=170)

# - 2시간 후 상태
label_state_twohour = tk.Label(right_bottom, text="2시간 후 상태", height=1, padx=10, pady=1, font=("Helvetica", 16, "bold"), fg='gray1')
label_state_twohour.place(x=0,y=230)

result_state_twohour = "샘플 텍스트13"

label_result_state_twohour = tk.Label(right_bottom, text=result_state_twohour, width=13, font=("Helvetica", 30), fg='gray1')
label_result_state_twohour.place(x=150,y=260)





client.loop_start() # Start the MQTT client loop in a separate thread
window.mainloop() # Start the Tkinter main loop
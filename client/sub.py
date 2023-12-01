import paho.mqtt.client as mqtt #pip install paho-mqtt  
import json


mqtt_scheme = "tcp"  # 프로토콜 선택 (mqtt 또는 tcp)
mqtt_host = "121.124.124.20"  # 브로커 주소
mqtt_port = 1883  # 브로커 포트
mqtt_topic = "innoroad"  # 기본 토픽 설정
mqtt_qos = 1  # QoS 레벨 설정
mqtt_topics_vector = 'innoroad/#'  # 벡터 토픽 설정
mqtt_username = "sjmqtt"  # 사용자명
mqtt_password = "sj9337700mqtt"  # 비밀번호


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
    try:
        data = json.dumps(msg.payload.decode("utf-8"))
        data = eval(json.loads(data))

        daytime = 'Data Empty'
        if data['device_name'] != '보조 분류AI용 USB카메라 이미지':
            if data['edge_time']!= None:
                daytime = data['edge_time'][:12]
            else:
                if data['API_time'] == None:
                    daytime = 'Data Empty'
                else:
                    daytime = data['API_time']
            del data['device']
            del data['edge_time']
            print(daytime)
            print(*data.keys())
            print(*data.values())
            print()
    except Exception as e:
        print(f"An error occurred: {e}")


# 새로운 클라이언트 생성
client = mqtt.Client()
client.username_pw_set(username=mqtt_username, password=mqtt_password)
# 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_subscribe(topic 구독),
# on_message(발행된 메세지가 들어왔을 때)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message



# 로컬 아닌, 원격 mqtt broker에 연결
client.connect(mqtt_host, mqtt_port)

# 토픽 구독
client.subscribe(mqtt_topics_vector, mqtt_qos)
client.loop_forever()
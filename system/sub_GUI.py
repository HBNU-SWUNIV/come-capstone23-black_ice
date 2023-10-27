import paho.mqtt.client as mqtt
import json
import tkinter as tk

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
    data = json.loads(msg.payload.decode("utf-8"))
    #print(data)
    daytime = 'Data Empty'
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
    
    if data.keys() != None and data.values() != None:
        update_gui(daytime, list(data.keys()), list(data.values()), data['device_name'])
    else:
        update_gui(daytime, data.keys(), data.values(), data['device_name'])


def _msg(column, value):
    msg = ''
    for i in range(len(column)):
        msg = msg + f'{column[i]} : {value[i]}\n'
    return msg


def update_gui(daytime, column, value, category):
    label_date.config(text = daytime)

    #print(column)
    #print(value)

    if category == 'Envsensor':
        label_env.config(text=_msg(column, value))

    elif category == 'GroundTemperature':
        label_surface.config(text=_msg(column, value))

    elif category == '기상청API(날씨)':
        #label_surface.config(text=_msg(column, value))
        pass

    elif category == 'AI 빙결예측':
        label_AI.config(text=_msg(column, value))
        pass

    elif category == '보조 분류AI용 USB카메라 이미지':
        #label_surface.config(text=_msg(column, value))
        pass

    elif category == '이미지 기반 보조 AI 빙결분류':
        #label_surface.config(text=_msg(column, value))
        pass




# MQTT setup
client = mqtt.Client()
client.username_pw_set(username="sjmqtt", password="sj9337700mqtt")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message
client.connect('qio.kr', 1883)
client.subscribe('innoroad/48B02DD4050F.231010/event/up', 1)





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




label_date = tk.Label(left_top, font=("Helvetica", 20), bg='gray19', fg='gray60')
label_date.pack(side="left")
label_date.place(x=0,y=10)


label_env = tk.Label(left_top, font=("Helvetica", 16), bg='gray19', fg='gray60')
label_env.pack(side="left")
label_env.place(x=0,y=50)


label_surface = tk.Label(left_bottom, font=("Helvetica", 16), bg='gray19', fg='gray60')
label_surface.pack(side="left")
label_surface.place(x=0,y=10)

label_AI = tk.Label(right_top, font=("Helvetica", 16), bg='gray19', fg='gray60')
label_AI.pack(side="left")
label_AI.place(x=0,y=10)





client.loop_start() # Start the MQTT client loop in a separate thread
window.mainloop() # Start the Tkinter main loop
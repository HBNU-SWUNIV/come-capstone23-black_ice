/*******************************************************************************
 * Copyright (c) 2012, 2022 IBM Corp., Ian Craggs
 *
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v2.0
 * and Eclipse Distribution License v1.0 which accompany this distribution. 
 *
 * The Eclipse Public License is available at 
 *   https://www.eclipse.org/legal/epl-2.0/
 * and the Eclipse Distribution License is available at 
 *   http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * Contributors:
 *    Ian Craggs - initial contribution
 *******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "MQTTAsync.h"
#include <dotenv.h>
#include <json-c/json.h>
#include <time.h>


#if !defined(_WIN32)
#include <unistd.h>
#else
#include <windows.h>
#endif

#if defined(_WRS_KERNEL)
#include <OsWrapper.h>
#endif

//#define ADDRESS     "tcp://mqtt.eclipseprojects.io:1883"
//#define ADDRESS     "tcp://175.207.12.148:1883"
//#define CLIENTID    "ExampleClientSub"
//#define TOPIC       "innoroad/#"
#define PAYLOAD     "Hello World!"
#define QOS         1
#define TIMEOUT     10000L

#include <uuid/uuid.h>

char quuid[37];
char address[256];
char topic[256];
char streamKey[256];


int disc_finished = 0;
int subscribed = 0;
int finished = 0;

void onConnect(void* context, MQTTAsync_successData* response);
void onConnectFailure(void* context, MQTTAsync_failureData* response);

void connlost(void *context, char *cause)
{
	MQTTAsync client = (MQTTAsync)context;
	MQTTAsync_connectOptions conn_opts = MQTTAsync_connectOptions_initializer; // https://eclipse.dev/paho/files/mqttdoc/MQTTAsync/html/struct_m_q_t_t_async__connect_options.html
	int rc;

	printf("\nConnection lost\n");
	if (cause)
		printf("     cause: %s\n", cause);

	printf("Reconnecting\n");
	
	conn_opts.username = "sjmqtt";
	conn_opts.password = "sj9337700mqtt";
	// -u 'sjmqtt' -P 'sj9337700mqtt'
	
	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	conn_opts.onSuccess = onConnect;
	conn_opts.onFailure = onConnectFailure;
	conn_opts.context = client;
	if ((rc = MQTTAsync_connect(client, &conn_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start connect, return code %d\n", rc);
		finished = 1;
	}
}


int msgarrvd(void *context, char *topicName, int topicLen, MQTTAsync_message *message)
{
    printf("Message arrived\n");
    printf("     topic: %s\n", topicName);
    printf("   message: %.*s\n", message->payloadlen, (char*)message->payload);
	
	json_object *jobj;
	json_object *jval;

	jobj = json_tokener_parse((char*)message->payload);
	printf("jobj from message:\n---\n%s\n---\n", json_object_to_json_string_ext(jobj, JSON_C_TO_STRING_SPACED | JSON_C_TO_STRING_PRETTY));
	
	jval = json_object_object_get(jobj, "type");
	printf("jobj->seq = %d\n", json_object_get_int(jval));
	jval = json_object_object_get(jobj, "temp1");
	printf("jobj->temp1 = %d\n", json_object_get_int(jval));
	jval = json_object_object_get(jobj, "temp2");
	printf("jobj->temp2 = %d\n", json_object_get_int(jval));
	jval = json_object_object_get(jobj, "temp3");
	printf("jobj->temp3 = %d\n", json_object_get_int(jval));
	jval = json_object_object_get(jobj, "temp4");
	printf("jobj->temp4 = %d\n", json_object_get_int(jval));
	jval = json_object_object_get(jobj, "temp5");
	printf("jobj->temp5 = %d\n", json_object_get_int(jval));
	jval = json_object_object_get(jobj, "timestamp");
	printf("jobj->timestamp = %s\n", json_object_get_string(jval));

    MQTTAsync_freeMessage(&message);
    MQTTAsync_free(topicName);
    return 1;
}

void onDisconnectFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Disconnect failed, rc %d\n", response->code);
	disc_finished = 1;
}

void onDisconnect(void* context, MQTTAsync_successData* response)
{
	printf("Successful disconnection\n");
	disc_finished = 1;
}

void onSubscribe(void* context, MQTTAsync_successData* response)
{
	printf("Subscribe succeeded\n");
	subscribed = 1;
}

void onSubscribeFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Subscribe failed, rc %d\n", response->code);
	finished = 1;
}


void onConnectFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Connect failed, rc %d\n", response->code);
	finished = 1;
}


void onConnect(void* context, MQTTAsync_successData* response)
{
	MQTTAsync client = (MQTTAsync)context;
	MQTTAsync_responseOptions opts = MQTTAsync_responseOptions_initializer;
	int rc;

	printf("Successful connection\n");

	printf("Subscribing to topic %s\nfor client %s using QoS%d\n\n"
           "Press Q<Enter> to quit\n\n", topic, quuid, QOS);
	opts.onSuccess = onSubscribe;
	opts.onFailure = onSubscribeFailure;
	opts.context = client;
	if ((rc = MQTTAsync_subscribe(client, topic, QOS, &opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start subscribe, return code %d\n", rc);
		finished = 1;
	}
}


int main(int argc, char* argv[])
{
	int i = env_load( "/webservice/.env.innoroad", false );
	printf("i = %d\n", i);
	
	sprintf( address, "mqtt://%s:%s", getenv( "mqtt.ip" ), getenv( "mqtt.port" ) );
	printf("address = %s\n", address);
	
	sprintf( topic, "%s", getenv( "mqtt.topic" ) );
	printf("topic = %s\n", topic);

	sprintf( streamKey, "%s:%s", getenv( "device.id" ), "stream" );
	printf("streamKey = %s\n", streamKey);
	
//
//
//

	MQTTAsync client;
	MQTTAsync_connectOptions conn_opts = MQTTAsync_connectOptions_initializer; // https://eclipse.dev/paho/files/mqttdoc/MQTTAsync/html/struct_m_q_t_t_async__connect_options.html
	MQTTAsync_disconnectOptions disc_opts = MQTTAsync_disconnectOptions_initializer;
	int rc;
	int ch;

uuid_t uuidGenerated;
uuid_generate_random(uuidGenerated);
uuid_unparse(uuidGenerated, quuid);

	if ((rc = MQTTAsync_create(&client, address, quuid, MQTTCLIENT_PERSISTENCE_NONE, NULL))
			!= MQTTASYNC_SUCCESS)
	{
		printf("Failed to create client, return code %d\n", rc);
		rc = EXIT_FAILURE;
		MQTTAsync_destroy(&client);
		return rc;
	}

	if ((rc = MQTTAsync_setCallbacks(client, client, connlost, msgarrvd, NULL)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to set callbacks, return code %d\n", rc);
		rc = EXIT_FAILURE;
		MQTTAsync_destroy(&client);
		return rc;
	}

	conn_opts.username = "sjmqtt";
	conn_opts.password = "sj9337700mqtt";
	// -u 'sjmqtt' -P 'sj9337700mqtt'
	
	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	conn_opts.onSuccess = onConnect;
	conn_opts.onFailure = onConnectFailure;
	conn_opts.context = client;
	if ((rc = MQTTAsync_connect(client, &conn_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start connect, return code %d\n", rc);
		rc = EXIT_FAILURE;
		MQTTAsync_destroy(&client);
		return rc;
	}

	while (!subscribed && !finished)
		#if defined(_WIN32)
			Sleep(100);
		#else
			usleep(10000L);
		#endif

	if (finished)
	{
		MQTTAsync_destroy(&client);
		return rc;
	}

	do 
	{
		ch = getchar();
	} while (ch!='Q' && ch != 'q');

	disc_opts.onSuccess = onDisconnect;
	disc_opts.onFailure = onDisconnectFailure;
	if ((rc = MQTTAsync_disconnect(client, &disc_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start disconnect, return code %d\n", rc);
		rc = EXIT_FAILURE;
		MQTTAsync_destroy(&client);
		return rc;
	}
 	while (!disc_finished)
 	{
		#if defined(_WIN32)
			Sleep(100);
		#else
			usleep(10000L);
		#endif
 	}

	MQTTAsync_destroy(&client);

 	return rc;
}

// https://github.com/eclipse/paho.mqtt.c/blob/master/src/samples/MQTTAsync_publish.c

// gcc -Wall -g mqttsubscriber.c -o mqttsubscriber -lpaho-mqtt3as -luuid -ldotenv -ljson-c

// mosquitto_sub -h 175.207.12.148 -p 1883 -t 'MQTT Examples/#' -v -u sjmqtt -P sj9337700mqtt
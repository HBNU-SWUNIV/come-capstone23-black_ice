/*******************************************************************************
 * Copyright (c) 2012, 2020 IBM Corp.
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
 *    Frank Pagliughi - loop to repeatedly read and sent time values.
 *******************************************************************************/

// This is a somewhat contrived example to show an application that publishes
// continuously, like a data acquisition app might do. In this case, though,
// we don't have a sensor to read, so we use the system time as the number
// of milliseconds since the epoch to simulate a data input.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "MQTTAsync.h"

#include <hiredis/hiredis.h>
#include <dotenv.h>
#include <json-c/json.h>
#include <time.h>


#if !defined(_WIN32)
#include <unistd.h>
#else
#include <windows.h>
#include <Minwinbase.h>
#endif

#if defined(_WRS_KERNEL)
#include <OsWrapper.h>
#endif

#if defined(_WIN32) || defined(_WIN64)
#define snprintf _snprintf
#endif


#define SSL

#ifdef SSL
//#define ADDRESS     "ssl://valid_address:8883"
//#define CA_PATH		"/valid_path/ca.pem"
//#define CERT_PATH		"/valid_path/cert.pem"
#endif

// Better not to flood a public broker. Test against localhost.
//#define ADDRESS         "mqtt://localhost:1883"
//#define ADDRESS     	"mqtt://175.207.12.148:1883"

//#define CLIENTID        "ExampleClientTimePub"
//#define TOPIC           "innoroad"
#define QOS             1
#define TIMEOUT         10000L
#define SAMPLE_PERIOD   1000L    // in ms

#include <uuid/uuid.h>

char quuid[37];


volatile int finished = 0;
volatile int connected = 0;

void onDisconnectFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Disconnect failed\n");
	finished = 1;
}

void onDisconnect(void* context, MQTTAsync_successData* response)
{
	printf("Successful disconnection\n");
	finished = 1;
}

void onSendFailure(void* context, MQTTAsync_failureData* response)
{
	MQTTAsync client = (MQTTAsync)context;
	MQTTAsync_disconnectOptions opts = MQTTAsync_disconnectOptions_initializer;
	int rc;

	printf("Message send failed token %d error code %d\n", response->token, response->code);
	opts.onSuccess = onDisconnect;
	opts.onFailure = onDisconnectFailure;
	opts.context = client;
	if ((rc = MQTTAsync_disconnect(client, &opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start disconnect, return code %d\n", rc);
		exit(EXIT_FAILURE);
	}
}

void onSend(void* context, MQTTAsync_successData* response)
{
	// This gets called when a message is acknowledged successfully.
}


void onConnectFailure(void* context, MQTTAsync_failureData* response)
{
	printf("Connect failed, rc %d\n", response ? response->code : 0);
	finished = 1;
}


void onConnect(void* context, MQTTAsync_successData* response)
{
	printf("Successful connection\n");
	connected = 1;
}

int messageArrived(void *context, char *topicName, int topicLen, MQTTAsync_message *message)
{
    printf("Message arrived\n");
    printf("     topic: %s\n", topicName);
    printf("   message: %.*s\n", message->payloadlen, (char*)message->payload);
    MQTTAsync_freeMessage(&message);
    MQTTAsync_free(topicName);
    return 1;
}


int64_t getTime(void)
{
	#if defined(_WIN32)
		FILETIME ft;
		GetSystemTimeAsFileTime(&ft);
		return ((((int64_t) ft.dwHighDateTime) << 8) + ft.dwLowDateTime) / 10000;
	#else
		struct timespec ts;
		clock_gettime(CLOCK_REALTIME, &ts);
		return ((int64_t) ts.tv_sec * 1000) + ((int64_t) ts.tv_nsec / 1000000);
	#endif
}

void connlost(void *context, char *cause)
{
	MQTTAsync client = (MQTTAsync)context;
	MQTTAsync_connectOptions conn_opts = MQTTAsync_connectOptions_initializer; // https://eclipse.dev/paho/files/mqttdoc/MQTTAsync/html/struct_m_q_t_t_async__connect_options.html
	int rc;

	printf("\nConnection lost\n");
	printf("     cause: %s\n", cause);

	printf("Reconnecting\n");
	
	conn_opts.username = getenv( "mqtt.username" );
	conn_opts.password = getenv( "mqtt.password" );
	
	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	conn_opts.onSuccess = onConnect;
	conn_opts.onFailure = onConnectFailure;
	conn_opts.context = client;
	
#ifdef SSL
	MQTTAsync_SSLOptions ssl_opts = MQTTAsync_SSLOptions_initializer;
    ssl_opts.enableServerCertAuth = false;
    ssl_opts.verify = false;
	conn_opts.ssl = &ssl_opts;
#endif
	
	if ((rc = MQTTAsync_connect(client, &conn_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start connect, return code %d\n", rc);
 		finished = 1;
	}
}

int main(int argc, char* argv[])
{
	char address[256];
	char topic[256];
	char streamKey[256];
	
	int i = env_load( "/webservice/.env.innoroad", false );
	printf("i = %d\n", i);
	
	sprintf( address, "%s://%s:%s", getenv( "mqtt.scheme" ), getenv( "mqtt.host" ), getenv( "mqtt.port" ) );
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

	MQTTAsync_message pubmsg = MQTTAsync_message_initializer;
	MQTTAsync_responseOptions pub_opts = MQTTAsync_responseOptions_initializer;

	int rc;

	uuid_t uuidGenerated;
	uuid_generate_random(uuidGenerated);
	uuid_unparse(uuidGenerated, quuid);
	
	if ((rc = MQTTAsync_create(&client, address, quuid, MQTTCLIENT_PERSISTENCE_NONE, NULL)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to create client object, return code %d\n", rc);
		exit(EXIT_FAILURE);
	}

	if ((rc = MQTTAsync_setCallbacks(client, NULL, connlost, messageArrived, NULL)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to set callback, return code %d\n", rc);
		exit(EXIT_FAILURE);
	}

	conn_opts.username = getenv( "mqtt.username" );
	conn_opts.password = getenv( "mqtt.password" );
	
	conn_opts.keepAliveInterval = 20;
	conn_opts.cleansession = 1;
	conn_opts.onSuccess = onConnect;
	conn_opts.onFailure = onConnectFailure;
	conn_opts.context = client;
	
#ifdef SSL
	MQTTAsync_SSLOptions ssl_opts = MQTTAsync_SSLOptions_initializer;
    ssl_opts.enableServerCertAuth = false;
    ssl_opts.verify = false;
	conn_opts.ssl = &ssl_opts;
#endif
	
	if ((rc = MQTTAsync_connect(client, &conn_opts)) != MQTTASYNC_SUCCESS)
	{
		printf("Failed to start connect, return code %d\n", rc);
		exit(EXIT_FAILURE);
	}

	while (!connected && !finished) {
		#if defined(_WIN32)
			Sleep(100);
		#else
			usleep(100000L);
		#endif
	}

//
//
//

    redisContext *rctx;
    redisReply *reply;
	
    const char *hostname = "127.0.0.1";
	int port = 6379;
	
	int isunix = 0;
	struct timeval timeout = { 1, 500000 }; // 1.5 seconds
	
	if (isunix) {
		rctx = redisConnectUnixWithTimeout(hostname, timeout);
	} else {
		rctx = redisConnectWithTimeout(hostname, port, timeout);
	}
	
	//
	
	if (rctx == NULL || rctx->err) {
		if (rctx) {
			printf( "Connection error: %s. [__FILE__ : %s] [__LINE__ : %d] [__FUNCTION__ : %s]", rctx->errstr, __FILE__, __LINE__, __FUNCTION__ );
			redisFree(rctx);
		} else {
			printf( "Connection error: can't allocate redis context. [__FILE__ : %s] [__LINE__ : %d] [__FUNCTION__ : %s]", __FILE__, __LINE__, __FUNCTION__ );
		}
		
		MQTTAsync_destroy(&client);
		exit(EXIT_FAILURE);
	}

//
//
//

	while (!finished) {
		reply = redisCommand(rctx,"LPOP %s", streamKey);
		if (reply == NULL || rctx->err) {
			if( rctx->err )
			{
				printf( "Error(%d):  Couldn't execute redisCommand.[%s] [__FILE__ : %s] [__LINE__ : %d] [__FUNCTION__ : %s]", rctx->err, rctx->errstr, __FILE__, __LINE__, __FUNCTION__ );
				
				redisFree(rctx);
				MQTTAsync_destroy(&client);
				
				exit(EXIT_FAILURE);
			}
			else
			{
				printf( "Error(NULL):  Couldn't execute redisCommand. [__FILE__ : %s] [__LINE__ : %d] [__FUNCTION__ : %s]", __FILE__, __LINE__, __FUNCTION__ );
			}
		}
		else {
			if( reply->str )
			{
				//printf( "LPOP:  %s [__FILE__ : %s] [__LINE__ : %d] [__FUNCTION__ : %s]", reply->str, __FILE__, __LINE__, __FUNCTION__ );
				
				pub_opts.onSuccess = onSend;
				pub_opts.onFailure = onSendFailure;
				pub_opts.context = client;

				pubmsg.payload = reply->str;
				pubmsg.payloadlen = strlen(pubmsg.payload) + 1;
				pubmsg.qos = QOS;
				pubmsg.retained = 0;

				if ((rc = MQTTAsync_sendMessage(client, topic, &pubmsg, &pub_opts)) != MQTTASYNC_SUCCESS)
				{
					printf("Failed to start sendMessage, return code %d\n", rc);
					finished = 1;
				}
			}
		}
		freeReplyObject(reply);
	}

	redisFree(rctx);
	
	MQTTAsync_destroy(&client);
 	return rc;
}

// https://github.com/eclipse/paho.mqtt.c/blob/master/src/samples/MQTTAsync_publish.c

// gcc -Wall -g qdaemon.c -o qdaemon -lhiredis -lpaho-mqtt3as -luuid -ldotenv -ljson-c

// mosquitto_sub -h 175.207.12.148 -p 1883 -t 'MQTT Examples/#' -v -u sjmqtt -P sj9337700mqtt
import cantools
import random
import string
import paho.mqtt.client as mqtt
import json
import os
import psycopg2
from dotenv import load_dotenv

print("Starting MQTT Connector")
load_dotenv()

def randomString(stringLength=6):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    if(mqtt_topic):
        print("Subscribing to topic: " + mqtt_topic)
        client.subscribe(mqtt_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # data variable with type as array of array string  # type: ignore
    print(msg.topic)
    [_, oem, model, vehicalId, userId] = msg.topic.split("/")[:5]
    data: list[list[str]] = json.loads(msg.payload)
    insert = {
        "oem": add_quotation_mark(oem),
        "model": add_quotation_mark(model),
        "vehicalId": vehicalId,
        "userId": userId,
    }
    is_inserted = False
    if (isinstance(candb, cantools.db.can.database.Database)):
        for frame in data:
            messages = decode_frame(frame)
            if messages is None:
                continue
            message = candb.get_message_by_frame_id(int(frame[0], 16))
            for m, n in messages.items(): # type: ignore
                if m not in insert and message.get_signal_by_name(m).is_multiplexer is False:
                    insert[m] = n
                    is_inserted = True
    if is_inserted:
        print(insert)
        insert_data(insert)



def insert_data(data: dict):
    # Convert data to SQL
    column_name = "\"" + "\",\"".join(data.keys()) + "\""
    values = ",".join([str(i) for i in data.values()])
    query = f"""INSERT INTO TEST_MQTT ({column_name}) VALUES ({values})"""
    print(query)
    cursor.execute(query)
    connection.commit()


def add_quotation_mark(data: str):
    """
    This function adds quotation marks to a string.

    :param data: The string to add quotation marks to.
    :return: The string with quotation marks added.
    """
    return "'" + data + "'"


def on_disconnect(client, userdata, rc):
    """
    This function is called when the client disconnects from the broker.

    :param client: The client instance that disconnected.
    :param userdata: The private user data as set in Client() or userdata_set().
    :param rc: The disconnection result.
    """
    print("Disconnected with result code "+str(rc))



def decode_frame(frame: list[str]):
    """Decode a frame from a list of strings.

    Args:
        frame: A list of strings representing a frame.

    Returns:
        The message decoded from the frame, or None if the frame cannot be decoded.
    """
    try:
        # convert the hex string to a list of hex values
        hex_values = frame[1].split(" ")
        # convert the hex values to a list of ints
        int_values = [int(hex_value, 16) for hex_value in hex_values]
        # convert the list of ints to a bytes string
        bytes_string = bytes(int_values)
        # decode the frame
        message = candb.decode_message(int(frame[0], 16), bytes_string)
        return message
    except:
        print("Error decoding frame: " + frame[0])
        return None




# Database Configuration
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_table = os.getenv('DB_TABLE')

# MQTT Configuration
mqtt_username = os.getenv('MQTT_USERNAME')
mqtt_password = os.getenv('MQTT_PASSWORD')
mqtt_host = os.getenv('MQTT_HOST', "localhost")
mqtt_port = int(os.getenv('MQTT_PORT', "1883"))
mqtt_topic = os.getenv('MQTT_TOPIC')

dbc_file = os.getenv('DBC_FILE', "main.dbc")


candb: cantools.db.can.database.Database = cantools.db.load_file(dbc_file) # type: ignore
connection = psycopg2.connect(user=db_user,
                              password=db_password,
                              host=db_host,
                              port=db_port,
                              database=db_name)
cursor = connection.cursor()

# MQTT client setup
clientId = randomString(6)
client = mqtt.Client(f"connector-py-{clientId}")
client.on_connect = on_connect
client.on_message = on_message

# Set MQTT credentials (if required)
if mqtt_username and mqtt_password:
    client.username_pw_set(mqtt_username, mqtt_password)

# Connect to MQTT broker
client.connect(mqtt_host, mqtt_port, 60)

# Start the MQTT event loop
client.loop_forever()
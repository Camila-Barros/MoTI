import paho.mqtt.client as mqtt
import time
import uuid #para RTT
import random
import logging
import ssl # para autenticação SSL
import json
import threading
import csv
from datetime import datetime, timezone

# CONFIGURAÇÃO DE LOGS
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
# obtém o logger do Paho e mantém-o em DEBUG
mqtt_logger = logging.getLogger("paho.mqtt.client")
mqtt_logger.setLevel(logging.DEBUG)

# CERTIFICADOS TLS (acaminhos bsolutos)
CA_CERT = "/home/camila/Documentos/MoTI/mqtt_tls_certs/ca.crt"
CLIENT_CERT = "/home/camila/Documentos/MoTI/mqtt_tls_certs/server.crt"
CLIENT_KEY = "/home/camila/Documentos/MoTI/mqtt_tls_certs/server.key"

# CONFIGURAÇÕES DO BROKER MQTT MOSQUITTO
BROKER = "localhost" # Endereço do broker Mosquitto, roda localmente
PORT = 8883 # porta para TLS, porta padrão é 1883 
TOPIC = "fabricaBeta/maquina1/temperatura" #Tópico
QOS = 2  # Altere para 0, 1 ou 2 conforme necessidade

# TOPICOS PARA RTT
ACK_TOPIC   = "moti/ack/temperatura"

# CAMINHO DO CSV
CSV_PATH = "/home/camila/Documentos/MoTI/rtt_log.csv"
with open(CSV_PATH, "w", newline="") as f:
    csv.writer(f).writerow([
        "id","qos","t0","t1","rtt_ms","temperature","datetime","date","time"
    ])

# guarda t0 de cada id
sent_times = {}

# CONECTANDO
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info("CONECTADO AO BROKER - SUBSCREVENDO AO ACK_TOPIC")
        client.subscribe(ACK_TOPIC, qos=QOS)
    else:
        logging.error(f"FALHA NA CONEXÃO: {rc}")

# PUBLISH
def on_publish(client, userdata, mid, reason_code, properties=None):
    logging.info(f"Mensagem {mid} publicada. Código: {reason_code}")

# LOOP
def on_ack(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        msg_id = data["id"]
        t0 = data["t0"]
        t1 = time.monotonic()
        if msg_id in sent_times:
            rtt = (t1 - sent_times.pop(msg_id))*1000  # ms
            temp = data.get("temperature")
            logging.info(f"RTT para temperatura {temp}°C (id={msg_id}) => {rtt:.1f} ms")
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_str, hora_str = agora.split(" ")
            # grava no CSV
            with open(CSV_PATH, "a", newline="") as f:
                csv.writer(f).writerow([
                    msg_id,
                    QOS,
                    t0,
                    t1,
                    f"{rtt:.1f}",
                    temp,
                    agora,      # carimbo completo
                    data_str,   # só a data
                    hora_str    # só a hora
                ])
    except Exception as e:
        logging.error(f"Erro no on_ack: {e}")

# MONTA O CLIENTE MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect 
client.on_publish = on_publish
client.enable_logger()
client.message_callback_add(ACK_TOPIC, on_ack)

# CONFIGURAÇÕES TLS
client.tls_set(ca_certs=CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY,
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS_CLIENT,
    ciphers=None)
client.tls_insecure_set(False)  # Rejeita certificados inválidos

# CONECTA E INICIA O LOOP
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()
time.sleep(5) # aguarda 5s para iniciar, dando tempo dos logs de conexão aparecerem

# LOOP PRINCIPAL DE PUBLICACAO DA MENSAGEM
try:
    while True:
        # monta payload com id, t0 e temperatura
        msg_id = str(uuid.uuid4())
        t0 = time.monotonic()
        sent_times[msg_id] = t0
        temperature = round(random.uniform(20, 40), 2) # Gera um número decimal entre 20 e 40 de "temperatura"
        payload = json.dumps({
            "id": msg_id,
            "t0": t0,
            "temperature": temperature
        })
        client.publish(TOPIC, payload, qos=QOS)
        logging.info(f"Publicando: {temperature}°C (QoS={QOS}, id={msg_id})")
        time.sleep(30) 
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
    logging.info("Publisher encerrado")

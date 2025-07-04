import paho.mqtt.client as mqtt
import requests
import logging
import json
import ssl
import time
import hashlib
import subprocess
import shlex
from datetime import datetime, timezone

# CONFIGURAÇÃO DE LOGS
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# CERTIFICADOS TLS MQTT 
CA_CERT = "/home/camila/Documentos/MoTI/mqtt_tls_certs/ca.crt"
CLIENT_CERT = "/home/camila/Documentos/MoTI/mqtt_tls_certs/server.crt"
CLIENT_KEY = "/home/camila/Documentos/MoTI/mqtt_tls_certs/server.key"

# CONFIGURAÇÕES DO IPFS PROTEGIDO POR mTLS VIA NGINX
IPFS_API_URL = "https://18.216.73.135:8443/api/v0/add" #PORTA 8443, COM IPFS PROTEGIDO POR mTLS VIA NGINX
NGINX_CA    = "/home/camila/Documentos/MoTI/mqtt_tls_certs/nginx-ca.crt"
CERT_CLIENT = "/home/camila/Documentos/MoTI/mqtt_tls_certs/nginx-client.crt"
KEY_CLIENT  = "/home/camila/Documentos/MoTI/mqtt_tls_certs/nginx-client.key"

# CONFIGURAÇÕES DO SSH PARA APPEND REMOTO
SSH_KEY      = "/home/camila/aws-keys/ipfs-key.pem"
SSH_HOST     = "ubuntu@18.216.73.135"
REMOTE_FILE  = "/var/www/ipfs_data/data.jsonl"
SSH_BIN      = "/usr/bin/ssh"

# CONFIGURAÇÕES DO BROKER MQTT MOSQUITTO
BROKER = "localhost" # Endereço do broker Mosquitto, roda localmente
PORT = 8883 # porta para TLS, porta padrão é 1883 
TOPIC = "fabricaBeta/maquina1/temperatura" #Tópico
QOS = 2  # Altere para 0, 1 ou 2 conforme necessidade

# TOPICOS PARA RTT
ACK_TOPIC   = "moti/ack/temperatura"

def processar_payload(data: dict):
    """Envia ao IPFS (via HTTPS+mTLS) e faz append remoto via SSH."""
    # serializa e envia ao IPFS
    #logging.debug(f"�� processar_payload() recebido: {data!r}")
    payload_json = json.dumps(data).encode()
    response = requests.post(
        IPFS_API_URL,
        files={"file": payload_json},
        cert=(CERT_CLIENT, KEY_CLIENT),
        verify=NGINX_CA,
        timeout=10
    )

    if response.status_code != 200:
        logging.error(f"❌ Erro IPFS: {response.status_code} {response.text}")
        return
    cid = response.json()["Hash"]
    logging.info(f"�� Enviado ao IPFS: CID={cid}")

    # prepara linha JSONL para armazenar em data.jsonl
    data["cid"] = cid
    line = json.dumps(data)

    # monta comando SSH append (não-interativo)
    ssh_cmd = (
        f"{SSH_BIN} -i {shlex.quote(SSH_KEY)} "
        "-o BatchMode=yes -o StrictHostKeyChecking=no "
        f"{SSH_HOST} "
        f"\"echo {shlex.quote(line)} >> {REMOTE_FILE}\""
    )
    #logging.debug(f" SSH append: {ssh_cmd}")

    try:
        proc = subprocess.run(
            ssh_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if proc.returncode:
            logging.error(f"❌ SSH falhou ({proc.returncode}): {proc.stderr.strip()}")
        else:
            logging.info("✅ Append remoto OK")
    except Exception:
        logging.exception("❌ Exceção ao executar SSH append")

    logging.info(f"�� https://ipfs.io/ipfs/{cid}")



# CALLBACK DE CONEXÃO
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe(TOPIC, qos=QOS)
        logging.info(f"CONECTADO E INSCRITO EM {TOPIC}")
    else:
        logging.error(f"❌ Falha na conexão MQTT: {rc}")


# CALLBACK PARA MENSAGENS
def on_message(client, userdata, msg):
    """Processa temperatura, IPFS+SSH e envia ACK."""
    try:
        data = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        logging.error("Payload inválido")
        return

    # preserva id, t0 e temperature
    msg_id = data["id"]
    t0     = data["t0"]
    temperature = data["temperature"]

    processar_payload({
        "id": msg_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "topic": msg.topic,
        "payload": str(temperature),
        "qos": msg.qos,
        "hash": hashlib.sha256(msg.payload).hexdigest() if msg.qos==2 else None
    })

    # envia ACK de volta para medir RTT
    ack_payload = json.dumps({
        "id": msg_id,
        "t0": t0,
        "temperature": temperature
    })

    client.publish(ACK_TOPIC, ack_payload, qos=QOS)
    logging.info(f"Enviado ACK para id={msg_id}")

    logging.debug(f">>> DADOS CAPTURADOS: {data}")  # Imprime para conferir
    time.sleep(1)  # respeito a qualquer rate limit (delay para não estourar limite de requisições)      

# MONTA E CONFIGURA MQTT CLIENT
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.enable_logger()

# TLS MQTT
client.tls_set(ca_certs=CA_CERT, certfile=CLIENT_CERT, keyfile=CLIENT_KEY)
client.tls_insecure_set(False)

# CONECTA E INICIA LOOP
client.connect(BROKER, PORT, keepalive=60)
client.loop_forever()

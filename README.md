# MOTI -> MQTT-ORIENTED THINGS INTEROPERABILITY

[![NPM](https://img.shields.io/npm/l/react)](https://github.com/Camila-Barros/MoTI/blob/main/LICENSE)

Este projeto apresenta uma solução voltada à interoperabilidade de comunicação entre dispositivos IoT industriais de diferentes organizações e sistemas, utilizando o protocolo MQTT. Nomeada de MoTI (MQTT-oriented Things Interoperability), a arquitetura promove uma integração segura, confiável e escalável entre dispositivos heterogêneos, com suporte à diferenciação de mensagens por níveis de QoS.


## Índice
- [Sobre o Projeto](#sobre-o-projeto)
     - [Arquitetura](#arquitetura)
     - [Aplicação](#aplicação)
- [Implementação](#implementação)
     - [Requisitos](#requisitos)
     - [Ambiente Local](#ambiente-local)
     - [Ambiente Remoto](#ambiente-remoto)
- [Testes](#testes)
     - [Execução](#execução)
     - [Telas de Logs](#telas-de-logs)
     - [Tempo de Resposta](#tempo-de-resposta)

  
---

# SOBRE O PROJETO

MoTI é uma arquitetura de comunicação interoperável voltada ao contexto da Indústria 4.0. Foi desenvolvido com o objetivo de superar barreiras de integração entre dispositivos IoT industriais heterogêneos, promovendo a descentralização do armazenamento de dados por meio da utilização do IPFS. A proposta adota o protocolo MQTT, amplamente utilizado em aplicações IoT por sua leveza e eficiência em redes com recursos limitados. A comunicação entre os dispositivos utiliza diferentes níveis de QoS, sendo o nível 2 empregado para garantir entrega confiável em mensagens críticas. Essa abordagem assegura que os dados sejam transmitidos com controle de duplicidade, confirmação de entrega e resiliência em ambientes industriais sujeitos a falhas de rede. Com isso, o MoTI busca garantir a confiabilidade, acessibilidade e rastreabilidade das informações trocadas entre diferentes sistemas industriais, ao mesmo tempo em que preserva a escalabilidade e a segurança das operações. Trata-se de uma iniciativa prática e viável frente aos desafios nacionais e globais de adoção das tecnologias habilitadoras da Indústria 4.0, especialmente no que se refere à interoperabilidade e descentralização dos fluxos de dados.


![image](https://github.com/Camila-Barros/MoTI/blob/main/Fig_Diagrama6.png)


## ARQUITETURA

A aplicação da arquitetura MoTI permite que múltiplas partes interessadas — como empresas, instituições e fornecedores — acessem os dados coletados a partir de dispositivos IoT de forma segura. A aplicação mantém compatibilidade com sistemas legados e utiliza o armazenamento descentralizado via IPFS para registrar os dados de forma distribuída, garantindo acessibilidade fora da rede local. 

Mensagens críticas, transmitidas com QoS nível 2, são tratadas com prioridade e autenticadas por meio de um componente dedicado, utilizando hashing com SHA-256, assegurando a integridade das informações compartilhadas. 

A arquitetura do MoTI é formada pelos componentes:
- **Admin:** Representa o cliente com perfil administrativo, responsável pela configuração inicial da rede, cadastro de dispositivos, definição de permissões e monitoramento geral da aplicação. O Admin possui acesso completo às funcionalidades da arquitetura.
- **Usuário:** Representa os clientes finais, que podem acessar os dados publicados na rede de forma autenticada. O acesso dos usuários é restrito aos dados e dispositivos previamente autorizados.
- **Dispositivos IoT:** São os elementos responsáveis pela coleta e envio de dados industriais (como sensores e atuadores) para o broker MQTT. Esses dispositivos podem pertencer a diferentes empresas, instituições ou fornecedores, reforçando a interoperabilidade.
- **MQTT Broker:** Componente central da comunicação assíncrona entre dispositivos e clientes. Ele gerencia os tópicos, roteia mensagens conforme os níveis de QoS definidos e garante a entrega conforme o contrato de qualidade do serviço. 
- **Interceptador:** Atua como intermediário entre o broker e os demais módulos, responsável por inspecionar, classificar e redirecionar as mensagens recebidas de acordo com seu nível de criticidade. Mensagens com QoS nível 2 são direcionadas ao Autenticador, e mensagens com QoS 0 ou 1 são encaminhadas diretamente ao módulo de armazenamento.
- **Autenticador:** Implementa uma camada de segurança adicional para mensagens críticas (QoS 2), utilizando hashing (SHA-256) para garantir a integridade dos dados. O resultado dessa autenticação pode ser utilizado para validação posterior pelos receptores autorizados.
- **IPFS:** Responsável pelo armazenamento descentralizado dos dados gerados pelos dispositivos IoT. Ao adotar o IPFS, a arquitetura permite a persistência dos dados fora da rede local, promovendo escalabilidade, disponibilidade e resistência à falhas.

## APLICAÇÃO

![image](https://github.com/Camila-Barros/MoTI/blob/main/Fig_DiagramaSeq7.png)

**RegistroDispositivo:** O administrador cadastra cada dispositivo IoT junto ao broker MQTT (Mosquitto), definindo seus respectivos tópicos de publicação, níveis de QoS e certificações necessárias para autenticação.

**RegistroUsuário:** O administrador também registra os usuários autorizados, gerando seus certificados digitais com base em uma autoridade certificadora (CA) local e controlada.


**RegistroAcesso:** Com base nos registros anteriores, são definidos os direitos de acesso. A autenticação mútua baseada em TLS garante que apenas agentes autorizados consigam publicar ou consumir dados.

**EnviaDados – Dispositivo IoT → Broker MQTT:** O dispositivo IoT publica mensagens para o broker Mosquitto via MQTT, utilizando \textit{Mutual TLS} para garantir criptografia e autenticação. O QoS pode variar entre 0, 1 ou 2, dependendo da criticidade dos dados.

**EnviaDados – Broker MQTT → IPFS (QoS 0,1):** Mensagens publicadas com QoS 0 ou 1 são interceptadas por um \textit{subscriber} (\textit{interceptor}), que valida o certificado do broker e transmite os dados ao IPFS via HTTPS com mTLS. A integridade dos dados é implicitamente confiada à conexão segura.

**RequestDados – IPFS (QoS 0,1):** Quando o usuário requisita dados não críticos (QoS 0 ou 1), o sistema realiza a verificação da autenticidade via TLS e retorna os dados do IPFS, acessando-os por meio do hash (CID) armazenado previamente.

**EnviaDados – Broker MQTT → IPFS (QoS 2):** Para dados críticos, o \textit{subscriber} envia as mensagens ao IPFS, mas agora com um adicional: o cálculo do hash SHA-256 é utilizado para garantir a integridade dos dados entre origem e destino. Esse hash é incluído no metadado JSON que acompanha o CID.

**RequestDados – IPFS (QoS 2):** Ao solicitar dados com QoS 2, o sistema autentica o usuário e realiza a verificação do hash SHA-256 para garantir que os dados recebidos do IPFS são exatamente os mesmos que os enviados, mitigando qualquer risco de alteração.

**Registro de CID + metadados:** Após o envio ao IPFS, o CID gerado é registrado remotamente junto com os metadados associados (tópico, payload, QoS, timestamp e hash SHA-256) em um arquivo `data.jsonl`, armazenado no backend da EC2. Esse passo assegura rastreabilidade e permite consultas futuras.


---

# IMPLEMENTAÇÃO

Para garantir a reprodutibilidade da arquitetura MoTI, foi elaborado um tutorial detalhado, contemplando o ambiente necessário, as dependências e as etapas de configuração passo a passo. O objetivo é facilitar futuras implementações e contribuir com outros pesquisadores interessados em soluções interoperáveis e seguras para dispositivos IoT industriais.

## REQUISITOS

- [Ubuntu 22.04 LTS](https://ubuntu.com/);
- [Python 3.12](https://www.python.org/);
- [OpenSSL](https://www.openssl.org/);
- [Mosquitto](https://mosquitto.org/);
- [Amazon Web Services (AWS)](https://aws.amazon.com/pt/free/);



## AMBIENTE LOCAL

### 1. PREPARAR O AMBIENTE

Atualizar os repositórios e pacotes do sistema operacional Ubuntu antes de iniciar a instalação:
```bash
sudo apt update && sudo apt upgrade -y 
```

Instalar dependências de sistema. Estas ferramentas são essenciais para comunicação segura via MQTT e uso do IPFS:
```bash
sudo apt install -y python3 python3-venv python3-pip mosquitto mosquitto-clients openssl 
```

Instalar as bibliotecas Python:
 ```bash
pip install paho-mqtt requests 
```

A instalação de pacotes Python via PIP foram bloqueadas a partir do Python 3.11 e a solução é criar um ambiente virtual (\textit{venv}) e instalar os pacotes necessários dentro.
```bash
python3 -m venv venv #Cria o ambiente virtual 
source venv/bin/activate #Ativa
pip install paho-mqtt requests #Instala o pacote Paho-MQTT 
```

### 2. CERTIFICADOS TLS MOSQUITTO

Criar um diretório em mosquitto para armazenar os certificados digitais.
```bash
sudo mkdir -p /etc/mosquitto/certs
sudo cp server.crt server.key ca.crt /etc/mosquitto/certs/ 
```

Gerar a autoridade certificadora (CA). O ambiente local foi nomeado como “EmpresaBeta”:
```bash
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt \
-subj "/C=BR/ST=SP/L=SaoPaulo/O=EmpresaBeta/OU=TI/CN=EmpresaBetaRootCA" 
```

Gerar o certificado digital para o servidor:
```bash
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
-subj "/C=BR/ST=SP/L=SaoPaulo/O=EmpresaBeta/OU=TI/CN=localhost"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
-out server.crt -days 1825 -sha256 
```

Gerar o certificado digital para o usuário:
```bash
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr \
-subj "/C=BR/ST=SP/L=SaoPaulo/O=EmpresaBeta/OU=TI/CN=clienteCamila"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
-out client.crt -days 1825 -sha256 
```

Para que os certificados sejam acessados sem problemas, é preciso dar permissão de leitura:
```bash
sudo chmod 644 /etc/mosquitto/certs/* 
```

Abrir o arquivo de configuração do mosquitto:
```bash
sudo nano /etc/mosquitto/conf.d/ssl.conf  
```

Editar o arquivo conf para mTLS:
```bash
listener 8883
protocol mqtt
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
require_certificate true
use_identity_as_username true
allow_anonymous false  
```

Reiniciar o broker MQTT:
```bash
sudo systemctl restart mosquitto 
```


### 3. CERTIFICADOS TLS LOCAIS

Ativar o ambiente virtual:
```bash
source venv/bin/activate  
```

Criar um diretório dentro do projeto para os certificados com um caminho absoluto:
```bash
mkdir ~/Documentos/MoTI/mqtt_tls_certs 
```

Copiar os certificados para o diretório criado:
```bash
sudo cp /etc/mosquitto/certs/*.crt ~/Documentos/MoTI/mqtt_tls_certs/
sudo cp /etc/mosquitto/certs/server.key ~/Documentos/MoTI/mqtt_tls_certs/ 
```

Dar permissão de leitura aos certificados:
```bash
sudo chmod 644 ~/Documentos/MoTI/mqtt_tls_certs/*  
```


### 4. PUBLISHER

No diretório do projeto, criar o arquivo "publish_to_mosquitto.py" em linguagem Python, com o código abaixo, que publicará os dados do dispositivo IoT nos tópicos do broker MQTT Mosquitto. O código fonte também pode ser encontrado anexado ao projeto.


```python
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
```

Dar permissão ao código criado e reiniciar o Mosquitto:
```bash
chmod 
```
\begin{lstlisting}[style=terminal]
chmod +x publish_to_mosquitto.py 
sudo systemctl restart mosquitto 
\end{lstlisting}

Para facilitar a execução do código-fonte, criar um serviço systemd moti-publisher:
```bash
sudo nano /etc/systemd/system/moti-publisher.service 
```

Colar dentro do editor:
```bash
[Unit]
Description=MoTI MQTT Publisher Service
After=network.target

[Service]
Type=simple
User=camila
WorkingDirectory=/home/camila/Documentos/MoTI
ExecStart=/home/camila/MoTI/producer/venv/bin/python publish_to_mosquitto.py
Restart=on-failure
RestartSec=5s
SyslogIdentifier=moti-publisher

[Install]
WantedBy=multi-user.target
\end{lstlisting}

Ativar e iniciar o serviço:
\begin{lstlisting}[style=terminal]
sudo systemctl daemon-reload
sudo systemctl enable moti-publisher
sudo systemctl start moti-publisher  
```

### 5. SUBSCRIBER

No diretório do projeto, criar também o arquivo "subscribe_to_ipfs.py" em linguagem Python, com o código abaixo, que assinará os tópicos do broker MQTT Mosquitto e os enviará ao IPFS de acordo com o nível de QoS. O código fonte também pode ser encontrado anexado ao projeto.

```python
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
```


Dar permissão ao código criado e reiniciar o Mosquitto:
```bash
chmod +x subscribe_to_ipfs.py
sudo systemctl restart mosquitto  
```

Criar o serviço systemd moti-subscriber para executá-lo:
```bash
sudo nano /etc/systemd/system/moti-subscriber.service  
```

Colar dentro do editor:
```bash
[Unit]
Description=MoTI MQTT→IPFS Subscriber Service
After=network.target

[Service]
Type=simple
User=camila
WorkingDirectory=/home/camila/Documentos/MoTI
ExecStart=/home/camila/MoTI/producer/venv/bin/python subscribe_to_ipfs.py
Restart=on-failure
RestartSec=5s
SyslogIdentifier=moti-subscriber

[Install]
WantedBy=multi-user.target 
```

Ativar e iniciar o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl enable moti-subscriber
sudo systemctl start moti-subscriber  
```


## AMBIENTE REMOTO

### 1. INSTÂNCIA EC2 NA AWS

A escolha da plataforma Amazon Web Services (AWS) para hospedagem do nó IPFS remoto foi motivada por sua infraestrutura confiável, escalável e amplamente consolidada no meio acadêmico e profissional. A AWS oferece recursos de segurança robustos, como controle de acesso, conexões seguras via SSH e suporte a certificados TLS, alinhando-se aos requisitos de autenticação e proteção de dados da arquitetura MoTI. 

Acessar o Console EC2 em https://aws.amazon.com/pt/console/ e criar uma instância. Em seguida criar um novo par de chaves SSH, tipo RSA, e salvar no formato “.pem”.

Configurar a rede (firewall), criando um grupo de segurança para o acesso remoto ao nó IPFS, e editando as regras de segurança, considerando as portas e IPs:
```bash
TIPO     | PROT. | PORTA | ORIGEM 	     | DESCRIÇÃO 

SSH 	 | TCP   | 22    | 189.xx.xxx.xxx/32 | Acesso remoto via terminal SSH 
                                               do computador local

TCP pers | TCP   | 8443  | 189.xx.xxx.xxx/32 | Conexão mTLS do computador local 
                                               ao Nginx (para enviar dados via 
                                               HTTPS ao IPFS)

TCP pers | TCP   | 8443  | 177.xx.xxx.xxx/32 | Conexão mTLS de outro dispositivo
                                               autorizado (usuário)

TCP pers | TCP   | 4001  | 0.xx.xxx.xxx/0    | Comunicação entre nós IPFS na rede 
                                               peer-to-peer

TCP pers | TCP   | 5001  | 189.xx.xxx.xxx/32 | Acesso direto a API do IPFS 
                                               (bypassando o Nginx) 
```


Clicar em “Iniciar Instância” e aguardar que a instância apareça como “Executando”. O console da instância é apresentado abaixo: 

![image](https://github.com/Camila-Barros/MoTI/blob/main/Fig_EC2instancia.png)

Clicar na instância e anotar o número do IPv4 público.

### 2. INSTÂNCIA EC2 (VM) VIA SSH

Mover a chave “.pem” salva anteriormente para uma pasta segura
```bash
mkdir -p ~/aws-keys
mv ~/Downloads/ipfs-key.pem ~/aws-keys/ 
```

Ajustar as permissões da chave, pois o SSH exige que a chave tenha permissão restrita:
```bash
chmod 400 ~/aws-keys/ipfs-key.pem 
```
  
Conectar e acessar a instância EC2 via SSH:
```bash
#Substituir pelo nome do arquivo da chave SSH .pem
#Substituir xxx pelo IPv4 da instância

ssh -i ~/aws-keys/seuarquivo.pem ubuntu@54.xxx.xxx.xxx  
```

Atualizar o sistema:
```bash
sudo apt update && sudo apt upgrade -y  
```
  
Instalar as dependências básicas:
```bash
sudo apt install curl wget tar -y 
```

Baixar e instalar o daemon Go-IPFS (Servidor IPFS) na EC2 (VM):
```bash
wget https://dist.ipfs.tech/go-ipfs/v0.24.0/go-ipfs_v0.24.0_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.24.0_linux-amd64.tar.gz
cd go-ipfs
sudo bash install.sh  
```

Verificar a instalação:
```bash
ipfs --version  
```

Inicializar o IPFS. Esse comando cria a estrutura básica de diretórios e configurações do IPFS para o usuário Ubuntu.
```bash
ipfs init 
```
  
Rodar o daemon do IPFS e configurar para que inicie automaticamente:
```bash
ipfs daemon & 
```

Instalar o Nginx na EC2 (protege o gateway com um reverse-proxy autenticado):
```bash
sudo apt update && sudo apt install nginx 
```
	
Criar o diretório para armazenar os certificados digitais do IPFS:
```bash
sudo mkdir -p /etc/nginx/certs 
```

Abrir o arquivo de configuração do Nginx:
```bash
sudo nano /etc/nginx/sites-available/ipfs.conf 
```

Editar o arquivo de configuração:
```bash
server {
    listen 8443 ssl;
    server_name _;
    # Serve certs
    ssl_certificate      /etc/nginx/certs/nginx-server.crt;
    ssl_certificate_key  /etc/nginx/certs/nginx-server.key;

    # CA que verifica clientes
    ssl_client_certificate /etc/nginx/certs/nginx-ca.crt;
    ssl_verify_client    on;

    # Proxy para API do IPFS
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
    }
    # Expor o arquivo data.jsonl
    location /data.jsonl {
        alias /var/www/ipfs_data/data.jsonl;
       # add_header Content-Type text/plain;
    }
} 
```

Ativar o Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/ipfs.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx 
```

Preparar o arquivo de registros:
```bash
sudo mkdir -p /var/www/ipfs_data
sudo touch /var/www/ipfs_data/data.jsonl
sudo chown www-data:www-data /var/www/ipfs_data/data.jsonl 
```

Ajustar as permissões do arquivo remoto:
```bash
sudo chown ubuntu:www-data /var/www/ipfs_data/data.jsonl
sudo chmod  664             /var/www/ipfs_data/data.jsonl 
```


### 3. CERTIFICADOS TLS NGINX

Gerar os certificados digitais para segurança TLS, utilizando o OpenSSL para gerar certificados que serão utilizados na comunicação MQTT e IPFS:
```bash
openssl req -newkey rsa:2048 -nodes -keyout client.key -x509 -days 365 -out client.crt 
```
    
Transferir certificados do servidor EC2 para o dispositivo da rede local (ambiente local):
```bash
scp -i ~/aws-keys/ipfs-key.pem ubuntu@IP_DA_EC2:/etc/nginx/certs/nginx-client.* ~/Documentos/MoTI/mqtt_tls_certs/ 
```

---


# TESTES

## EXECUÇÃO





```bash
chmod 
```

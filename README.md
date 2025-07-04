# MoTI - MQTT-oriented Things Interoperability 

[![NPM](https://img.shields.io/npm/l/react)](https://github.com/Camila-Barros/MoTI/blob/main/LICENSE)

Este projeto apresenta uma solução voltada à interoperabilidade de comunicação entre dispositivos IoT industriais de diferentes organizações e sistemas, utilizando o protocolo MQTT. Nomeada de MoTI (MQTT-oriented Things Interoperability), a arquitetura promove uma integração segura, confiável e escalável entre dispositivos heterogêneos, com suporte à diferenciação de mensagens por níveis de QoS.


## Índice
- [Sobre](#sobre-o-projeto)


## Sobre o Projeto

MoTI é uma arquitetura de comunicação interoperável voltada ao contexto da Indústria 4.0. Foi desenvolvido com o objetivo de superar barreiras de integração entre dispositivos IoT industriais heterogêneos, promovendo a descentralização do armazenamento de dados por meio da utilização do IPFS. A proposta adota o protocolo MQTT, amplamente utilizado em aplicações IoT por sua leveza e eficiência em redes com recursos limitados. A comunicação entre os dispositivos utiliza diferentes níveis de QoS, sendo o nível 2 empregado para garantir entrega confiável em mensagens críticas. Essa abordagem assegura que os dados sejam transmitidos com controle de duplicidade, confirmação de entrega e resiliência em ambientes industriais sujeitos a falhas de rede. Com isso, o MoTI busca garantir a confiabilidade, acessibilidade e rastreabilidade das informações trocadas entre diferentes sistemas industriais, ao mesmo tempo em que preserva a escalabilidade e a segurança das operações. Trata-se de uma iniciativa prática e viável frente aos desafios nacionais e globais de adoção das tecnologias habilitadoras da Indústria 4.0, especialmente no que se refere à interoperabilidade e descentralização dos fluxos de dados.

<< [FIGURA] <<

A aplicação da arquitetura MoTI permite que múltiplas partes interessadas — como empresas, instituições e fornecedores — acessem os dados coletados a partir de dispositivos IoT de forma segura. A aplicação mantém compatibilidade com sistemas legados e utiliza o armazenamento descentralizado via IPFS para registrar os dados de forma distribuída, garantindo acessibilidade fora da rede local. 

Mensagens críticas, transmitidas com QoS nível 2, são tratadas com prioridade e autenticadas por meio de um componente dedicado, utilizando hashing com SHA-256, assegurando a integridade das informações compartilhadas. 


### Arquitetura

Descritivo dos componentes da estrutura:
- **Admin:** Representa o cliente com perfil administrativo, responsável pela configuração inicial da rede, cadastro de dispositivos, definição de permissões e monitoramento geral da aplicação. O Admin possui acesso completo às funcionalidades da arquitetura.
- **Usuário:** Representa os clientes finais, que podem acessar os dados publicados na rede de forma autenticada. O acesso dos usuários é restrito aos dados e dispositivos previamente autorizados.
- **Dispositivos IoT:** São os elementos responsáveis pela coleta e envio de dados industriais (como sensores e atuadores) para o broker MQTT. Esses dispositivos podem pertencer a diferentes empresas, instituições ou fornecedores, reforçando a interoperabilidade.
- **MQTT Broker:** Componente central da comunicação assíncrona entre dispositivos e clientes. Ele gerencia os tópicos, roteia mensagens conforme os níveis de QoS definidos e garante a entrega conforme o contrato de qualidade do serviço. 
- **Interceptador:** Atua como intermediário entre o broker e os demais módulos, responsável por inspecionar, classificar e redirecionar as mensagens recebidas de acordo com seu nível de criticidade. Mensagens com QoS nível 2 são direcionadas ao Autenticador, e mensagens com QoS 0 ou 1 são encaminhadas diretamente ao módulo de armazenamento.
- **Autenticador:** Implementa uma camada de segurança adicional para mensagens críticas (QoS 2), utilizando hashing (SHA-256) para garantir a integridade dos dados. O resultado dessa autenticação pode ser utilizado para validação posterior pelos receptores autorizados.
- **IPFS:** Responsável pelo armazenamento descentralizado dos dados gerados pelos dispositivos IoT. Ao adotar o IPFS, a arquitetura permite a persistência dos dados fora da rede local, promovendo escalabilidade, disponibilidade e resistência à falhas.





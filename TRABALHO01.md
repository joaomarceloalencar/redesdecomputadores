# Trabalho Prático 01 — Análise de Conexões TCP com Wireshark

**Disciplina:** Redes de Computadores

**Valor:** 2,0 pontos (Avaliação 3)

**Formação de equipes:** até 2 integrantes

**Prazo de entrega:** 16/06/2026

**Formato da entrega:** Enviar o link do vídeo no YouTube (não listado) via Telegram, com o nome dos integrantes da equipe.

---

## 1. Contexto

Este trabalho integra os conteúdos estudados nos capítulos 1, 2 e 3 da obra *Redes de Computadores e a Internet* (Kurose & Ross). O objetivo é consolidar, por meio de experimentação prática, os conceitos fundamentais do protocolo TCP, com ênfase no processo de estabelecimento de conexão e nos mecanismos de controle de sequência e reconhecimento.

---

## 2. Objetivos

Ao concluir este trabalho, espera-se que o(a) aluno(a) seja capaz de:

- Configurar um ambiente de laboratório de rede para geração e captura de tráfego TCP;
- Utilizar o Wireshark para capturar e analisar pacotes de rede;
- Identificar e interpretar os campos de número de sequência (*Sequence Number*) e número de reconhecimento (*Acknowledgment Number*) nos segmentos TCP;
- Descrever o funcionamento do handshake de três vias (*three-way handshake*) do TCP.

---

## 3. Metodologia

### 3.1 Ambiente de laboratório

Os(as) alunos(as) devem configurar, de forma autônoma, um ambiente de laboratório com duas máquinas em rede — seja por meio de máquinas virtuais ou de um ambiente de rede local. A escolha das ferramentas e dos recursos utilizados fica a critério da equipe.

### 3.2 Desenvolvimento da aplicação

Para geração do tráfego TCP a ser analisado, as equipes devem desenvolver um **servidor TCP de eco** (*echo server*) em Python, tendo como ponto de partida os exemplos de código fornecidos pelo professor. O comportamento esperado da aplicação é o seguinte:

1. O cliente envia um caractere ao servidor;
2. O servidor exibe o caractere recebido em sua saída padrão e o retransmite ao cliente;
3. O cliente exibe o caractere recebido em sua saída padrão;
4. O processo se repete até que o cliente envie um caractere especial predefinido, sinalizando o encerramento da conexão.

### 3.3 Captura e análise com Wireshark

Com a aplicação em execução, a equipe deve realizar a captura do tráfego TCP utilizando o Wireshark. Para evitar que tráfego não relacionado à conexão analisada comprometa a legibilidade da captura, **é obrigatório configurar um filtro de captura** restringindo a exibição aos pacotes pertencentes exclusivamente à conexão estabelecida pela aplicação.

O vídeo deve demonstrar o estabelecimento da conexão TCP capturado nas duas máquinas e incluir uma explicação clara dos seguintes elementos:

- Os três segmentos do handshake de três vias (SYN, SYN-ACK, ACK);
- Os valores dos campos de número de sequência e número de reconhecimento em cada etapa do handshake;
- A relação entre os valores observados na captura e os conceitos teóricos apresentados em aula.

---

## 4. Entrega

O trabalho deve ser entregue na forma de um **vídeo de até 5 (cinco) minutos**, carregado no YouTube como **não listado**. O link do vídeo deve ser encaminhado ao professor via **Telegram** até a data de entrega estabelecida.

---

## 5. Critérios de avaliação

| Critério | Descrição |
|---|---|
| Ambiente de laboratório | Configuração funcional com duas máquinas em rede |
| Aplicação de eco | Implementação correta do servidor e cliente TCP de eco |
| Captura com filtro | Uso adequado do filtro de captura no Wireshark |
| Análise do handshake | Identificação e explicação correta dos três segmentos |
| Números de sequência e reconhecimento | Interpretação correta dos campos nos pacotes capturados |
| Clareza da apresentação | Objetividade e qualidade da explicação no vídeo |

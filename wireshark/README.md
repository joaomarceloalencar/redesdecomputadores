# Aula prática: Wireshark — Observando protocolos em ação

> Roteiro de aula para apresentar o Wireshark a uma turma de redes de computadores, partindo de uma instalação limpa de Ubuntu Desktop e demonstrando, em ordem crescente de complexidade, as diferenças entre TCP/UDP, HTTP/HTTPS e o papel do DNS.

## Sumário

- [Objetivos de aprendizagem](#objetivos-de-aprendizagem)
- [Pré-requisitos e cenário](#pré-requisitos-e-cenário)
- [Estrutura geral da aula](#estrutura-geral-da-aula)
- [Bloco 1 — Instalação do Wireshark no Ubuntu Desktop](#bloco-1--instalação-do-wireshark-no-ubuntu-desktop)
- [Bloco 2 — Tour pela interface](#bloco-2--tour-pela-interface)
- [Bloco 3 — Demo 1: TCP vs UDP com sockets Python](#bloco-3--demo-1-tcp-vs-udp-com-sockets-python)
- [Bloco 4 — Demo 2: HTTP vs HTTPS](#bloco-4--demo-2-http-vs-https)
- [Bloco 5 — Demo 3: DNS](#bloco-5--demo-3-dns)
- [Bloco 6 — Fechamento](#bloco-6--fechamento)
- [Dicas operacionais](#dicas-operacionais)
- [Referências](#referências)

## Objetivos de aprendizagem

Ao final da aula, os alunos devem ser capazes de:

1. Instalar e configurar o Wireshark em um sistema Linux com permissões adequadas para captura.
2. Diferenciar filtros de captura (BPF) e filtros de exibição (display).
3. Identificar visualmente, em uma captura, o handshake de três vias do TCP, ACKs e o encerramento ordenado da conexão.
4. Reconhecer a ausência de conexão e de confirmação no UDP.
5. Distinguir tráfego HTTP em texto claro de tráfego HTTPS criptografado.
6. Reconstruir, a partir de uma captura, a sequência completa DNS → TCP → TLS → HTTP que ocorre em uma navegação web típica.

## Pré-requisitos e cenário

| Recurso | Descrição |
|---|---|
| Estação do professor | Ubuntu Desktop 22.04+ recém-instalado |
| Servidor remoto | Mesma rede, **sem firewall**, com Python 3 instalado |
| Conectividade | Acesso à Internet a partir da estação |
| Conhecimento prévio | Capítulos 1 e 2 do livro-texto (modelo em camadas, TCP/UDP, HTTP, DNS) |

Os alunos devem ter lido as Seções 2.7 (programação de sockets) e 2.4 (DNS) antes da aula.

## Estrutura geral da aula

| Bloco | Tempo | Atividade |
|---|---|---|
| 1 | 15 min | Motivação e instalação do Wireshark |
| 2 | 10 min | Tour pela interface |
| 3 | 30 min | Demo 1 — TCP vs UDP via sockets Python |
| 4 | 25 min | Demo 2 — HTTP vs HTTPS |
| 5 | 15 min | Demo 3 — DNS |
| 6 | 15 min | Fechamento e encaminhamento dos labs do livro |
| **Total** | **~110 min** | |

---

## Bloco 1 — Instalação do Wireshark no Ubuntu Desktop

### Contextualização (5 min)

Antes de qualquer comando, retomar com a turma a definição do livro:

> *"A ferramenta básica para observar as mensagens trocadas entre entidades de protocolos em execução é denominada analisador de pacotes (packet sniffer). [...] copia passivamente mensagens enviadas e recebidas por seu computador; também exibe o conteúdo dos vários campos de protocolo das mensagens que captura."* (Capítulo 1)

Ressaltar a dupla face do tema: a mesma ferramenta usada para diagnóstico legítimo é usada por atacantes para vazar credenciais — ponto que motivou o tratamento de criptografia no Capítulo 8.

### Instalação (10 min)

```bash
# 1. Atualizar índices de pacote
sudo apt update

# 2. Instalar o Wireshark
sudo apt install wireshark -y
```

> **Atenção pedagógica:** durante a instalação aparece uma tela `dpkg-reconfigure` perguntando *"Should non-superusers be able to capture packets?"*. **Selecione "Yes"**. Esse é o gancho ideal para explicar:
>
> - Capturar pacotes exige acesso à interface de rede em modo promíscuo.
> - Esse é, normalmente, um privilégio de root.
> - O Debian/Ubuntu cria o grupo `wireshark` e atribui o capability `cap_net_raw` ao binário `dumpcap`, permitindo captura sem rodar a GUI como root.
> - **Rodar a GUI do Wireshark como root é má prática de segurança**, porque ela dissectiona conteúdo vindo de fontes não confiáveis.

```bash
# 3. Adicionar o usuário ao grupo wireshark
sudo usermod -aG wireshark $USER

# 4. Aplicar a mudança de grupo sem precisar fazer logout
newgrp wireshark

# 5. Confirmar
groups | grep wireshark
```

Abrir o Wireshark **pelo menu de aplicativos**, não via `sudo`.

---

## Bloco 2 — Tour pela interface

Antes de qualquer captura, percorrer com a turma os elementos da janela:

1. **Lista de interfaces** com sparkline de tráfego — escolher a interface ativa (`enp0s3`, `wlp2s0`, ou `lo` para loopback).
2. **Três painéis** após iniciar a captura:
   - lista de pacotes
   - árvore de protocolos do pacote selecionado (Ethernet → IP → TCP/UDP → ...)
   - hexdump
3. **Barra de filtro de exibição** (verde = sintaxe válida, vermelho = inválida).
4. **Statistics → Conversations** e **Statistics → Protocol Hierarchy**.

### Diferença essencial: filtros de captura vs. filtros de exibição

| | Filtro de **captura** | Filtro de **exibição** |
|---|---|---|
| Quando age | Antes de gravar | Depois de gravar |
| Sintaxe | BPF | Wireshark |
| Exemplo | `host 192.168.1.10` | `ip.addr == 192.168.1.10` |
| Onde fica | Tela inicial / Capture Options | Barra acima da lista de pacotes |

Esse é o ponto onde os alunos mais se confundem. Vale 1 min de slide.

Faça uma captura curta (10 s) só de tráfego de fundo e mostre o filtro de exibição em ação:

```
tcp.port == 443
ip.src == 192.168.0.0/24
dns
```

---

## Bloco 3 — Demo 1: TCP vs UDP com sockets Python

Esta é a demonstração mais importante da aula porque os alunos veem **exatamente** o código que leram no Capítulo 2 produzir pacotes na rede.

### Preparação no servidor remoto

Copie os arquivos [`servidor/UDPServer.py`](servidor/UDPServer.py) e [`servidor/TCPServer.py`](servidor/TCPServer.py) para o servidor remoto. Os códigos são os do livro-texto (Capítulo 2, Seção 2.7), reproduzidos no diretório `servidor/` deste repositório.

### Preparação na estação do professor

Edite [`cliente/UDPClient.py`](cliente/UDPClient.py) e [`cliente/TCPClient.py`](cliente/TCPClient.py) e ajuste a variável `serverName` para o IP (ou nome) do servidor remoto.

### Roteiro da demonstração

**A ordem importa: UDP primeiro, TCP depois.** O contraste fica óbvio.

#### Passo 1 — Iniciar a captura

No Wireshark, **filtro de captura**:

```
host <IP_SERVIDOR> and port 12000
```

Isso evita poluir a tela com tráfego de fundo. Iniciar a captura na interface ativa.

#### Passo 2 — Executar o cliente UDP

No servidor remoto:

```bash
python3 UDPServer.py
```

Na estação:

```bash
python3 UDPClient.py
# Digitar: hello wireshark
# Receber:  HELLO WIRESHARK
```

**Pause a captura** e mostre à turma:

- **Apenas 2 pacotes no fio**: a mensagem do cliente e a resposta do servidor.
- Coluna *Protocol* mostra `UDP` em ambos.
- Expanda a árvore de um pacote: `Ethernet → IP → UDP → Data`.
  - **Não há handshake.**
  - **Não há ACK.**
  - O cabeçalho UDP tem só 8 bytes (porta origem, porta destino, comprimento, checksum).
- Clique no campo *Data*: a frase aparece **em texto claro** no hexdump à direita.

Conecte com a citação do livro:

> *"O UDP não é orientado para conexão e envia pacotes de dados independentes de um sistema final ao outro, sem nenhuma garantia de entrega."* (Capítulo 2, Seção 2.7)

**Salve a captura**: `File → Save As → demo1-udp.pcapng`.

#### Passo 3 — Executar o cliente TCP

Pare o servidor UDP e inicie o TCP:

```bash
python3 TCPServer.py
```

Reinicie a captura no Wireshark (mesmo filtro). Na estação:

```bash
python3 TCPClient.py
# Digitar: hello wireshark
# Receber:  HELLO WIRESHARK
```

Pause. Agora a tela tem **muito mais pacotes** para entregar exatamente a mesma frase.

Aponte, na ordem de cima para baixo:

| # | Pacote | Significado |
|---|---|---|
| 1 | `[SYN]` | Cliente pede para abrir conexão |
| 2 | `[SYN, ACK]` | Servidor aceita e também sincroniza |
| 3 | `[ACK]` | Cliente confirma — fim do *3-way handshake* |
| 4 | `[PSH, ACK]` "hello wireshark" | Dados do cliente |
| 5 | `[ACK]` | Servidor confirma recebimento |
| 6 | `[PSH, ACK]` "HELLO WIRESHARK" | Resposta do servidor |
| 7 | `[ACK]` | Cliente confirma |
| 8 | `[FIN, ACK]` | Servidor inicia encerramento |
| 9 | `[ACK]` | Cliente reconhece |
| 10 | `[FIN, ACK]` | Cliente também encerra |
| 11 | `[ACK]` | Servidor reconhece — conexão fechada |

> **Truque visual:** filtre com `tcp.flags.syn == 1` para isolar o handshake. Depois remova o filtro.

#### Passo 4 — Visualizar o diagrama de sequência

Com qualquer pacote da conexão TCP selecionado:

`Statistics → Flow Graph → Limit to display filter` (com filtro `tcp`).

O Wireshark desenha o diagrama de sequência, idêntico à **Figura 2.29 do livro**. Esse é o momento "uau" da aula — o desenho do livro materializado a partir do código real.

**Salve a captura**: `File → Save As → demo1-tcp.pcapng`.

#### Passo 5 — Comparação final

| Característica | UDP | TCP |
|---|---|---|
| Pacotes para entregar 1 frase + resposta | 2 | ~10–11 |
| Estabelecimento de conexão | Não | SYN / SYN-ACK / ACK |
| Confirmação de entrega | Não | ACKs em todos os dados |
| Encerramento ordenado | Não | FIN handshake |
| Tamanho do cabeçalho | 8 bytes | 20+ bytes |
| Garantia de entrega | Não | Sim |
| Garantia de ordem | Não | Sim |

---

## Bloco 4 — Demo 2: HTTP vs HTTPS

### Preparação

Para o lado HTTP, suba um servidor simples no servidor remoto:

```bash
# No servidor remoto
mkdir -p /tmp/www && cd /tmp/www
echo '<h1>Pagina de teste</h1><p>Wireshark lab.</p>' > index.html
sudo python3 -m http.server 80
```

> Por que servidor próprio? Porque a maioria dos sites públicos hoje redireciona para HTTPS via HSTS. Servir HTTP localmente garante que a turma veja realmente o tráfego em claro.
>
> Alternativa: usar `http://neverssl.com`, criado justamente para nunca migrar para HTTPS.

### HTTP em texto claro

Inicie nova captura no Wireshark com filtro de captura:

```
host <IP_SERVIDOR> and port 80
```

Na estação:

```bash
curl http://<IP_SERVIDOR>/
```

Pare a captura. Filtro de exibição: `http`.

Mostre à turma:

- A requisição `GET / HTTP/1.1` aparece **legível** no painel de detalhes.
- Cabeçalhos `Host:`, `User-Agent:`, `Accept:` totalmente expostos.
- Corpo da resposta HTML também legível.
- **Botão direito → Follow → HTTP Stream** reconstrói a conversa inteira como se fosse um terminal.

> Reflexão para a turma: imagine que isso fosse um login. Usuário e senha cruzariam a rede em texto claro, à mercê de qualquer analisador no caminho.

**Salve**: `demo2-http.pcapng`.

### HTTPS criptografado

Nova captura, filtro `host example.com and port 443` (ou outro site HTTPS conhecido).

```bash
curl https://example.com/
```

Pare. Filtro de exibição: `tls`.

Mostre:

- O **handshake TLS** é visível: `Client Hello`, `Server Hello`, `Certificate`, `Server Hello Done`, `Change Cipher Spec`, etc.
- O `Client Hello` **vaza o SNI** — o nome do servidor visitado aparece em claro no campo *Extension: server_name*. Bom gancho para mencionar **ECH (Encrypted Client Hello)** como tópico de pesquisa atual.
- A partir do primeiro `Application Data`, **só lixo criptografado** no hexdump: nem a URL, nem os cabeçalhos, nem o corpo são legíveis.

Comparativamente, no HTTP a mesma operação expunha tudo.

**Salve**: `demo2-https.pcapng`.

### Quadro comparativo

| | HTTP (porta 80) | HTTPS (porta 443) |
|---|---|---|
| Conteúdo do `GET` | Visível | Criptografado |
| Cabeçalhos | Visíveis | Criptografados |
| Corpo da resposta | Visível | Criptografado |
| Nome do servidor (SNI) | N/A | **Visível** (até ECH se popularizar) |
| IP de origem/destino | Visível | Visível |
| Tamanho dos pacotes | Visível | Visível |

> Importante: HTTPS não esconde **com quem** você fala, apenas **o que** é dito.

---

## Bloco 5 — Demo 3: DNS

### Por que esta terceira demo?

Até aqui a turma viu UDP isoladamente (sockets do Cap. 2) e HTTP/HTTPS isoladamente. **Falta mostrar como esses pedaços se compõem em uma navegação real.** O DNS é o protocolo perfeito para fechar:

1. **Reforça o UDP** — o livro afirma explicitamente que *"o protocolo DNS utiliza UDP e usa a porta 53"* (Capítulo 2, Seção 2.4). A turma vê na prática a justificativa de design: consultas curtas, rápidas, sem necessidade de conexão persistente.
2. **Conecta camadas** — uma única navegação a `https://www.exemplo.com` envolve DNS (UDP/53) + TCP handshake + TLS handshake + HTTP. O Wireshark mostra isso como uma narrativa contínua.
3. **É curta** — 15 minutos bastam.

### Roteiro

#### Passo 1 — Limpar o cache DNS local

Sem isso, a consulta pode não chegar à rede:

```bash
sudo resolvectl flush-caches
# (alternativa em sistemas mais antigos: sudo systemd-resolve --flush-caches)
```

#### Passo 2 — Capturar uma resolução simples

Inicie captura sem filtro de captura. Filtro de exibição: `dns`.

```bash
nslookup www.kernel.org
```

Pause. Você verá tipicamente 2 pacotes:

- **Standard query A www.kernel.org** — saindo (UDP, porta destino 53).
- **Standard query response A www.kernel.org A 145.40.73.55** — voltando.

Expanda a árvore de protocolos do segundo pacote e mostre os campos descritos no livro:

- *Transaction ID*
- *Flags* (com os bits de *recursion desired*, *recursion available*, *authoritative*)
- *Questions*: 1
- *Answer RRs*: 1+
- Dentro de *Answers*: o registro **Type A** com o IP

Esse é o **formato de mensagem DNS da Figura 2.21 do livro**, em campo de batalha real.

**Salve**: `demo3-dns-simples.pcapng`.

#### Passo 3 — A narrativa completa de uma navegação

Limpe o cache de novo e inicie captura **sem filtro de captura**. Depois, no terminal:

```bash
curl -v https://www.kernel.org/ -o /dev/null
```

Pare a captura. **Sem filtro de exibição inicialmente**, mostre à turma a sequência de pacotes numerada:

| # aprox. | Protocolo | O que é |
|---|---|---|
| 1 | DNS | Standard query A www.kernel.org (UDP/53) |
| 2 | DNS | Standard query response (UDP/53) |
| 3 | TCP | SYN para o IP retornado, porta 443 |
| 4 | TCP | SYN/ACK |
| 5 | TCP | ACK |
| 6 | TLSv1.3 | Client Hello |
| 7 | TLSv1.3 | Server Hello, Certificate, ... |
| ... | ... | Resto do handshake TLS |
| ... | TLSv1.3 | Application Data (HTTP dentro do TLS) |
| ... | TCP | FIN/ACK encerrando a conexão |

Esse "filme" amarra **toda a aula**:

- Demo 1 explicou TCP vs UDP — aqui aparecem os dois lado a lado.
- Demo 2 explicou HTTP vs HTTPS — aqui o HTTPS aparece em contexto.
- Demo 3 explica como tudo começa: o DNS é o tradutor que torna tudo mais possível.

> Pergunta provocativa para fechar: **o DNS rodou em UDP. O que aconteceria se um pacote de consulta DNS se perdesse?** (Resposta: o cliente reenviaria após timeout — a confiabilidade fica na aplicação, não no transporte. Compare com HTTP, que delega isso ao TCP.)

**Salve**: `demo3-navegacao-completa.pcapng`.

---

## Bloco 6 — Fechamento

Encaminhe os alunos para os laboratórios do livro como atividade prática extraclasse:

- **Wireshark Lab: Getting Started** (final do Capítulo 1)
- **Wireshark Lab: HTTP** (final do Capítulo 2)
- **Wireshark Lab: DNS** (final do Capítulo 2)

Cada um traz roteiros prontos com perguntas guiadas que reforçam o conteúdo da aula. Os arquivos `.pcap` salvos durante a aula servem como gabarito visual de referência.

### Avaliação sugerida

Peça que cada aluno entregue um pequeno relatório com:

1. Captura própria de uma resolução DNS + navegação HTTPS para um site à sua escolha.
2. Identificação no relatório dos pacotes correspondentes a: DNS query, DNS response, TCP SYN, TLS Client Hello, primeiro Application Data, FIN.
3. Resposta à pergunta: *"O que um analisador de pacotes posicionado entre você e o site consegue saber sobre sua navegação? E o que ele não consegue?"*

---

## Dicas operacionais

- **Aumente o tamanho das fontes** antes da aula em `Edit → Preferences → Appearance → Fonts and Colors`. O default é ilegível em telão.
- **Salve os `.pcap` antes da aula**: se algo der errado ao vivo (rede caiu, servidor remoto fora do ar), você abre o arquivo salvo e segue.
- **Tenha uma colorização customizada**: em `View → Coloring Rules`, destaque pacotes TCP `[SYN]` e `[FIN]` com cores fortes. Ajuda muito a turma a localizar visualmente o handshake.
- **Não rode o Wireshark como root**. Se a captura não funcionar, problema é com o grupo `wireshark` ou com o capability do `dumpcap`, não com o usuário. Diagnóstico: `getcap $(which dumpcap)` deve retornar `cap_net_admin,cap_net_raw=eip`.
- **Para HTTPS com decriptação**, é possível configurar o Firefox para escrever as chaves de sessão em `SSLKEYLOGFILE` e o Wireshark para lê-las em `Preferences → Protocols → TLS → (Pre)-Master-Secret log filename`. Isso provavelmente é tema para uma segunda aula sobre TLS — não tente espremer aqui.
- **Backup de rede**: tenha um hotspot de celular pronto. Demos de DNS e HTTPS dependem de Internet.

## Referências

- Kurose, J. F.; Ross, K. W. *Redes de Computadores e a Internet*. Capítulos 1 e 2.
- Wireshark User's Guide — <https://www.wireshark.org/docs/wsug_html_chunked/>
- Wireshark Labs (site de apoio do livro) — <https://gaia.cs.umass.edu/kurose_ross/wireshark.htm>

## Estrutura deste repositório

```
.
├── README.md                  # este roteiro
├── servidor/
│   ├── UDPServer.py           # servidor UDP do Capítulo 2
│   └── TCPServer.py           # servidor TCP do Capítulo 2
└── cliente/
    ├── UDPClient.py           # cliente UDP do Capítulo 2
    └── TCPClient.py           # cliente TCP do Capítulo 2
```

## Licença

Material didático sob CC BY-SA 4.0. Os códigos de socket em `servidor/` e `cliente/` são adaptados do livro-texto e mantêm a atribuição original aos autores.

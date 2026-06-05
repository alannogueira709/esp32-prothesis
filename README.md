# Gesture Recognition + ESP32 Servo Control

Projeto que integra um reconhecedor de gestos em Python com firmware para ESP32 que controla servomotores. A ideia é detectar movimentos/manipulações da mão no computador e enviar comandos seriais para um ESP32 que move servos.

## Visão geral
- **Reconhecimento de gestos (host)**: código Python em `src/gesture_to_esp` que captura/analisa imagens (ou landmarks) e traduz gestos em comandos.
- **Firmware ESP32 (controle de servos)**: projetos PlatformIO em `gesture_recognition/firmware/esp32_servo_control` e `esp32_servo_control` que compilam e enviam o binário para a placa.
- **Modelos**: modelos de hand/landmark estão em `src/models`.

## Estrutura do repositório

- [gesture_recognition/firmware/esp32_servo_control](gesture_recognition/firmware/esp32_servo_control) — código PlatformIO para ESP32 (controle dos servos).
- [gesture_recognition/src/gesture_to_esp](gesture_recognition/src/gesture_to_esp) — aplicação Python que detecta gestos e envia comandos seriais.
- [gesture_recognition/src/models](gesture_recognition/src/models) — modelos necessários para detecção/landmarks.

## Pré-requisitos

- Python 3.8+ (recomenda-se 3.10/3.11)
- PlatformIO (VS Code extension ou CLI) para compilar e enviar firmware ao ESP32
- Um cabo USB e uma placa ESP32 com servos conectados

## Como usar

1. Preparar o ambiente Python

```bash
python -m venv venv
venv\\Scripts\\activate    # Windows
pip install -r gesture_recognition/src/gesture_to_esp/requirements.txt  # se existir
```

Se não houver `requirements.txt`, abra `gesture_recognition/src/gesture_to_esp` e instale as dependências listadas (por exemplo, packages de visão/ML/serial).

2. Configurar porta serial

Edite `gesture_recognition/src/gesture_to_esp/config.py` para ajustar a porta serial (ou passe via variável de ambiente, conforme implementação).

3. Rodar o reconhecedor de gestos (host)

```bash
cd gesture_recognition/src/gesture_to_esp
python -m gesture_to_esp
```

4. Compilar e enviar firmware ao ESP32

Usando PlatformIO (CLI):

```bash
cd gesture_recognition/firmware/esp32_servo_control
pio run --target upload
```

Ou use a extensão PlatformIO no VS Code e clique em "Upload" no projeto `esp32_servo_control`.


## Dicas e troubleshooting

- Verifique a porta serial correta no Gerenciador de Dispositivos (Windows) e em `config.py`.
- Se o reconhcedor usa webcam, feche outros apps que ocupem a câmera.
- Ao conectar servos diretamente ao ESP32, confira alimentação adequada (evite alimentar servos pelo 3.3V da placa se eles consomem muito; use fonte externa comum com GND em comum).

## Contribuição

1. Abra uma issue descrevendo o que pretende alterar.
2. Crie um branch com uma mensagem clara.
3. Faça um pull request; descreva como testar suas mudanças.

## Licença
Este projeto está licenciado sob a Apache License, Version 2.0. Veja o arquivo `LICENSE` para o texto completo ou acesse http://www.apache.org/licenses/LICENSE-2.0.

---
Se quiser, eu posso:
- ajustar o README com itens mais técnicos (ex.: dependências exatas),
- gerar `requirements.txt` com base nos imports do código Python, ou
- adicionar exemplo de comandos seriais esperados pelo firmware.
Diga o que prefere que eu faça a seguir.

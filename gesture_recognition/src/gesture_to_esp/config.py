from dataclasses import dataclass, field
from typing import Optional

ODIN_ASCII = """
                                                        
                                      ..:::::.              
                                   :------::::-:.           
                         .:::--===+===--:::::.::---:.       
              ..  ...:-=========+++++++====--:::::--===:    
             .:------=====+=++=+=++++++++++++=-.    .::.    
            .:--::::-====++====+++++==========-             
       ...:-:--:..:--====+===-==+=+===----::-=:             
    :--:::-:-:...:---==++==----===++======-::=-             
 .:----:::--:. .::--=++==:..:::--=+++++++==:-=-.            
::-----::--:. ..:-:-+===: ...:--======+======:              
:-----:---:..  .:::-===:  ...:-:--==+========-.             
::---:-:--:.    ..:-==:.....::::--==============-:.         
:----:::-:.    ....:=-.:-::::-------=======-----====:.      
-:---:::::.    .....-::----:-==---=========----------==:.   
::---:::::. .......--------:--------=-====----::::::::-:.   
::----::::. ......:::-----:----------===--:::::::::::..::   
:-===-::-:  ...  .:::::--:-------:--====-::::....::......   
-==++=:--.   :.  .:--::----------:--==---::::.....   ...-:  
++++=-==:    .  ..::::::------------------::::...    ...==  
+++====:     .  .:::::::::---------:---=------:..  ....:=:. 
*+===-:      .. ..::--:::::---:::---====--===--::.....:==:  
*+===:        .  ..:---::-----::--==========----::::::--:   
+++==:        .   :::::::----------=======-=---::::.:---    
-==-:.:..     ..  .::--:-:::---=--=====-===----::...-=:     
:::..........:..  ...:::-::::-=--------==--::...:::-=:      
...............       .:::::::----:::.:---:::.:::--=-:      
..............        ..::::::.:::::-::-:-------==-::.      
......... ....           .::::::::::------=-::-::.          
.............             .::-=---:--------:                
"""

@dataclass
class Config:
    CAMERA_ID: int = 0
    FRAME_WIDTH: int = 1080
    FRAME_HEIGHT: int = 720
    MAX_HANDS: int = 1
    DETECTION_CONFIDENCE: float = 0.7
    TRACKING_CONFIDENCE: float = 0.5
    SERIAL_PORT: Optional[str] = None
    SERIAL_BAUD: int = 115200
    SERIAL_TIMEOUT: Optional[float] = None
    SEND_INTERVAL: float = 0.05
    WRIST: int = 0
    POLEGAR_PONTA: int = 4
    INDICADOR_PONTA: int = 8
    INDICADOR_MCP: int = 5
    MEIO_PONTA: int = 12
    MEIO_MCP: int = 9
    ANELAR_PONTA: int = 16
    ANELAR_MCP: int = 13
    MINDINHO_PONTA: int = 20
    MINDINHO_MCP: int = 17
    DEDOS: dict = field(default_factory=lambda: {
        "polegar":  (4, 2, 3),
        "indicador":  (8, 5, 6),
        "meio": (12, 9, 10),
        "anelar":   (16, 13, 14),
        "mindinho":  (20, 17, 18),
    })
    GESTURE_THRESHOLD_OPEN: float = 0.75
    GESTURE_THRESHOLD_CLOSED: float = 0.35
    NUM_SERVOS: int = 5
    SERVO_MIN: int = 0
    SERVO_MAX: int = 180
    SHOW_PREVIEW: bool = True
    WINDOW_NAME: str = "Controle da protese v1.0"
    HAND_MODEL_PATH: str = "models/hand_landmarker.task"


def print_serial_config(config):
    art_lines = ODIN_ASCII.strip("\n").split("\n")
    art_width = max(len(line) for line in art_lines)

    serial_text = [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "  ╔════════════════════════════════════════════════╗",
        "  ║  [Serial] Porta serial não configurada.       ║",
        "  ╚════════════════════════════════════════════════╝",
        "",
        "  Porta serial (ex: COM3 ou /dev/ttyUSB0):",
        "",
        "  Taxa de baud (padrão {}):".format(config.SERIAL_BAUD),
        "",
        "  Timeout em segundos (padrão {}):".format(config.SERIAL_TIMEOUT),
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ]

    print()
    for i in range(max(len(art_lines), len(serial_text))):
        art = art_lines[i] if i < len(art_lines) else ""
        txt = serial_text[i] if i < len(serial_text) else ""
        if art or txt:
            print(art.ljust(art_width) + "    " + txt)


def interactive_setup(config=None):
    if config is None:
        config = Config()

    print_serial_config(config)

    config.SERIAL_PORT = input("  > Porta: ")
    baud = input("  > Baud (ENTER para {}): ".format(config.SERIAL_BAUD))
    timeout = input("  > Timeout (ENTER para {}s): ".format(config.SERIAL_TIMEOUT))

    if baud.strip():
        config.SERIAL_BAUD = int(baud)
    if timeout.strip():
        config.SERIAL_TIMEOUT = float(timeout)

    print("\n  [OK] Configurado: {} @ {} baud, timeout={}s".format(
        config.SERIAL_PORT, config.SERIAL_BAUD, config.SERIAL_TIMEOUT))

    return config


if __name__ == "__main__":
    cfg = interactive_setup()

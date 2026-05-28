from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

doc = Document()

style = doc.styles["Normal"]
font = style.font
font.name = "Consolas"
font.size = Pt(10)

for level in range(1, 4):
    hs = doc.styles[f"Heading {level}"]
    hs.font.name = "Consolas"
    hs.font.color.rgb = RGBColor(0, 120, 0)

# ===== PORTADA =====
for _ in range(4):
    doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("SECURE DATA GRAPHER")
run.font.size = Pt(28)
run.bold = True
run.font.color.rgb = RGBColor(0, 150, 0)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run("Guia de instalacion paso a paso\npara Raspberry Pi 4 Model B + Raspbian OS\n\nProyecto EPOC")
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(80, 80, 80)

doc.add_paragraph()
info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = info.add_run("Cifrado Cesar + Seguridad Avanzada  |  Mayo 2026")
run.font.size = Pt(10)
run.font.color.rgb = RGBColor(120, 120, 120)

doc.add_page_break()

# ===== INDICE =====
doc.add_heading("Indice", level=1)
indice_items = [
    "1. Requisitos de hardware y software",
    "2. Instalar Raspberry Pi OS en la SD",
    "3. Configuracion inicial del sistema",
    "4. Conectarse a la Raspberry Pi por SSH",
    "5. Transferir los archivos del bot",
    "6. Ejecutar el instalador automatico",
    "7. Configurar variables de entorno",
    "8. Probar el bot localmente",
    "9. Configurar ngrok (tunel publico)",
    "10. Gestionar el servicio con systemd",
    "11. Ver graficos desde el navegador",
    "12. Enviar datos desde otro dispositivo",
    "13. Solucion de problemas comunes",
    "14. Comandos de referencia rapida",
]
for item in indice_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(2)
    p.runs[0].font.size = Pt(10)

doc.add_page_break()

# =====================================================================
secciones = [
    ("1. Requisitos de hardware y software", [
        ("Hardware necesario", [
            "Raspberry Pi 4 Model B (2GB, 4GB u 8GB RAM)",
            "MicroSD de 16GB o mas (Clase 10 recomendada)",
            "Cargador USB-C 5V/3A",
            "Cable Ethernet o WiFi funcional",
            "(Opcional) Computadora con lector de SD para grabar la imagen",
        ]),
        ("Software necesario (en su PC)", [
            "Raspberry Pi Imager (https://www.raspberrypi.com/software/)",
            "PuTTY (Windows) o ssh (Linux/Mac) para conectarse",
            "Cliente SCP o USB para transferir archivos",
            "Navegador web para ver los graficos",
        ]),
    ]),

    ("2. Instalar Raspberry Pi OS en la SD", [
        ("Paso 1: Descargar e instalar Raspberry Pi Imager",
         "Vaya a https://www.raspberrypi.com/software/ y descargue el instalador. Instalelo."),
        ("Paso 2: Abrir Raspberry Pi Imager",
         "Conecte la microSD a su computadora. Abra Raspberry Pi Imager."),
        ("Paso 3: Seleccionar SO",
         "CHOOSE OS -> Raspberry Pi OS (other) -> Raspberry Pi OS Lite (32-bit).\n"
         "NOTA: Version Lite sin escritorio, ideal para servidores."),
        ("Paso 4: Seleccionar tarjeta SD",
         "CHOOSE STORAGE -> seleccione su microSD."),
        ("Paso 5: Configuracion avanzada (IMPORTANTE)",
         "Click en el icono de engranaje (⚙) esquina inferior derecha.\n"
         "Active:\n"
         "  - Set hostname:  grapherpi\n"
         "  - Enable SSH:    Use password authentication\n"
         "  - Set username:  pi\n"
         "  - Set password:  (contrasena segura)\n"
         "  - Configure WiFi: (si no usa Ethernet)\n"
         "  - Set locale: (su pais, idioma, zona horaria)"),
        ("Paso 6: Escribir la imagen",
         "Click WRITE. Confirme advertencia. Espere 5-10 min. Retire la SD."),
    ]),

    ("3. Configuracion inicial del sistema", [
        ("Paso 1: Insertar SD y encender",
         "Inserte la SD en la Pi. Conecte Ethernet (si usa) y el cargador USB-C.\n"
         "La primera vez tarda 30s-2min en arrancar."),
        ("Paso 2: Encontrar la IP",
         "Revise el router o use app Fing (celular).\n"
         "La IP sera algo como 192.168.1.X.\n"
         "O desde Linux/Mac: ping grapherpi.local"),
        ("Paso 3: Conectarse por SSH",
         "Windows (PuTTY):\n"
         "  Host Name: 192.168.1.X, Port: 22, Connection: SSH, Open.\n"
         "  Login: pi, Password: (la que configuro)\n\n"
         "Linux/Mac:\n"
         "  ssh pi@192.168.1.X\n"
         "  yes + password"),
    ]),

    ("4. Conectarse a la Raspberry Pi por SSH", [
        ("Ya conectado, actualice el sistema:",
         "sudo apt-get update && sudo apt-get upgrade -y\n\n"
         "Tarda varios minutos. Espere."),
        ("Verifique Python 3:",
         "python3 --version\n\n"
         "Deberia ver: Python 3.11.2"),
    ]),

    ("5. Transferir los archivos del bot", [
        ("Instalar Git:",
         "sudo apt-get install -y git"),
        ("Opcion A: Git (recomendada)",
         "Si subio a GitHub:\n"
         "  git clone https://github.com/TU_USUARIO/secure-grapher.git /home/pi/secure-grapher"),
        ("Opcion B: SCP desde su PC",
         "En su computadora (NO en la Pi), en la carpeta del proyecto:\n"
         "  scp -r ./bot/* pi@192.168.1.X:/home/pi/secure-grapher/\n\n"
         "Reemplace 192.168.1.X con la IP real de su Pi."),
        ("Verificar archivos:",
         "ls -la /home/pi/secure-grapher/\n\n"
         "Debe ver: config.py, crypto.py, grapher.py, install_pi.sh, run.py,\n"
         "security.py, server.py, .env.example, client_example.py, requirements.txt"),
    ]),

    ("6. Ejecutar el instalador automatico", [
        ("Que hace el instalador:", [
            "Actualizar paquetes del sistema",
            "Instalar dependencias (Python, librerias graficas, etc.)",
            "Descargar ngrok para ARM64",
            "Crear entorno virtual Python",
            "Instalar todas las dependencias Python (Flask, matplotlib, etc.)",
            "Crear archivo .env",
            "Crear e iniciar el servicio systemd (auto-arranque)",
        ]),
        ("Ejecutar:",
         "cd /home/pi/secure-grapher && bash install_pi.sh\n\n"
         "Pedira su contrasena de sudo varias veces. Es normal.\n"
         "Tarda 5-15 min segun internet y velocidad de SD.\n\n"
         "AL FINALIZAR, el servicio ya esta corriendo automaticamente."),
    ]),

    ("7. Configurar variables de entorno", [
        ("Edite el .env:",
         "sudo nano /opt/secure-grapher/.env"),
        ("Variables que DEBE cambiar:",
         "API_KEY     -> Clave secreta para autenticar sus requests. Ej: MiClave123\n"
         "SECRET_KEY  -> Clave para firmar HMAC. Distinta a API_KEY.\n"
         "CAESAR_SHIFT -> Desplazamiento Cesar (1-25). Default: 7.\n"
         "NGROK_AUTHTOKEN -> Solo si usa ngrok. Registrese en ngrok.com"),
        ("Guardar y reiniciar:",
         "Ctrl+O, Enter, Ctrl+X\n"
         "sudo systemctl restart secure-grapher"),
    ]),

    ("8. Probar el bot localmente", [
        ("Verificar estado del servicio:",
         "sudo systemctl status secure-grapher\n\n"
         "Debe mostrar 'active (running)' en verde."),
        ("Health check:",
         "curl http://localhost:5000/health\n\n"
         'Respuesta: {"encrypted":"...","status":"ok"}'),
        ("Enviar datos de prueba:",
         "cd /opt/secure-grapher && source venv/bin/activate && python client_example.py\n\n"
         "Debe ver 30 puntos enviados correctamente."),
        ("Verificar grafico generado:",
         "ls -la /opt/secure-grapher/graphs/\n\n"
         "Debe aparecer last_graph.png de varios KB."),
    ]),

    ("9. Configurar ngrok (tunel publico)", [
        ("Paso 1: Registrarse",
         "Vaya a https://ngrok.com, cree cuenta gratis.\n"
         "En el dashboard copie su Auth Token."),
        ("Paso 2: Configurar token",
         "sudo nano /opt/secure-grapher/.env\n\n"
         "Busque NGROK_AUTHTOKEN y pegue su token:\n"
         "  NGROK_AUTHTOKEN=2xQpR...su_token...\n"
         "Guardar: Ctrl+O, Enter, Ctrl+X"),
        ("Paso 3: Habilitar ngrok en el servicio",
         "sudo sed -i 's|ExecStart=.*|ExecStart=/opt/secure-grapher/venv/bin/python /opt/secure-grapher/run.py --ngrok|' /etc/systemd/system/secure-grapher.service\n"
         "sudo systemctl daemon-reload\n"
         "sudo systemctl restart secure-grapher"),
        ("Paso 4: Ver URL publica",
         "sudo journalctl -u secure-grapher -n 20 --no-pager\n\n"
         "Busque: Tunel ngrok establecido: https://abc123.ngrok-free.app\n\n"
         "Esa URL es su endpoint publico. Ej: https://abc123.ngrok-free.app/api/v1/data"),
    ]),

    ("10. Gestionar el servicio con systemd", [
        ("Comandos utiles:", [
            ("Ver estado", "sudo systemctl status secure-grapher"),
            ("Ver logs en tiempo real", "sudo journalctl -u secure-grapher -f"),
            ("Ultimas 50 lineas", "sudo journalctl -u secure-grapher -n 50 --no-pager"),
            ("Reiniciar", "sudo systemctl restart secure-grapher"),
            ("Detener", "sudo systemctl stop secure-grapher"),
            ("Iniciar", "sudo systemctl start secure-grapher"),
            ("Deshabilitar auto-inicio", "sudo systemctl disable secure-grapher"),
            ("Habilitar auto-inicio", "sudo systemctl enable secure-grapher"),
        ]),
    ]),

    ("11. Ver graficos desde el navegador", [
        ("Abrir el navegador en cualquier dispositivo de la red:",
         "http://192.168.1.X:5000/api/v1/graph\n\n"
         "(Reemplace X con la IP de su Pi)\n\n"
         "Obten la imagen PNG actualizada en tiempo real."),
        ("Ver datos en crudo (cifrados):",
         'curl -H "X-API-Key: MiClave123" http://localhost:5000/api/v1/data'),
    ]),

    ("12. Enviar datos desde otro dispositivo", [
        ("Desde Python (con libreria incluida)",
         "En cualquier maquina con Python, copie la carpeta 'bot' y use:\n\n"
         "from crypto import SecurePayload\n"
         "import requests\n\n"
         "secure = SecurePayload()\n"
         'API_URL = "http://192.168.1.X:5000/api/v1/data"\n'
         'API_KEY = "MiClave123"\n\n'
         'datos = {"x": 1, "value": 25.5}\n'
         "encrypted = secure.encode(datos)\n\n"
         "resp = requests.post(\n"
         '    API_URL,\n'
         "    data=encrypted,\n"
         '    headers={"Content-Type": "text/plain", "X-API-Key": API_KEY}\n'
         ")\n"
         "print(resp.json())"),
        ("Desde curl (rapido para pruebas):",
         'curl -X POST http://192.168.1.X:5000/api/v1/data \\\n'
         '  -H "Content-Type: text/plain" \\\n'
         '  -H "X-API-Key: MiClave123" \\\n'
         '  -d \'{"x": 1, "value": 42.5}\''),
        ("Envio multiple (bulk):",
         '[{"x": 1, "value": 10}, {"x": 2, "value": 20}, {"x": 3, "value": 30}]'),
    ]),

    ("13. Solucion de problemas comunes", [
        ("El servicio no arranca",
         "Revise logs: sudo journalctl -u secure-grapher -n 50 --no-pager\n"
         "Causas: error en .env, puerto 5000 ocupado, falta dependencia."),
        ("No me conecto por SSH",
         "Verifique que la Pi esta encendida. Revise la IP.\n"
         "Pruebe con cable Ethernet en vez de WiFi."),
        ("ngrok no funciona",
         "Verifique el Auth Token en .env.\n"
         "ngrok gratuito tiene limite de 40 conexiones/minuto."),
        ("Error: Address already in use",
         "Cambie NGROK_PORT en .env (ej: 5001) o mate el proceso:\n"
         "  sudo lsof -i :5000\n"
         "  sudo kill -9 [PID]"),
        ("El grafico se ve mal",
         "Ajuste GRAPH_FIGSIZE y GRAPH_DPI en .env."),
    ]),

    ("14. Comandos de referencia rapida", [
        ("Tabla de comandos", [
            ("Servicio - Estado", "sudo systemctl status secure-grapher"),
            ("Servicio - Logs", "sudo journalctl -u secure-grapher -f"),
            ("Servicio - Reiniciar", "sudo systemctl restart secure-grapher"),
            ("Servicio - Detener", "sudo systemctl stop secure-grapher"),
            ("Servicio - Iniciar", "sudo systemctl start secure-grapher"),
            ("Editar config", "sudo nano /opt/secure-grapher/.env"),
            ("Ver IP de la Pi", "hostname -I"),
            ("Health check", "curl http://localhost:5000/health"),
            ("Enviar dato prueba", 'curl -X POST http://localhost:5000/api/v1/data -H "Content-Type: text/plain" -H "X-API-Key: MiClave123" -d \'{"x":1,"value":42}\''),
            ("Ver grafico", "curl http://localhost:5000/api/v1/graph -o grafico.png"),
            ("Ver datos", 'curl -H "X-API-Key: MiClave123" http://localhost:5000/api/v1/data'),
            ("Limpiar datos", 'curl -X POST -H "X-API-Key: MiClave123" http://localhost:5000/api/v1/data/clear'),
        ]),
    ]),
]

for sec_title, contenido in secciones:
    doc.add_heading(sec_title, level=1)
    for item in contenido:
        if isinstance(item, tuple) and len(item) == 2:
            tit, desc = item
            p = doc.add_paragraph()
            run = p.add_run(tit)
            run.bold = True
            run.font.size = Pt(11)

            if isinstance(desc, list):
                for sub in desc:
                    doc.add_paragraph(sub, style="List Bullet")
            elif desc.startswith("sudo") or desc.startswith("curl") or desc.startswith("ssh") or desc.startswith("cd") or desc.startswith("from crypto") or desc.startswith("pip") or desc.startswith("git clone") or desc.startswith("scp") or desc.startswith("ls") or desc.startswith("python") or desc.startswith("source") or desc.startswith("http://") or desc.startswith("["):
                p2 = doc.add_paragraph()
                run2 = p2.add_run(desc)
                run2.font.size = Pt(9.5)
                run2.font.name = "Consolas"
            else:
                doc.add_paragraph(desc)

        elif isinstance(item, tuple) and len(item) == 3:
            tit, subitems = item
            p = doc.add_paragraph()
            run = p.add_run(tit)
            run.bold = True
            run.font.size = Pt(11)
            if isinstance(subitems, list):
                for st, sc in subitems:
                    p2 = doc.add_paragraph(style="List Bullet")
                    run2 = p2.add_run(f"{st}: ")
                    run2.bold = True
                    run3 = p2.add_run(sc)
                    run3.font.size = Pt(9.5)
                    run3.font.name = "Consolas"

        elif isinstance(item, list):
            for sub in item:
                doc.add_paragraph(sub, style="List Bullet")
        else:
            doc.add_paragraph(str(item))

    doc.add_page_break()

# ===== TABLA COMANDOS RAPIDOS =====
# Remove the last page break and add table
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("--- Fin de la guia ---")
run.font.size = Pt(10)
run.font.color.rgb = RGBColor(120, 120, 120)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Secure Data Grapher  |  Proyecto EPOC  |  Cifrado Cesar + Seguridad Avanzada")
run.font.size = Pt(9)
run.font.color.rgb = RGBColor(120, 120, 120)

import tempfile, shutil, time
final_path = os.path.join(os.path.dirname(__file__), "Guia_Secure_Data_Grapher_EPOC.docx")
tmp_path = os.path.join(tempfile.gettempdir(), f"grapher_guide_{int(time.time())}.docx")
doc.save(tmp_path)
shutil.copy2(tmp_path, final_path)
os.remove(tmp_path)
print(f"Documento guardado: {final_path}")
print(f"Tamano: {os.path.getsize(final_path)} bytes")

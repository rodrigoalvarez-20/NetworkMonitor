import os
from pprint import pprint
from flask import Flask, make_response, send_file
import pygal

from trappy import get_interface_status

app = Flask(__name__)

@app.get("/api")
def test_api():
    return make_response({"message": "Api correcta"}, 200)

@app.get("/api/monitor/status")
def get_int_status():
    int_status = get_interface_status()

    if int_status != None:
        if len(int_status) == 0:
            # Ver si lo puedo jalar desde el monitor
            return make_response({"error":"Estado de la interfaz desconocido. No se han realizado cambios en ella"}, 200)
        else:
            all_status = [ x.split(" = ")[1].replace("\n", "") for x in int_status ]
            return make_response({
                "message": "Se ha obtenido el estado de la interfaz Fa2/0",
                "status": all_status[len(all_status)-1],
                "all_status": all_status
            }, 200)

    else:
        return make_response({"error": "El servicio de trampas aun no ha sido iniciado"}, 200)

@app.get("/api/monitor/graph")
def get_packets_graph():
    
    if not os.path.isfile("monitor.log"):
        return make_response({"error": "Aun no se tiene informacion de la interfaz"}, 200)

    full_packets = []
    # Leer el archivo de datos
    with open("monitor.log", "r") as m:
        full_packets = [int(x) if x != "None\n" else None for x in m.readlines()]

    # Intervalo de tiempo
    time_interval = []
    count = 0
    for _ in range(0, len(full_packets)):
        time_interval.append(count)
        count += 5

    # Rellenar la grafica

    line_chart = pygal.Line(fill=True, show_x_guides = False, show_y_guides = True)
    line_chart.title = "Total de paquetes recibidos en la interfaz FastEthernet2/0"
    line_chart.x_labels = time_interval
    line_chart.add("Fa2/0", full_packets)

    # Guardar la grafica

    line_chart.render_to_file("images/graph.svg")

    # Regresar el archivo de imagen

    return send_file("images/graph.svg", mimetype="image/svg+xml")



if __name__ == "__main__":
    app.run("0.0.0.0", 8000, True)
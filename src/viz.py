#!/usr/bin/env python
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.embed import components
import numpy as np
import sys
import itertools
sys.path.insert(0, 'modules/czml/czml')
import czml
from projectile import Projectile


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def hello():
    temp = render_template('viz.html',
                           div=div, script=script,
                           div2=div2, script2=script2)
    return temp

@socketio.on('connect')
def handle_connect():
    emit('loadData', doc.dumps())

if __name__ == '__main__':

    doc = czml.CZML()
    packet1 = czml.CZMLPacket(id='document', version='1.0')
    doc.packets.append(packet1)

    clock_packet = czml.CZMLPacket(id="document",
                                   name="CZML Path",
                                   version = "1.0",
                                   clock={"interval": "2000-01-01T11:58:55Z/2000-01-01T23:58:55Z",
                                          "currentTime:":"2000-01-01T11:58:55Z",
                                          "multiplier": 5})


    glider_packet = czml.CZMLPacket(id="path",
                                    name="path with GPS flight data",
                                    availability="2000-01-01T11:58:55Z/2000-01-01T23:58:55Z")

    # building the path packet that goes in glider
    color_pack = czml.Color(rgba=[255, 0, 255, 255])
    outlineColor_pack = czml.Color(rgba=[0, 255, 255, 255])
    polylineGlow_pack = czml.PolylineGlow(color=czml.Color(rgba=[255, 255, 0,  255]),
                                          glowPower=3)
    polylineOutline_pack = czml.PolylineOutline(color=color_pack,
                                                outlineColor=outlineColor_pack,
                                                outlineWidth=5,
                                                polylineGlow=polylineGlow_pack,
                                                )
    material_pack = czml.Material(polylineOutline=polylineOutline_pack)
    path_pack = czml.Path(material=material_pack, width=8, leadTime=0, trailTime=10000000,
                          resolution=5)
    glider_packet.path = path_pack

    position_pack = czml.Position(epoch="2000-01-01T11:58:55Z")

    p = Projectile(4000, 45)
    tof = np.ceil(p.timeOfFlight())
    time = np.arange(0, tof, 0.1)
    x, y = p.pos(time)
    y = (20925646.3255*.3048) + y
    z = np.zeros(time.size)

    vx, vy = p.vel(time)

    pos = zip(time, x, y, z)

    position_pack.cartesian = list(itertools.chain.from_iterable(pos))

    glider_packet.position = position_pack

    doc.append(clock_packet)
    doc.append(glider_packet)

    displacement = list(map(np.linalg.norm, zip(x, y, z)))

    plot = figure(title="Displacement vs Time", plot_width=600, plot_height=400)
    plot.line(time, displacement)
    plot.xaxis.axis_label = 'Time'
    plot.yaxis.axis_label = 'Displacement'
    script, div = components(plot)

    speed = list(map(np.linalg.norm, zip(vx, vy, z)))

    plot2 = figure(title="Speed vs Time", plot_width=600, plot_height=400)
    plot2.line(time, speed)
    plot2.xaxis.axis_label = 'Time'
    plot2.yaxis.axis_label = 'Speed'
    script2, div2 = components(plot2)

    socketio.run(app, port=8081, debug=True)

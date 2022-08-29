from arena import *
import random
import math

scene = Scene(host="mqtt.arenaxr.org", scene="example")

user_holding = {}

evt = Event()

def q_mult(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
    z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
    return w, x, y, z

def q_conjugate(q):
    w, x, y, z = q
    return (w, -x, -y, -z)

def qv_mult(q1, v1):
    q2 = (0.0,) + v1
    return q_mult(q_mult(q1, q2), q_conjugate(q1))[1:]

def clickbox(scene, evt, msg):
    usr = msg['data']['source']
    box = scene.get_persisted_obj(object_id="box")
    if evt.type == "mousedown":
        box.update_attributes(material=Material(transparent=True, opacity=0.5))
        scene.update_object(box)
        user_holding[usr] = box.object_id
    elif evt.type == "mouseup":
        box.update_attributes(material=Material(transparent=False, opacity=1))
        scene.update_object(box)
        user_holding.pop(usr)

@scene.run_once
def make_box():
    box = Box(
        object_id="box",
        position=(0, 1, 0),
        clickable=True,
        evt_handler=clickbox,
        material=Material(transparent=False, opacity=1),
        persist=True
    )
    scene.add_object(box)

@scene.run_forever(interval_ms=20)
def update():
    for usr in user_holding.keys():
        cam = scene.get_persisted_obj(usr)
        cposition = cam['data']['position']
        crotation = cam['data']['rotation']
        quaternion = (crotation['w'], crotation['x'], crotation['y'], crotation['z'])

        v2 = qv_mult(quaternion, (1,0,0))
        holding_posX = cposition['x']+3*v2[2]
        holding_posY = 1
        holding_posZ = cposition['z']-3*v2[0]

        box = scene.get_persisted_obj(user_holding[usr])

        box.update_attributes(position=(holding_posX, holding_posY, holding_posZ))
        scene.update_object(box)


scene.run_tasks()
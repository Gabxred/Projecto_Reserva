from flask import Flask, request, jsonify, redirect, url_for, g, render_template

import os
import sqlite3
from datetime import date,time, datetime
from flask_sqlalchemy import SQLAlchemy
from modelo import usuario
from modelo import reservas
from modelo import salas
BASE_DIR =  os.path.abspath(os.path.dirname(__file__))
DB_URI = "sqlite:///" + os.path.join(BASE_DIR, "reservasDB.db")

app = Flask(__name__, template_folder="front")

#app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True


db = SQLAlchemy(app)


#index el inicio de todo
@app.route('/' )
def index():
   
    
    return render_template("index.html", usuario="eje", usuario2="")

@app.route('/registroU')
def prueba():
    return render_template("registroCliente.html")

@app.route('/saveU',  methods=["POST"])
def nuevUs():
    nombre=request.form.get("user_name")
    apellido=request.form.get("user_apellido")
    ci=request.form.get("ci")
    correo=request.form.get("user_email")
    direccion=request.form.get("direccion")
    numero=request.form.get("numero")
    nuevo=usuario(nombre=nombre,apellido=apellido,ci=ci,correo=correo,direccion=direccion,numero=numero)
    db.session.add(nuevo)
    db.session.commit()
    return render_template("listadeclientes.html")

def actualizar(id):
    obj=usuario.query.get(int(id))
    obj.nombre="hola"
    db.session.commit()


def borrado_usuario(ci):
    idusuario=usuario.query.filter_by(ci=ci).first()
    db.session.query(reservas).filter(reservas.cod_usuario==idusuario.cod_usuario).delete()
    db.session.query(usuario).filter(usuario.ci== ci).delete()
    db.session.commit()
    return 0

''' 
    borrado
    db.session.query(usuario).filter(usuario.ci==5412384).delete()
    db.session.commit()
'''

''' 
    Update funcional
    usuar = db.session.query(usuario).get(2)
    usuar.apellido="RAMON"
    db.session.commit()    
'''

'''
    Agregar reserva
    time = datetime.now().strftime("%m/%d/%Y")
    dt=datetime.now().strftime("%H:%M:%S")
    dt2=datetime.now().strftime("%H:%M:%S")
    #nuevo= reserva(cod_sala=1,cod_usuario=1,fecha=date.fromisoformat('2019-12-04'),horario_inicio=time(hour=12,minute=56).isoformat(timespec='minutes'),horario_fin=time(hour=12,minute=56).isoformat(timespec='minutes') )
    nuevo= reservas(cod_usuario=1,cod_sala=1,fecha=time,horario_inicio=dt,horario_fin=dt2) ##
'''
app.run()
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
db.configure_mappers()

#index el inicio de todo
@app.route('/' )
def index():
   
    
    return render_template("index.html")
#rutaregistrocliente
@app.route('/registroU')
def prueba():
    return render_template("registroCliente.html")

#Guardado Cliente nuevo
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
    return redirect(url_for('listC'))


#listado de clientes
@app.route('/listC', methods=["GET"])
def listC():
    obj=db.session.query(usuario).all()
    
    return render_template("listadeclientes.html",datos= obj)

#actualizacion de Datos  Clientte
@app.route("/upd<int:id>", methods=["GET","POST"])
def actualizar(id):
    if  request.method =="GET":
        obj=db.session.query(usuario).filter_by(ci=id).first()
        return render_template("editarCliente.html", nombre=obj.nombre, apellido=obj.apellido,
         ci=obj.ci, dirreccion=obj.direccion, numero=obj.numero, correo=obj.correo)
    
    if  request.method =="POST":
        
        obj=db.session.query(usuario).filter_by(ci=id).first()
        obj.nombre=request.form.get("user_name") 
        obj.apellido=request.form.get("user_apellido")   
        obj.ci=request.form.get("ci")
        obj.correo=request.form.get("user_email")    
        obj.direccion=request.form.get("direccion")    
        obj.numero=request.form.get("numero")
        db.session.commit()
        return redirect(url_for('listC'))

#elimminado de cliente
@app.route("/elim<int:ci>")
def borrado_usuario(ci):
    idusuario=usuario.query.filter_by(ci=ci).first()
    db.session.query(reservas).filter(reservas.cod_usuario==idusuario.cod_usuario).delete()
    db.session.query(usuario).filter(usuario.ci== ci).delete()
    db.session.commit()
    return redirect(url_for('listC'))

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
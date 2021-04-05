from flask import Flask, request, jsonify, redirect, url_for, g, render_template, flash,jsonify
from flask_marshmallow import Marshmallow
import json
import os
import requests
import sqlite3
from datetime import date,time, datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from modelo import usuario
from modelo import reservas
from modelo import salas
from modelo import usuarioSchema 
from modelo import reservaSchema
from modelo import salaSchema
from modelo import usuarioReservaSchema
from marshmallow_sqlalchemy import SQLAlchemySchema
BASE_DIR =  os.path.abspath(os.path.dirname(__file__))
DB_URI = "sqlite:///" + os.path.join(BASE_DIR, "reservasDB.db")

app = Flask(__name__, template_folder="front")
app.secret_key = "abc"
#app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["DEBUG"]=True

db = SQLAlchemy(app)
db.configure_mappers()


#index del login
@app.route('/' )
def index():
   
    usuariosession.correo=""
    usuariosession.nivel=0
    return render_template("login.html")


class usuariosession:
    nivel=None
    correo=None
    def __init__(nivel,correo):
        self.nivel
        self.correo

#lista de reserva Cliente
@app.route("/listR")
def listR():
    #usuar = usuario.query.filter(usuario.correo==usuariosession.correo).first()
    #idusuar=usuar.cod_usuario
    
    if usuariosession.nivel==0:
        url = "http://localhost:5000/api/usuario/"+usuariosession.correo
        response = requests.get(url)
        response_json1 = json.loads(response.text)
        idusuar=response_json1
        #reserv=db.session.query(reservas).filter(reservas.cod_usuario==idusuar).all()
        url = "http://localhost:5000/api/usuarioreservas"+str(idusuar)
        response = requests.get(url)
        response_json = json.loads(response.text)
        return render_template("listadereservacliente.html", nivel=usuariosession.nivel, datos=response_json)
    else:
        #reserv2=db.session.query(reservas, usuario).filter(reservas.cod_usuario==usuario.cod_usuario).order_by(reservas.fecha).all()
        url = "http://localhost:5000/api/usuarioreservas"
        response = requests.get(url)
        response_json = json.loads(response.text)
        return render_template("listadereservacliente.html", nivel=usuariosession.nivel,  datos2=response_json)


        

#reservacliente
@app.route("/reserv", methods=["POST","GET"])
def reserv():
    url = "http://localhost:5000/api/salas"
    response = requests.get(url)
    listsa = json.loads(response.text)
    url = "http://localhost:5000/api/usuarios"
    response = requests.get(url)
    usuar = json.loads(response.text)
    #listsa=salas.query.order_by(salas.cod_sala)
    #usuar=usuario.query.order_by(usuario.nombre)
    if request.method=="GET":
       
        return render_template("reservar.html",salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)
    
    if request.method=="POST":
        if usuariosession.nivel==1:
            idusuar = request.form.get("selUser")
            sala=request.form.get("salaid")
            horaini=request.form.get("horaini")
            horafin=request.form.get("horafin")
            fecha=request.form.get("fecha")
            fechahoy = datetime.now()
            if horaini<horafin and fecha >= str(fechahoy.date()):
               if validarreserva(horaini, horafin, fecha,sala)==True:
                   '''nuevo=reservas(cod_usuario=usuar,cod_sala=sala,horario_inicio=horaini,horario_fin=horafin,fecha=fecha)
                   db.session.add(nuevo)
                   db.session.commit()'''
                   url = "http://localhost:5000/api/aggreserva"
                   sav = requests.post(url,json={'cod_usuario':idusuar,'cod_sala':sala,'horario_inicio':horaini,'horario_fin':horafin,'fecha':fecha})
                   flash("Rerserva Realizada")
                   return redirect(url_for('listR'))
               else:
                    flash("Ese horario de reserva esta ocupado")
                    return render_template("reservar.html", fecha=fecha, horaini=horaini,horafin=horafin,salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)    
            else:
                #aca
                flash("La hora final debe ser mayor que la hora de inicio y la fecha debe ser actual o posterior")
                return render_template("reservar.html", fecha=fecha, horaini=horaini,horafin=horafin,salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)
        else:
            '''usuar = usuario.query.filter(usuario.correo==usuariosession.correo).first()
            idusuar=usuar.cod_usuario'''
            url = "http://localhost:5000/api/usuario/"+usuariosession.correo
            response=requests.get(url)
            idusuar = json.loads(response.text)
            sala=request.form.get("salaid")
            horaini=request.form.get("horaini")
            horafin=request.form.get("horafin")
            fecha=request.form.get("fecha")
            fechahoy = datetime.now()
            if horaini<horafin and fecha >= str(fechahoy.date()):

               if validarreserva(horaini, horafin, fecha,sala)==True:
                   url = "http://localhost:5000/api/aggreserva"
                   sav = requests.post(url,json={'cod_usuario':idusuar,'cod_sala':sala,'horario_inicio':horaini,'horario_fin':horafin,'fecha':fecha})
                   '''nuevo=reservas(cod_usuario=idusuar,cod_sala=sala,horario_inicio=horaini,horario_fin=horafin,fecha=fecha)
                   db.session.add(nuevo)
                   db.session.commit()'''
                   flash("Rerserva Realizada")
                   return redirect(url_for('listR'))
               else:
                    flash("Ese horario de reserva esta reservado")
                    return render_template("reservar.html", fecha=fecha, horaini=horaini,horafin=horafin,salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)    
            else:
                
                flash("La hora final debe ser mayor que la hora de inicio")
                return render_template("reservar.html", fecha=fecha, horaini=horaini,horafin=horafin,salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)

#para validar reservas
def validarreserva(horaini,horafin,fechA,sala):
    #reserv=reservas.query.filter(reservas.fecha==fechA ,reservas.cod_sala==sala)
    url = "http://localhost:5000/api/validarReserv"
    response = requests.get(url, json={'fecha':fechA,'sala':sala})
    reserv = json.loads(response.text)
    b=None
    HI=int(horaini.replace(":",""))
    HF=int(horafin.replace(":",""))

    if len(reserv)!=0:

        for j in reserv: 

            if int(j["horario_inicio"].replace(":",""))<=HF  and int(j["horario_fin"].replace(":",""))>=HI:
                b=False
                return b
         
        return True
    else:
        
        return True

def validarreservaEdit(horaini,horafin,fechA,sala,idreserva):
    #reserv=reservas.query.filter(and_(reservas.fecha==fechA ,reservas.cod_sala==sala,reservas.cod_reserva!=idreserva))
    url = "http://localhost:5000/api/validarReservedit"
    response = requests.get(url, json={'fecha':fechA,'sala':sala,'reserv':idreserva})
    reserv = json.loads(response.text)
    b=None
    HI=int(horaini.replace(":",""))
    HF=int(horafin.replace(":",""))
    if len(reserv)!=0:

        for j in reserv: 

            if int(j["horario_inicio"].replace(":",""))<=HF  and int(j["horario_fin"].replace(":",""))>= HI:
                b=False
                return b
         
        return True
    else:
        
        return True

#editar reserva
@app.route("/editR<int:id>", methods=["GET","POST"])
def editR(id):
    #listsa=salas.query.order_by(salas.cod_sala)
    url = "http://localhost:5000/api/salas"
    response = requests.get(url)
    listsa = json.loads(response.text)
    
    if request.method=="GET":
        if usuariosession.nivel==1:
            url = "http://localhost:5000/api/reserva"+str(id)
            response = requests.get(url)
            reserv = json.loads(response.text)
            idusuar=reserv["cod_usuario"]
            
            url = "http://localhost:5000/api/usuarioid"+str(idusuar)
            response = requests.get(url)
            usuar = json.loads(response.text)
            salaid=reserv["cod_sala"]


            horaini=reserv["horario_inicio"]
            horafin=reserv["horario_fin"]
            fechas=reserv["fecha"]

            return render_template("reservaedit.html", fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
             nivel=usuariosession.nivel, nombre_usuario=usuar["nombre"]+" "+usuar["apellido"],
             idcliente=usuar["cod_usuario"], salaid=salaid,
             idreserv=id
            ) 

        else:
            url = "http://localhost:5000/api/usuario/"+usuariosession.correo
            response = requests.get(url)
            idusuar = json.loads(response.text)

            ''' usuar = usuario.query.filter(usuario.correo==usuariosession.correo).first()
            idusuar=usuar.cod_usuario'''
            '''reserv=reservas.query.get(id)'''
            url = "http://localhost:5000/api/reserva"+str(id)
            response = requests.get(url)
            reserv = json.loads(response.text)
            horaini=reserv["horario_inicio"]
            horafin=reserv["horario_fin"]
            fechas=reserv["fecha"]
            salaid=reserv["cod_sala"]

            return render_template("reservaedit.html", fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
             nivel=usuariosession.nivel, salaid=salaid,idcliente=idusuar,
             idreserv=id   )

    if request.method=="POST":
       
        if usuariosession.nivel==1:
            usuar = request.form.get("idusuario")
            url = "http://localhost:5000/api/usuarioid"+str(usuar)
            response = requests.get(url)
            usuari = json.loads(response.text)
            sala=request.form.get("salaid")
            horaini=request.form.get("horaini")
            horafin=request.form.get("horafin")
            fechas=request.form.get("fecha")
            fechahoy = datetime.now()
            if horaini<horafin and fechas >= str(fechahoy.date()):

               if validarreservaEdit(horaini, horafin, fechas,sala,id)==True:
                   url = "http://localhost:5000/api/editreserva"+str(id)
                   response = requests.put(url,json={"idusuario":usuar,"salaid":sala,
                   'horaini':horaini,'horafin':horafin,'fecha':fechas})
                   flash("Actualizado")
                   return redirect(url_for('listR'))
               else:   
                    flash("Ese horario esta reservado")
                    return render_template("reservaedit.html",fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
                    nivel=usuariosession.nivel, nombre_usuario=usuari['nombre']+" "+usuari['apellido'],
                    idcliente=usuar, salaid=sala,   idreserv=id)
            else:
                flash("La hora final debe ser mayor que la hora de inicio")
                return render_template("reservaedit.html",fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
                    nivel=usuariosession.nivel, nombre_usuario=usuari['nombre']+" "+usuari['apellido'],
                    idcliente=usuar, salaid=sala, idreserv=id)
        else:
            url = "http://localhost:5000/api/usuario/"+usuariosession.correo
            response = requests.get(url)
            usuarid = json.loads(response.text)
            sala=request.form.get("salaid")
            horaini=request.form.get("horaini")
            horafin=request.form.get("horafin")
            fechas=request.form.get("fecha")
            fechahoy = datetime.now()
            if horaini<horafin and fechas >= str(fechahoy.date()):

               if validarreservaEdit(horaini, horafin, fechas,sala,id)==True:
                   url = "http://localhost:5000/api/editreserva"+str(id)
                   response = requests.put(url,json={"idusuario":usuarid,"salaid":sala,
                   'horaini':horaini,'horafin':horafin,'fecha':fechas})
                   flash("Actualizado")
                   return redirect(url_for('listR'))
               else:
                    flash("Ese horario esta reservado")
                    return render_template("reservaedit.html",fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
                    nivel=usuariosession.nivel,   salaid=sala,     idreserv=id )
                
            else:
                #aca revisar
                
                flash("La hora final debe ser mayor que la hora de inicio")
                return render_template("reservaedit.html",fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
                    nivel=usuariosession.nivel,   salaid=sala,     idreserv=id )

#eliminarReserva
@app.route("/elimR/<int:id>", methods=["POST"])
def elimR(id):
    url = "http://localhost:5000/api/eliminarReserva/"+str(id)
    response = requests.delete(url)
    flash("Sala eliminada")
    return redirect(url_for('listR'))
    


#rutaregistrocliente
@app.route('/registroU')
def registroU():
    return render_template("registroCliente.html", nivel=usuariosession.nivel)

#Guardado Cliente nuevo
@app.route('/saveU',  methods=["POST"])
def nuevUs():
    nombre=request.form.get("user_name")
    apellido=request.form.get("user_apellido")
    ci=request.form.get("ci")
    correo=request.form.get("user_email")
    direccion=request.form.get("direccion")
    numero=request.form.get("numero")
    contra=request.form.get("contra")
    contra2=request.form.get("contra2")
    #usuar = usuario.query.filter ( (usuario.correo==correo) | (usuario.ci==ci)).first()
    url = "http://localhost:5000/api/loginver"
    response = requests.post(url, json={"correo": correo,"ci": ci})
    response_json = json.loads(response.text)
    if len(response_json)!=0:
        flash("Error: Usuario Registrado")
        return render_template("registroCliente.html", nivel=usuariosession.nivel,nombre=nombre,apellido=apellido,
        ci=ci, correo=correo,direccion=direccion,numero=numero,contra=contra)       
    else:
        if contra==contra2:
            '''nuevo=usuario(nombre=nombre,apellido=apellido,ci=ci,correo=correo,direccion=direccion,numero=numero)
            db.session.add(nuevo)
            db.session.commit()'''
            url = "http://localhost:5000/api/nuevoclient"
            response = requests.post(url, json={"correo": correo,"contra":contra,
            "ci":ci,"nombre":nombre,"apellido":apellido,"direccion":direccion,
            "numero":numero,"nivel":0})
            flash("Guardado")
            return redirect(url_for('listC'))
        else:
            flash("Error: Contrasena deben ser iguales")
            return render_template("registroCliente.html", nivel=usuariosession.nivel,nombre=nombre,apellido=apellido,
            ci=ci, correo=correo,direccion=direccion,numero=numero,contra=contra)


#listado de clientes
@app.route('/listC', methods=["GET"])
def listC():
    #obj=db.session.query(usuario).order_by(usuario.nombre).all()
    url = "http://localhost:5000/api/usuarios"
    response = requests.get(url)
    response_json = json.loads(response.text)
    return render_template("listadeclientes.html",datos= response_json,nivel=usuariosession.nivel)

#actualizacion de Datos  Cliente
@app.route("/upd<int:id>", methods=["GET","POST"])
def actualizar(id):
    if  request.method =="GET":
       
        #obj=db.session.query(usuario).filter_by(ci=id).first()
        url="http://localhost:5000/api/usuarioedit/"+str(id)
        response = requests.get(url)
        response_json = json.loads(response.text)
        #nombre=response_json[0]["nombre"]
        return render_template("editarCliente.html", nombre=response_json[0]["nombre"], apellido=response_json[0]["apellido"],
         ci=response_json[0]["ci"], direccion=response_json[0]["direccion"], numero=response_json[0]["numero"], correo=response_json[0]["correo"], contra=response_json[0]["contrasena"],
          nivelc=response_json[0]["nivel"],cod_usuario=response_json[0]["cod_usuario"], nivel=usuariosession.nivel)
        
    
    if request.method=="POST":
        
        nombre=request.form.get("user_name") 
        apellido=request.form.get("user_apellido")   
        ci=request.form.get("ci")
        correo=request.form.get("user_email")    
        direccion=request.form.get("direccion")    
        numero=request.form.get("numero")
        contrasena=request.form.get("contra")
        contra2=request.form.get("contra2")
        nivel=request.form.get("nivel")
        if contra2==contrasena:
            url = "http://localhost:5000/api/usuarioedit"+str(id)
            response = requests.put(url, json={"correo": correo,"contra":contrasena,
            "ci":ci,"nombre":nombre,"apellido":apellido,"direccion":direccion,
            "numero":numero,"nivel":nivel})
            #db.session.commit()
            flash("Actualizado")
            return redirect(url_for('listC'))
        else:
            flash("Las contrasenas deben coincidir")
            return render_template("editarCliente.html", nombre=nombre, apellido=apellido,
            ci=ci, direccion=direccion, numero=numero, correo=correo, contra=contrasena,
            nivelc=nivel,nivel=usuariosession.nivel,cod_usuario=id)     

        

#eliminar de cliente
@app.route("/elimC/<int:id>", methods=["POST"])
def borrado_usuario(id):
    url = "http://localhost:5000/api/eliminarusuario/"+str(id)
    response = requests.delete(url)
    return redirect(url_for('listC'))

#inicio logeado
@app.route ("/inicio<int:lvl>", methods=["GET"])
def inicio(lvl):
    now = datetime.now()
    inicio=now.hour
    
    reserv=reservas.query.all()
    
    return render_template("index.html", nivel=lvl, todo=reserv )


#listado Salas
@app.route("/listS")
def listS():
    #listas=salas.query.order_by(salas.cod_sala).all()
    url = "http://localhost:5000/api/salas"
    response = requests.get(url)
    response_json = json.loads(response.text)
    return render_template("listadesalas.html",datos=response_json,nivel=usuariosession.nivel)

#agregar Sala nueva
@app.route("/nuevaS", methods=["POST"])
def nuevaS():
    if request.method=="POST":
        url = "http://localhost:5000/api/salaAgg"
        capacidad=request.form.get("capacidadN")
        response = requests.post(url, json={'capacidad':capacidad})
        flash("Creada correctamente")
        return redirect(url_for('listS'))
 
#editar_sala
@app.route("/editS<int:id>", methods=["POST","GET"])
def editS(id):
    if request.method=="POST":
        
        '''sala=db.session.query(salas).filter_by(cod_sala=id).first()
        sala.capacidad=request.form.get("capacidad") 
        db.session.commit()'''
        url = "http://localhost:5000/api/salaedit"+str(id)
        capacidad=request.form.get("capacidad")
        response = requests.put(url, json={'capacidad':capacidad})
        flash("Sala Actualizada")
        return redirect(url_for('listS'))       

#eliminarSala
@app.route("/elimS<int:id>", methods=["POST"])
def elimS(id):
   
    '''db.session.query(reservas).filter(reservas.cod_sala==id).delete()
    db.session.query(salas).filter(salas.cod_sala==id).delete()
    db.session.commit()'''

    url = "http://localhost:5000/api/eliminarSala/"+str(id)
    response = requests.delete(url)
    flash("Sala eliminada")
    return redirect(url_for('listS'))  



#login
@app.route("/log<int:val>", methods=[ "POST"])
def login(val):
    #logeo usuario registrado
    if  val==0:
        correo=request.form.get("correo") 
        passw=request.form.get("contrasena") 
        #usuar = usuario.query.filter_by(correo=correo).first()
        url = "http://localhost:5000/api/login"
        response = requests.post(url, json= {"correo": correo,"contrasena":passw})
        #if usuar:
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if (len(response_json)==0):
                return render_template("login.html", mensaje="Error de credenciales", contrasena=passw, correo=correo ) 
            else:
                usuariosession.correo=correo
                usuariosession.nivel=response_json[0]["nivel"]
                return redirect(url_for('inicio',lvl= usuariosession.nivel))     
        else:
            return render_template("login.html", mensaje="Error de credenciales: Usuario no registrado", contrasena=passw, correo=correo)
            
        
    #creacion y verificacion de usuario nuevo
    if  val==1:
        correo=request.form.get("correon") 
        passw=request.form.get("contran")
        passw2=request.form.get("contran2")
        ci=request.form.get("ci")
        nombre=request.form.get("nombre")
        apellido=request.form.get("apellido")
        direccion=request.form.get("direccion")
        numero=request.form.get("numero")
        #usuar = usuario.query.filter ( (usuario.correo==correo) | (usuario.ci==ci)).first()

        url = "http://localhost:5000/api/loginver"
        response = requests.post(url, json={"correo": correo,"ci": ci})
        response_json = json.loads(response.text)
        if (len(response_json)!=0):
            return render_template("login.html", mensaje2="Error de credenciales: El usuario ya ha sido registrado", 
            correon=correo, contran=passw, nombre=nombre,apellido=apellido, direccion=direccion, numero=numero, ci=ci
            )
        else:
            if passw==passw2:
                usuariosession.nivel=0
                usuariosession.correo=correo
                #nuevo=usuario(nombre=nombre,apellido=apellido,ci=ci,correo=correo,contrasena=passw,direccion=direccion,numero=numero, nivel=usuariosession.nivel)
                #db.session.add(nuevo)
                #db.session.commit()       
                url = "http://localhost:5000/api/nuevoclient"
                response = requests.post(url, json={"correo": correo,"contra":passw,
                "ci":ci,"nombre":nombre,"apellido":apellido,"direccion":direccion,
                "numero":numero,"nivel":usuariosession.nivel})
                return redirect(url_for('inicio',lvl=usuariosession.nivel))
            else:
                return render_template("login.html", mensaje2="Las contraseñas deben ser iguales", 
                correon=correo, contran=passw, nombre=nombre,apellido=apellido, direccion=direccion, numero=numero, ci=ci,
               )

esquemaUsuario=usuarioSchema()
esquemasUsuarios=usuarioSchema(many=True)

esquemaReserva=reservaSchema()
esquemasReserva=reservaSchema(many=True)

esquemaSala=salaSchema()
esquemasSalas=salaSchema(many=True)

esquemareservauser=usuarioReservaSchema()
esquemasreservausers=usuarioReservaSchema(many=True)

#COMIENZO API
@app.route("/api/usuarios", methods = ["GET"])
def api_usuarios():
   
    data=usuario.query.order_by(usuario.nombre).all()
    result=esquemasUsuarios.dump(data)
    return jsonify(result)


@app.route("/api/salas", methods = ["GET"])
def api_salas():
   
    data=salas.query.order_by(salas.cod_sala).all()
    result=esquemasSalas.dump(data)
    return jsonify(result)


@app.route("/api/reservas", methods = ["GET"])
def api_reservas():
   
    data=reservas.query.order_by(reservas.fecha).all()
    result=esquemasReserva.dump(data)
    return jsonify(result)

@app.route("/api/usuarioreservas", methods = ["GET"])
def api_usuarioreserva():
    data=db.session.query(usuario.nombre,usuario.apellido, reservas.cod_reserva,reservas.cod_sala,reservas.fecha,reservas.horario_fin,reservas.horario_inicio).filter(reservas.cod_usuario==usuario.cod_usuario).order_by(reservas.fecha).all()
    result=esquemasreservausers.dump(data)
    return jsonify(result)

@app.route("/api/usuarioreservas<int:id>", methods = ["GET"])
def api_usuarioreservac(id):
   
    data=db.session.query(reservas).filter(reservas.cod_usuario==id).order_by(reservas.fecha).all()
    result=esquemasreservausers.dump(data)
    return jsonify(result)


@app.route("/api/login", methods=["POST"])
def api_login():
  
    correo = request.get_json()['correo']
    contrasena = request.get_json()['contrasena']
    usuar = usuario.query.filter(usuario.correo==correo, usuario.contrasena==contrasena)
    result=esquemasUsuarios.dump(usuar)
    return jsonify(result)

#para validar usurio nuevo
@app.route("/api/loginver", methods=["POST"])
def api_loginver():
    correo = request.get_json()['correo']
    ci = request.get_json()['ci']
    usuar = db.session.query(usuario).filter(or_(usuario.correo==correo, usuario.ci==ci))
    result=esquemasUsuarios.dump(usuar)
    return jsonify(result)

#para agregar usuario api
@app.route("/api/nuevoclient", methods=["POST"])
def api_nuevoclient():
    correo = request.get_json()['correo']
    ci = request.get_json()['ci']
    contra=request.get_json()["contra"]
    nombre=request.get_json()["nombre"]
    apellido=request.get_json()["apellido"]
    direccion=request.get_json()["direccion"]
    numero=request.get_json()["numero"]
    nivel=request.get_json()["nivel"]
    nuevo=usuario(nombre=nombre,apellido=apellido,ci=ci,correo=correo,contrasena=contra,direccion=direccion,numero=numero, nivel=usuariosession.nivel)
    db.session.add(nuevo)
    db.session.commit()
    return "si"

@app.route("/api/usuario/<string:correo>", methods=["GET"])
def api_userid(correo):
    usuar = usuario.query.filter (usuario.correo==correo)
    result=esquemasUsuarios.dump(usuar)
    if  (len(result)==0):
        return "no hay"
    else:
        return jsonify(result[0]["cod_usuario"])


@app.route("/api/eliminarSala/<int:id>", methods=["DELETE"])
def api_eliminarSala(id):
    try:
        db.session.query(reservas).filter(reservas.cod_sala==id).delete()
        db.session.query(salas).filter(salas.cod_sala==id).delete()
        db.session.commit()
        return redirect(url_for('listS'))

    except:
        return jsonify("error")


@app.route("/api/eliminarReserva/<int:id>", methods=["DELETE"])
def api_eliminarRerserva(id):
    try:
        db.session.query(reservas).filter(reservas.cod_reserva==id).delete()
        db.session.commit()
        return redirect(url_for('listR'))

    except:
        return jsonify("error")

@app.route("/api/eliminarusuario/<int:id>", methods=["DELETE"])
def api_eliminarUsuario(id):
    try:
        db.session.query(reservas).filter(reservas.cod_usuario==id).delete()
        db.session.query(usuario).filter(usuario.cod_usuario==id).delete()
        db.session.commit()
        return redirect(url_for('listC'))
    except:
        return jsonify("error")

@app.route("/api/usuarioedit/<int:id>", methods=["GET"])
def api_editUserget(id):
    try:
        obj=db.session.query(usuario).filter(usuario.cod_usuario==id)
        result=esquemasUsuarios.dump(obj)
        return jsonify(result)
    except:
        return jsonify("error")


@app.route("/api/usuarioedit<int:id>", methods=["PUT"])
def api_editUS(id):
    try:
        obj=db.session.query(usuario).get(id)
        obj.correo=request.get_json()['correo']
        obj.ci=request.get_json()['ci']
        obj.nombre=request.get_json()["nombre"]
        obj.apellido=request.get_json()["apellido"]
        obj.contrasena=request.get_json()["contra"]
        obj.direccion=request.get_json()["direccion"]
        obj.numero=request.get_json()["numero"]
        obj.nivel=request.get_json()["nivel"]
        db.session.commit()
        return "Actualizado"
    except:
        return jsonify("error")



@app.route("/api/salaedit/<int:id>", methods=["PUT"])
def api_editSa(id):
    try:
        obj=db.session.query(salas).get(id)
        obj.capacidad=request.get_json()["capacidad"]
        db.session.commit()
        return "Actualizado"
    except:
        return jsonify("error")


@app.route("/api/salaAgg", methods=["POST"])
def api_Aggsala():
    try:
        nueva=salas(capacidad=request.get_json()["capacidad"])
        db.session.add(nueva)
        db.session.commit()
        return "Agregado correctamente"
    except:
        return jsonify("error")

@app.route("/api/validarReserv", methods=["GET"])
def validarReserv():
    try:

        reserv=reservas.query.filter(and_(reservas.fecha==request.get_json()["fecha"] ,reservas.cod_sala==request.get_json()["sala"]))
        result=esquemasReserva.dump(reserv)
        return jsonify(result)
    except:
        return jsonify("error")


@app.route("/api/validarReservedit", methods=["GET"])
def validarReservedit():
    try:

        reserv=reservas.query.filter(and_(reservas.fecha==request.get_json()["fecha"] ,reservas.cod_sala==request.get_json()["sala"],
        reservas.cod_reserva!=request.get_json()["reserv"]))
        result=esquemasReserva.dump(reserv)
        return jsonify(result)
    except:
        return jsonify("error")

@app.route("/api/aggreserva",methods=["POST"])
def api_aggreserva():
    try:
        
        nuevo=reservas(cod_usuario=request.get_json()["cod_usuario"],cod_sala=request.get_json()["cod_sala"],
        horario_inicio=request.get_json()["horario_inicio"],horario_fin=request.get_json()["horario_fin"],fecha=request.get_json()["fecha"])
        db.session.add(nuevo)
        db.session.commit()
        return "Guardado"
    except:
       return jsonify("error")

@app.route("/api/reserva<int:id>", methods = ["GET"])
def api_reservasget(id):
   
    data=reservas.query.get(id)
    result=esquemaReserva.dump(data)
    return jsonify(result)

@app.route("/api/usuarioid<int:id>", methods = ["GET"])
def api_usuarioid(id):
    usuar = usuario.query.get(id)
    result=esquemaUsuario.dump(usuar)
    return jsonify(result)



@app.route("/api/editreserva<int:id>",methods=["PUT"])
def api_aggreserv(id):
    try:
        reserv=db.session.query(reservas).filter_by(cod_reserva=id).first()
        reserv.cod_usuario=request.get_json()["idusuario"]
        reserv.cod_sala=request.get_json()["salaid"]
        reserv.horario_inicio=request.get_json()["horaini"]
        reserv.horario_fin=request.get_json()["horafin"]
        reserv.fecha=request.get_json()["fecha"]
        db.session.commit()
        return "Actualizado"
    except:
        return jsonify("error")

















































app.run()

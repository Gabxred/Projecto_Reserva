from flask import Flask, request, jsonify, redirect, url_for, g, render_template, flash

import os
import sqlite3
from datetime import date,time, datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
from modelo import usuario
from modelo import reservas
from modelo import salas

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
    usuar = usuario.query.filter(usuario.correo==usuariosession.correo).first()
    idusuar=usuar.cod_usuario
    if usuariosession.nivel==0:
        reserv=db.session.query(reservas).filter(reservas.cod_usuario==idusuar).all()
        return render_template("listadereservacliente.html", nivel=usuariosession.nivel, datos=reserv)
    else:
        reserv2=db.session.query(reservas, usuario).filter(reservas.cod_usuario==usuario.cod_usuario).order_by(reservas.fecha).all()
        return render_template("listadereservacliente.html", nivel=usuariosession.nivel,  datos2=reserv2)


        

#reservacliente
@app.route("/reserv", methods=["POST","GET"])
def reserv():
    listsa=salas.query.order_by(salas.cod_sala)
    usuar=usuario.query.order_by(usuario.nombre)
    if request.method=="GET":
       
        return render_template("reservar.html",salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)
    
    if request.method=="POST":
        if usuariosession.nivel==1:
            usuar = request.form.get("selUser")
            sala=request.form.get("salaid")
            horaini=request.form.get("horaini")
            horafin=request.form.get("horafin")
            fecha=request.form.get("fecha")
            if horaini<horafin:

               if validarreserva(horaini, horafin, fecha,sala)==True:
                   nuevo=reservas(cod_usuario=usuar,cod_sala=sala,horario_inicio=horaini,horario_fin=horafin,fecha=fecha)
                   db.session.add(nuevo)
                   db.session.commit()
                   return redirect(url_for('listR'))
               else:
                    flash("Ese horario de reserva esta ocupado")
                    return render_template("reservar.html", fecha=fecha, horaini=horaini,horafin=horafin,salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)
                
            else:
                #aca
                flash("La hora final debe ser mayor que la hora de inicio")
                return render_template("reservar.html", fecha=fecha, horaini=horaini,horafin=horafin,salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)
        else:
            usuar = usuario.query.filter(usuario.correo==usuariosession.correo).first()
            idusuar=usuar.cod_usuario
            sala=request.form.get("salaid")
            horaini=request.form.get("horaini")
            horafin=request.form.get("horafin")
            fecha=request.form.get("fecha")
            if horaini<horafin:

               if validarreserva(horaini, horafin, fecha,sala)==True:
                   nuevo=reservas(cod_usuario=idusuar,cod_sala=sala,horario_inicio=horaini,horario_fin=horafin,fecha=fecha)
                   db.session.add(nuevo)
                   db.session.commit()
                   return redirect(url_for('listR'))
               else:
                    flash("Ese horario de reserva esta reservado")
                    return render_template("reservar.html", fecha=fecha, horaini=horaini,horafin=horafin,salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)    
            else:
                
                flash("La hora final debe ser mayor que la hora de inicio")
                return render_template("reservar.html", fecha=fecha, horaini=horaini,horafin=horafin,salas=listsa, nivel=usuariosession.nivel,usuarios=usuar)

#para validar reservas
def validarreserva(horaini,horafin,fechA,sala):
    reserv=reservas.query.filter(reservas.fecha==fechA ,reservas.cod_sala==sala)
    b=None
    HI=int(horaini.replace(":",""))
    HF=int(horafin.replace(":",""))

    if reserv:

        for j in reserv: 

            if int(j.horario_inicio.replace(":",""))<HF  and int(j.horario_fin.replace(":",""))> HI:
                b=False
                return b
         
        return True
    else:
        
        return True

def validarreservaEdit(horaini,horafin,fechA,sala,idreserva):
    reserv=reservas.query.filter(reservas.fecha==fechA ,reservas.cod_sala==sala,reservas.cod_reserva!=idreserva)
    b=None
    HI=int(horaini.replace(":",""))
    HF=int(horafin.replace(":",""))

    if reserv:

        for j in reserv: 

            if int(j.horario_inicio.replace(":",""))<HF  and int(j.horario_fin.replace(":",""))> HI:
                b=False
                return b
         
        return True
    else:
        
        return True
#editar reserva
@app.route("/editR<int:id>", methods=["GET","POST"])
def editR(id):
    listsa=salas.query.order_by(salas.cod_sala)
    listauser=usuario.query.order_by(usuario.nombre)
    
    if request.method=="GET":
        if usuariosession.nivel==1:
            reserv=reservas.query.get(id)
            usuar = usuario.query.filter(usuario.cod_usuario==reserv.cod_usuario).first()
            horaini=reserv.horario_inicio
            horafin=reserv.horario_fin
            fechas=reserv.fecha

            return render_template("reservaedit.html", fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
             nivel=usuariosession.nivel,usuarios=listauser, nombre_usuario=usuar.nombre+" "+usuar.apellido,
             idcliente=usuar.cod_usuario, salaid=reserv.cod_sala,
             idreserv=id
            ) 

        else:
            usuar = usuario.query.filter(usuario.correo==usuariosession.correo).first()
            idusuar=usuar.cod_usuario
            reserv=reservas.query.get(id)
            horaini=reserv.horario_inicio
            horafin=reserv.horario_fin
            fechas=reserv.fecha
            
            return render_template("reservaedit.html", fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
             nivel=usuariosession.nivel,usuarios=listauser, salaid=reserv.cod_sala,idcliente=usuariosession.nivel,
             idreserv=id
            )

    if request.method=="POST":
        if usuariosession.nivel==1:
            usuar = request.form.get("idusuario")
            sala=request.form.get("salaid")
            horaini=request.form.get("horaini")
            horafin=request.form.get("horafin")
            fecha=request.form.get("fecha")
            if horaini<horafin:

               if validarreservaEdit(horaini, horafin, fecha,sala,id)==True:
                   reserv=db.session.query(reservas).filter_by(cod_reserva=id).first()
                   reserv.cod_usuario=request.form.get("idusuario")
                   reserv.cod_sala=request.form.get("salaid")
                   reserv.horario_inicio=request.form.get("horaini")
                   reserv.horario_fin=request.form.get("horafin")
                   reserv.fecha=request.form.get("fecha")
                   db.session.commit()
                   return redirect(url_for('listR'))
               else:
                    flash("Ese horario de reserva esta ocupado")
                    return render_template("reservaedit.html",fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
                    nivel=usuariosession.nivel,usuarios=listauser, nombre_usuario=usuar.nombre+" "+usuar.apellido,
                    idcliente=usuar.cod_usuario, salaid=reserv.cod_sala,
                    idreserv=id)
            else:
                #aca
                flash("La hora final debe ser mayor que la hora de inicio")
                return render_template("reservaedit.html",fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
                    nivel=usuariosession.nivel,usuarios=listauser, nombre_usuario=usuar.nombre+" "+usuar.apellido,
                    idcliente=usuar.cod_usuario, salaid=reserv.cod_sala, idreserv=id)
        else:
            usuar = usuario.query.filter(usuario.correo==usuariosession.correo).first()
            idusuar=usuar.cod_usuario
            sala=request.form.get("salaid")
            horaini=request.form.get("horaini")
            horafin=request.form.get("horafin")
            fecha=request.form.get("fecha")
            if horaini<horafin:

               if validarreserva(horaini, horafin, fecha,sala)==True:
                   reserv=db.session.query(reservas).filter_by(cod_reserva=id).first()
                   reserv.cod_usuario=usuariosession.nivel
                   reserv.cod_sala=request.form.get("salaid")
                   reserv.horario_inicio=request.form.get("horaini")
                   reserv.horario_fin=request.form.get("horafin")
                   reserv.fecha=request.form.get("fecha")
                   db.session.commit()
               else:
                    flash("Ese horario de reserva esta reservado")
                    return render_template("reservaedit.html",fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
                    nivel=usuariosession.nivel,usuarios=listauser, nombre_usuario=usuar.nombre+" "+usuar.apellido,
                    idcliente=usuar.cod_usuario, salaid=reserv.cod_sala,     idreserv=id )
                
            else:
                #aca revjsar
                
                flash("La hora final debe ser mayor que la hora de inicio")
                return render_template("reservaedit.html",fecha=fechas, horaini=horaini,horafin=horafin,salas=listsa,
                    nivel=usuariosession.nivel,usuarios=listauser, nombre_usuario=usuar.nombre+" "+usuar.apellido,
                    idcliente=usuar.cod_usuario, salaid=reserv.cod_sala,             idreserv=id       )

#eliminar Reserva
@app.route("/elimR/<int:id>")
def elimR(id):
    db.session.query(reservas).filter(reservas.cod_reserva==id).delete()
    db.session.commit()
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
    usuar = usuario.query.filter ( (usuario.correo==correo) | (usuario.ci==ci)).first()
    if usuar:
        flash("Error: Usuario Registrado")
        return redirect(url_for('registroU'))
        
               
    else:
        if contra==contra2:
            nuevo=usuario(nombre=nombre,apellido=apellido,ci=ci,correo=correo,direccion=direccion,numero=numero)
            db.session.add(nuevo)
            db.session.commit()
            return redirect(url_for('listC'))
        else:
            flash("Error: Contrasena deben ser iguales")
            return redirect(url_for('registroU'))


#listado de clientes
@app.route('/listC', methods=["GET"])
def listC():
    obj=db.session.query(usuario).order_by(usuario.nombre).all()
    
    return render_template("listadeclientes.html",datos= obj)

#actualizacion de Datos  Cliente
@app.route("/upd<int:id>", methods=["GET","POST"])
def actualizar(id):
    if  request.method =="GET":
       
        obj=db.session.query(usuario).filter_by(ci=id).first()
        return render_template("editarCliente.html", nombre=obj.nombre, apellido=obj.apellido,
         ci=obj.ci, direccion=obj.direccion, numero=obj.numero, correo=obj.correo, contra=obj.contrasena,
          nivel=obj.nivel)
    
    if request.method=="POST":
        obj=db.session.query(usuario).filter_by(ci=id).first()
        obj.nombre=request.form.get("user_name") 
        obj.apellido=request.form.get("user_apellido")   
        obj.ci=request.form.get("ci")
        obj.correo=request.form.get("user_email")    
        obj.direccion=request.form.get("direccion")    
        obj.numero=request.form.get("numero")
        obj.contrasena=request.form.get("contra")
        contra2=request.form.get("contra2")
        obj.nivel=request.form.get("nivel")
        if contra2==obj.contrasena:
            db.session.commit()
            return redirect(url_for('listC'))
        else:
            flash("Las contrasenas deben coincidir")
            return render_template("editarCliente.html", nombre=obj.nombre, apellido=obj.apellido,
            ci=obj.ci, direccion=obj.direccion, numero=obj.numero, correo=obj.correo, contra=obj.contrasena,
            nivel=obj.nivel)     

        

#eliminado de cliente
@app.route("/elim<int:ci>")
def borrado_usuario(ci):
    idusuario=usuario.query.filter_by(ci=ci).first()
    db.session.query(reservas).filter(reservas.cod_usuario==idusuario.cod_usuario).delete()
    db.session.query(usuario).filter(usuario.ci== ci).delete()
    db.session.commit()
    return redirect(url_for('listC'))

#inicio logeado
@app.route ("/inicio<int:lvl>", methods=["GET"])
def inicio(lvl):
    tuplasala=salas.query.order_by(salas.cod_sala)
    now = datetime.now()
    inicio=now.hour
  
    if inicio>7 and inicio<19:
        tuplahora=inicio       
    else:
        tuplahora=8
    
    hoy=str(now.month)+"/"+str(now.day)+"/"+str(now.year)
    
    reserv=reservas.query.filter(reservas.fecha==hoy).all()
    
    return render_template("index.html", nivel=lvl, salas=tuplasala, hora=tuplahora)


#listado Salas
@app.route("/listS")
def listS():
    listas=salas.query.order_by(salas.cod_sala).all()
    return render_template("listadesalas.html",datos=listas,nivel=usuariosession.nivel)

#agregar Sala nueva
@app.route("/nuevaS", methods=["POST"])
def nuevaS():
    if request.method=="POST":
        nueva=salas(capacidad=request.form.get("capacidadN"))
        db.session.add(nueva)
        db.session.commit()
        flash("Creada correctamente")
        return redirect(url_for('listS'))
 
#editar_sala
@app.route("/editS<int:id>", methods=["POST","GET"])
def editS(id):
    if request.method=="POST":
        
        sala=db.session.query(salas).filter_by(cod_sala=id).first()
        sala.capacidad=request.form.get("capacidad") 
        db.session.commit()
        flash("Sala Actualizada")
        return redirect(url_for('listS'))       

#eliminarSala
@app.route("/elimS<int:id>")
def elimS(id):
   
    db.session.query(reservas).filter(reservas.cod_sala==id).delete()
    db.session.query(salas).filter(salas.cod_sala==id).delete()
    db.session.commit()
    flash("Sala eliminada")
    return redirect(url_for('listS'))  

#login
@app.route("/log<int:val>", methods=[ "POST"])
def login(val):
    #logeo usuario registrado
    if  val==0:
        correo=request.form.get("correo") 
        passw=request.form.get("contrasena") 
        usuar = usuario.query.filter_by(correo=correo).first()
        if usuar:
            if usuar.contrasena==passw:
                usuariosession.correo=correo
                usuariosession.nivel=usuar.nivel
                return redirect(url_for('inicio',lvl= usuariosession.nivel))
            else:
                return render_template("login.html", mensaje="Error de credenciales", contrasena=passw, correo=correo )
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
        usuar = usuario.query.filter ( (usuario.correo==correo) | (usuario.ci==ci)).first()
        usuariosession.nivel=0
        usuariosession.ci=ci
        if usuar:
            return render_template("login.html", mensaje2="Error de credenciales: El usuario ya ha sido registrado", 
            correon=correo, contran=passw, nombre=nombre,apellido=apellido, direccion=direccion, numero=numero, ci=ci
            )
        else:
            if passw==passw2:
                nuevo=usuario(nombre=nombre,apellido=apellido,ci=ci,correo=correo,contrasena=passw,direccion=direccion,numero=numero, nivel=usuariosession.nivel)
                db.session.add(nuevo)
                db.session.commit()
                nuevo=0         
                return redirect(url_for('inicio',lvl=usuariosession.nivel))
            else:
                return render_template("login.html", mensaje2="Las contraseñas deben ser iguales", 
                correon=correo, contran=passw, nombre=nombre,apellido=apellido, direccion=direccion, numero=numero, ci=ci,
               )


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
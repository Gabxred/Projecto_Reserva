from flask import Flask, request, jsonify, redirect, url_for, g, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
db = SQLAlchemy(app)
#usuario

class usuario(db.Model):
    cod_usuario= db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(150))
    apellido=db.Column(db.String(150))
    ci= db.Column(db.Integer)
    numero =db.Column(db.String(150))
    direccion=db.Column(db.String(150))
    correo=db.Column(db.String(150))
    contrasena=db.Column(db.String(150))
    nivel=db.Column(db.Integer)
    reservas = db.relationship('reservas', cascade="all,delete",backref='usuario', )
   
   
    def __repr__(self):
        return '<Codigo %r>' % self.cod_usuario
        
        
   


#reserva
class reservas(db.Model):
    cod_reserva=db.Column(db.Integer, primary_key=True)
    cod_usuario=db.Column(db.Integer, db.ForeignKey('usuario.cod_usuario',ondelete="CASCADE"),nullable=True)
    cod_sala=db.Column(db.Integer, db.ForeignKey('salas.cod_sala',ondelete="CASCADE"),nullable=True)
    fecha=db.Column(db.String(10))
    horario_inicio=db.Column(db.String(10))
    horario_fin=db.Column(db.String(10))
    def __repr__(self):
        return '<Codigo %r>' % self.cod_reserva

#sala
class salas(db.Model):
    cod_sala=db.Column(db.Integer, primary_key=True)
    capacidad=db.Column(db.Integer)
    cod_reserva = db.relationship('reservas', cascade="all,delete",backref='salas')

    

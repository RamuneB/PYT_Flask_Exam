from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed
import app


class RegistracijosForma(FlaskForm):
    vardas = StringField('Vardas', [DataRequired()])
    el_pastas = StringField('El. paštas', [DataRequired()])
    slaptazodis = PasswordField('Slaptažodis', [DataRequired()])
    patvirtintas_slaptazodis = PasswordField("Pakartokite slaptažodį", [EqualTo('slaptazodis', "Slaptažodis turi sutapti.")])
    submit = SubmitField('Prisiregistruoti')


class PrisijungimoForma(FlaskForm):
    el_pastas = StringField('El. paštas', [DataRequired()])
    slaptazodis = PasswordField('Slaptažodis', [DataRequired()])
    prisiminti = BooleanField("Prisiminti mane")
    submit = SubmitField('Prisijungti')


class StraipsnioForma(FlaskForm):
    suma = IntegerField('Suma', [DataRequired()])
    pavadinimas = StringField('Pavadinimas', [DataRequired()])
    tekstas = TextAreaField('Tekstas', [DataRequired()])
    grupe = QuerySelectField(
        query_factory=lambda: app.Grupe.query, 
        get_label="pavadinimas", 
        get_pk=lambda obj: obj.id,
        allow_blank=True)
   
    submit = SubmitField('Išsaugoti')
    


class PaskyrosAtnaujinimoForma(FlaskForm):
    vardas = StringField('Vardas', [DataRequired()])
    el_pastas = StringField('El. paštas', [DataRequired()])
    nuotrauka = FileField('Atnaujinti profilio nuotrauką', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Atnaujinti')

class IncomeForm(FlaskForm):
    suma = IntegerField('Suma', [DataRequired()])
    #siuntejas = StringField('Siuntėjas', [DataRequired(message='Nenurodytas siuntėjas')])
    pavadinimas = StringField('Pavadinimas', [DataRequired()])
    grupe = QuerySelectField(
        query_factory=lambda: app.Grupe.query, 
        get_label="pavadinimas", 
        get_pk=lambda obj: obj.id,
        allow_blank=True)
    papildoma_info = TextAreaField('Papildoma info')
    submit = SubmitField('Išsaugoti')

    def tikrinti_varda(self, vardas):
        if vardas.data != app.current_user.vardas:
            vartotojas = app.Vartotojas.query.filter_by(vardas=vardas.data).first()
            if vartotojas:
                raise ValidationError('Šis vardas panaudotas. Pasirinkite kitą.')

    def tikrinti_pasta(self, el_pastas):
        if el_pastas.data != app.current_user.el_pastas:
            vartotojas = app.Vartotojas.query.filter_by(el_pastas=el_pastas.data).first()
            if vartotojas:
                raise ValidationError('Šis el. pašto adresas panaudotas. Pasirinkite kitą.')

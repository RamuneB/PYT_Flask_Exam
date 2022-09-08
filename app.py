from telnetlib import STATUS
from flask import Flask, render_template, redirect, url_for, request, session, flash, abort
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from forms import IncomeForm
import forms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slaptas_raktas'
csrf = CSRFProtect(app)


# Workaroundo pradzia
from sqlalchemy import MetaData
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
# Workaroundo pabaiga

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
db = SQLAlchemy(app, metadata=metadata)     # Workaroundo dalis: metadata
migrate = Migrate(app, db, render_as_batch=True)


# Reikia instaliuoti:
# pip install flask-login
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
login_manager = LoginManager()
login_manager.init_app(app)


# Reikia instaliuoti:
# pip install flask-bcrypt
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


# Reikia instaliuoti:
# pip install flask-admin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='Administravimo skydelis', template_mode='bootstrap3')

class ManoModelView(ModelView):
    can_delete = False  # disable model deletion

    def is_accessible(self):
        return current_user.is_authenticated

class IncomeRecord(db.Model):
    __tablename__ = 'saskaitos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    suma = db.Column(db.Integer, nullable=False)
    pavadinimas = db.Column("Pavadinimas", db.String(200), nullable=False)
    #siuntejas = db.Column(db.String(100), nullable=False)
    papildoma_info = db.Column(db.Text, nullable=True)
    #grupe = db.relationship('grupe', back_populates='incomerecord')


import os
import secrets
# Reikia instaliuoti:
# pip install Pillow
from PIL import Image

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilio_nuotraukos', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



class Vartotojas(db.Model, UserMixin):
    __tablename__ = "vartotojas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String(20), unique=True, nullable=False)
    el_pastas = db.Column("El. pašto adresas", db.String(120), unique=True, nullable=False)
    slaptazodis = db.Column("Slaptažodis", db.String(60), unique=True, nullable=False)
    nuotrauka = db.Column(db.String(20), nullable=True, default='default.jpg')
    grupes_saskaitos = db.relationship('Grupesaskaitos', back_populates='vartotojas')


class Grupesaskaitos(db.Model):
    __tablename__ = 'grupes_saskaitos'
    id = db.Column(db.Integer, primary_key=True)
    pavadinimas = db.Column("Pavadinimas", db.String(200), nullable=False)
    tekstas = db.Column("Tekstas", db.Text, nullable=False)
    grupe_id = db.Column(db.Integer, db.ForeignKey('grupes.id'))
    vartotojas_id = db.Column(db.Integer, db.ForeignKey('vartotojas.id'))
    grupe = db.relationship('Grupe', back_populates='grupes_saskaitos')
    vartotojas = db.relationship('Vartotojas', back_populates='grupes_saskaitos')


class Grupe(db.Model):
    __tablename__ = 'grupes'
    id = db.Column(db.Integer, primary_key=True)
    pavadinimas = db.Column("Pavadinimas", db.String(200), nullable=False)
    grupes_saskaitos = db.relationship('Grupesaskaitos', back_populates='grupe')


admin.add_view(ManoModelView(Grupe, db.session))


@login_manager.user_loader
def load_user(user_id):
    return Vartotojas.query.get(user_id)


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    # visi_irasai = Irasas.query.filter_by(vartotojas_id=current_user.id).order_by(Irasas.data.desc()).paginate(page=page, per_page=5)
    # return render_template("irasai.html", visi_irasai=visi_irasai, datetime=datetime)

    grupes_saskaitos = Grupesaskaitos.query.paginate(page=page, per_page=1)
    return render_template('index.html', grupes_saskaitos=grupes_saskaitos)


@app.route('/registracija', methods=['GET', 'POST'])
def register():
    form = forms.RegistracijosForma()
    if form.validate_on_submit():
        koduotas_slaptazodis = bcrypt.generate_password_hash(form.slaptazodis.data).decode('utf-8')
        vartotojas = Vartotojas(vardas=form.vardas.data, el_pastas=form.el_pastas.data, slaptazodis=koduotas_slaptazodis)
        db.session.add(vartotojas)
        db.session.commit()
        flash('Sėkmingai prisiregistravote! Galite prisijungti', 'success')
        return redirect(url_for('index'))
    return render_template('form_register.html', form=form)


@app.route('/prisijungti', methods=['GET', 'POST'])
def login():
    form = forms.PrisijungimoForma()
    if form.validate_on_submit():
        user = Vartotojas.query.filter_by(el_pastas=form.el_pastas.data).first()
        if user and bcrypt.check_password_hash(user.slaptazodis, form.slaptazodis.data):
            login_user(user, remember=form.prisiminti.data)
            next_page = request.args.get('next')
            flash('Sėkmingai prisijungta', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Prisijungti nepavyko. Patikrinkite el. paštą ir slaptažodį', 'danger')
    return render_template('form_login.html', form=form)


@app.route("/atsijungti")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/profilis", methods=['GET', 'POST'])
@login_required
def profile():
    form = forms.PaskyrosAtnaujinimoForma()
    if form.validate_on_submit():
        if form.nuotrauka.data:
            nuotrauka = save_picture(form.nuotrauka.data)
            current_user.nuotrauka = nuotrauka
        current_user.vardas = form.vardas.data
        current_user.el_pastas = form.el_pastas.data
        db.session.commit()
        flash('Tavo paskyra atnaujinta!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.vardas.data = current_user.vardas
        form.el_pastas.data = current_user.el_pastas
    if current_user.nuotrauka:
        nuotrauka = url_for('static', filename='profilio_nuotraukos/' + current_user.nuotrauka)
    else:
        nuotrauka = None
    return render_template('profilis.html', title='Account', form=form, nuotrauka=nuotrauka)
    # return render_template('profilis.html', form=form)
'''
@app.route('/')
def index1():
    balansas = 0
    pajamu_irasai = IncomeRecord.query.all()
    
    for record in pajamu_irasai:
        balansas += record.suma
    
    return render_template('index.html', balansas=balansas,
        pajamu_irasai=pajamu_irasai)
'''
@app.route("/grupe_saskaitos/naujas", methods=['GET', 'POST'])
@login_required
def article_create():
    form = forms.StraipsnioForma()
    if form.validate_on_submit():
        grupes_saskaitos = Grupesaskaitos(
        pavadinimas=form.pavadinimas.data,
        tekstas=form.tekstas.data,
        vartotojas_id=current_user.id,
        grupe_id = form.grupe.data.id)
        db.session.add(grupes_saskaitos)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form_groups.html', form=form)


@app.route("/grupes_saskaitos/<int:article_id>")
def article(article_id):
    grupes_saskaitos = Grupesaskaitos.query.get(article_id)
    if grupes_saskaitos.vartotojas.nuotrauka:
        nuotrauka = url_for('static', filename='profilio_nuotraukos/' + grupes_saskaitos.vartotojas.nuotrauka)
    else:
        nuotrauka = None
    return render_template('groups.html', grupes_saskaitos=grupes_saskaitos, nuotrauka=nuotrauka)




@app.route('/grupes_saskaitos', methods=['GET', 'POST'])
def income():
    form = forms.IncomeForm()
    if form.validate_on_submit():
        # Jei su forma viskas ok
        record = IncomeRecord(
            suma=form.suma.data,
            papildoma_info=form.papildoma_info.data)
        db.session.add(record)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form_bills.html', form=form)

@app.route('/grupes_saskaitos/<int:grupes_saskaitos_id>', methods=['GET', 'POST'])
def income_update(grupes_saskaitos_id):
    record = IncomeRecord.query.get(grupes_saskaitos_id)
    if record is None:
        abort(404)
    form = forms.IncomeForm(obj=record)
    if form.validate_on_submit():
        record.suma = form.suma.data
        record.papildoma_info = form.papildoma_info.data
        db.session.add(record)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('form_bills.html', form=form)


@app.route('/grupes_saskaitos/<int:grupes_saskaitos_id>/delete', methods=['POST'])
def income_delete(grupes_saskaitos_id):
    record = IncomeRecord.query.get(grupes_saskaitos_id)
    if record is None:
        abort(404)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('index'))



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

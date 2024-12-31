from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PhoneField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yourusername:yourpassword@localhost/user_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define models
class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class State(db.Model):
    __tablename__ = 'states'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    country = db.relationship('Country', backref='states')

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'))
    state = db.relationship('State', backref='cities')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))

# Create form for user registration
class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = PhoneField('Phone', validators=[DataRequired()])
    country = SelectField('Country', coerce=int, validators=[DataRequired()])
    state = SelectField('State', coerce=int, validators=[DataRequired()])
    city = SelectField('City', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

# View to handle user addition and the table view
@app.route('/', methods=['GET', 'POST'])
def home():
    form = UserForm()
    form.country.choices = [(c.id, c.name) for c in Country.query.all()]

    if form.validate_on_submit():
        # Create user
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            country_id=form.country.data,
            state_id=form.state.data,
            city_id=form.city.data
        )
        db.session.add(user)
        db.session.commit()
#redirecting to view table
        return redirect(url_for('view_user'))

    # If a GET request or form validation fails
    if form.country.data:
        form.state.choices = [(s.id, s.name) for s in State.query.filter_by(country_id=form.country.data).all()]
    if form.state.data:
        form.city.choices = [(c.id, c.name) for c in City.query.filter_by(state_id=form.state.data).all()]

#loading to index page
    return render_template('index.html', form=form)

# Dynamic loading of states and cities based on selected country/state
@app.route('/get_states/<int:country_id>', methods=['GET'])
def get_states(country_id):
    states = State.query.filter_by(country_id=country_id).all()
    return {'states': [(state.id, state.name) for state in states]}

@app.route('/get_cities/<int:state_id>', methods=['GET'])
def get_cities(state_id):
    cities = City.query.filter_by(state_id=state_id).all()
    return {'cities': [(city.id, city.name) for city in cities]}

@app.route('/view_users')
def view_users():
    users = User.query.all()
    return render_template('view_users.html', users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.country.choices = [(c.id, c.name) for c in Country.query.all()]
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.country_id = form.country.data
        user.state_id = form.state.data
        user.city_id = form.city.data
        db.session.commit()
        return redirect(url_for('view_users'))
    
    return render_template('edit_user.html', form=form, user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('view_users'))

if __name__ == '__main__':
    app.run(debug=True)

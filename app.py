import re
import random
import string
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import (DataRequired,
                                Optional,
                                Regexp,
                                Email,
                                EqualTo,
                                InputRequired,
                                Length,
                                AnyOf,
                                URL)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bank'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfZudsZAAAAAK4zjjg9j8m2CbYICtFMvHlvpF_w'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfZudsZAAAAAA0HzK4nXC57yodWUwHaRZF8BYYi'
app.config['TESTING'] = True


class LoginForm(FlaskForm):
    username = StringField('Email', validators=[InputRequired("Поле поштової скриньки обов'язкове!"),
                                                Email(message="Не коректно ведена поштова скринька!",
                                                      granular_message=True, check_deliverability=True)])
    password = PasswordField('Password', validators=[InputRequired("Пароль обов'язковий!"),
                                                     Regexp(r'[A-Za-z0-9@#$%^&+=]{8,}', flags=0,
                                                            message='Пароль має містити від 8 символів, не мати пробілів, та містити тільки символи латинського алфавіту A-Z, a-z, цифри: 0-9, та спеціальні знаки @#$%^&+=!')])
    recaptcha = RecaptchaField()


class RegistrationForm(FlaskForm):
    name = StringField("І'мя", [InputRequired("І'мя обов'язковe!")])
    surname = StringField('Прізвище ', [InputRequired("Прізвище обов'язковe!")])
    type_of_passport = SelectField('Вкажіть тип паспорту', [DataRequired()],
                                   choices=[('Старий паспорт', 'Старий паспорт'),
                                            ('Паспорт нового зразку ', 'Новий паспорт')])
    passport_id = StringField('PassportID', [InputRequired("PassportID обов'язковe!"),
                                             Regexp(r'^[\w.@+-]+$', message='PassportId не повинно містити пробілів '),
                                             Length(min=8, max=8,
                                                    message="Кількість симмволів PassportId повинно дорівнювати 8!")])
    IPN = StringField('ІПН', [InputRequired("ІПН обов'язковe!"),
                              Regexp(r'^[\0-9]+$', message='IPN не повинно містити пробілів або літер'),
                              Length(min=10, max=10,
                                     message="Кількість цифр ІПН повинно дорівнювати 10!")])
    city = StringField('Місто', [InputRequired("Місто обов'язковe!"),
                                 Regexp(r'^[\Dw.@+-]+$', message="І'мя не повинно містити пробілів і цифр"),
                                 Length(min=2, max=25, message="Місто  повино бути більше 2-ох літер і менше 25")])
    email = StringField('Email', validators=[InputRequired("Поле поштової скриньки обов'язкове!"),
                                             Email(message="Не коректно ведена поштова скринька!",
                                                   granular_message=True, check_deliverability=True)])
    phone = StringField('Телефон ', [InputRequired("Номер телефону обов'язковe!"),
                                     Regexp(r'^^\+?3?8?(0[5-9][0-9]\d{7})$',
                                            message="Некоректно ведений номер телефону!"), Length(min=13, max=13,
                                                                                                  message="Номер телефону повинен дорівнювати 13 символам включаючи <<+>>")])
    password = PasswordField('Пароль', validators=[InputRequired("Пароль обов'язковий!"),
                                                   Regexp(r'[A-Za-z0-9@#$%^&+=]{8,}', flags=0,
                                                          message='Пароль має містити від 8 символів, не мати пробілів, та містити тільки символи латинського алфавіту A-Z, a-z, цифри: 0-9, та спеціальні знаки @#$%^&+=!'),
                                                   EqualTo('confirm', message='Паролі не співпадають')])
    confirm = PasswordField('Повторіть пароль')
    secret = SelectField('Оберіть секретне питання', [DataRequired()],
                         choices=[('Прізвисько', 'Яке прізвисько у вас було в школі?'),
                                  ('Дівоче прізвище ', 'Дівоче прізвище матері'),
                                  ('Найскращий друг', "Ім'я найкращого друга"),
                                  ('Аніме', 'Улюблене аніме')])
    answer = TextAreaField('Відповідь на питання', [InputRequired("Відповідь на питання обов'язковe!")])


class CreationCard(FlaskForm):
    type_ = SelectField('Оберіть тип карти', [DataRequired()],
                        choices=[('Debit', 'Debit'),
                                 ('Credit', 'Credit')])

    rate = SelectField('Оберіть тариф карти', [DataRequired()],
                        choices=[('Gold', 'Gold'),
                                 ('Premium', 'Premium')])


class Luhn:
    db = {}

    def create_(self):
        num = random.randrange(1, 10 ** 10)
        num_with_zeros = '{:010}'.format(num)
        num_with_zeros = str(num).zfill(10)
        card_number = '400000'+num_with_zeros

        num = random.randrange(1, 10 ** 4)
        num_with_zeros = '{:04}'.format(num)
        num_with_zeros = str(num).zfill(4)
        pin = num_with_zeros

        num = random.randrange(1, 10 ** 3)
        num_with_zeros = '{:03}'.format(num)
        num_with_zeros = str(num).zfill(3)
        csv = num_with_zeros

        iban = 'UA4430529900000' + card_number

        self.db[card_number] = pin
        return iban

example = Luhn()


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str

@app.route('/form', methods=['GET', 'POST'])
def form():
    form = LoginForm()

    if form.validate_on_submit():
        return '<h1>Поштова скринька: {}. Пароль: {}.'.format(form.username.data, form.password.data)
    return render_template('form.html', form=form)


@app.route('/re', methods=['GET', 'POST'])
def re():
    re = RegistrationForm()

    if re.validate_on_submit():
        return '<h1>name: {}. surname: {}.'.format(re.name.data, re.surname.data)
    return render_template('registration.html', form=re)


@app.route('/cre', methods=['GET', 'POST'])
def cre():
    cre = CreationCard()
    if cre.validate_on_submit():
        return '<h1>Type: {}. ' \
               'Rate: {}\n. ' \
               '{}'.format(cre.type_.data, cre.rate.data, example.create_())
    return render_template('card_creation.html', form=cre)


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    return render_template('reg_page.html')


@app.route('/reg-in', methods=['GET', 'POST'])
def reg_in():
    if request.method == 'POST':
        reg = request.form
        name = reg["name"]
        surname = reg["surname"]
        email = reg["email"]
        pass_type = reg['passport_type']
        se_pass = reg['se_pass']
        pass_id = reg['pass_id']
        ipn = reg['IPN']
        region = reg['region']
        city = reg['city']
        phone = reg['phone_numb']
        password = reg['password']
        question = reg['secret']
        answer = reg['answer']
        iban = example.create_()
        secret_key = get_random_alphanumeric_string(64)

        tmp = {
                'name': name, 'surname': surname, 'email': email,
                'pass_type': pass_type, 'se_pass': se_pass, 'pass_id': pass_id,
                'ipn': ipn, 'region': region, 'city': city, 'phone': phone,
                'password': password, 'question': question, 'answer': answer,
                'iban': iban, 'secret_key': secret_key
               }

        print(tmp)
        return redirect(url_for('apiget', action="get_secret_key"))


@app.route('/bank/<action>', methods=['GET', 'POST'])
def apiget(action):
    if action == "get_secret_key":
        return render_template("secret_key.html")


if __name__ == '__main__':
    print(example.create_())
    print(get_random_alphanumeric_string(64))
    app.run(debug=True)

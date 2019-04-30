from flask import Flask, url_for, request, render_template, redirect
import json

from flask_wtf import FlaskForm
from flask import session

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

import pmDB


class LoginForm(FlaskForm):        
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
   



app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

is_authorized = False
#session['usrLogin'] = ''
#session['usrPass'] = ''

@app.route('/')
@app.route('/show')
def show():
    if is_authorized:
        items = pmPwds.show(user_id)
        html = '<ul>'
        for i in range(len(items)):
            f_name = items[i][0]
            f_username = items[i][1]
            f_password = items[i][2]
            f_uri = items[i][3]
            f_comment = items[i][4]
            html += '<li>{} > {} > {} > {} > {}</li>'.format(f_name, 
                                                             f_username,
                                                             f_password,
                                                             f_uri,
                                                             f_comment)
            
        html += '<ul>'    
        return render_template('show.xml', title='My account', html=html)
    else:
        return redirect('/auth')



@app.route('/auth', methods=['GET', 'POST'])
def login():
    frmLogin = LoginForm()
    if frmLogin.validate_on_submit():
        session['usrLogin'] = request.form.get('login')
        session['usrPass'] = request.form.get('password')

        #---
        user_id = -1    
        login = session['usrLogin']
        password = session['usrPass']
        user_info = pmUser.user_auth(login, password) 
        isAuth = user_info[0]
        if isAuth:
            user_id = user_info[1] 
            #print('Авторизован {}, id={}'.format(login, user_id))
            return render_template('success.xml', title='My account', login=session.pop('usrLogin'))
        else:
            #print('Ошибка авторизации!')                        
            return render_template('auth.xml', title='Authentication error: Incorrect login or password', form=frmLogin)
        #---
    return render_template('auth.xml', title='Authentication', form=frmLogin)

#continue work -> /show (is_authorized = True)

@app.route('/start', methods=['GET', 'POST'])
def start():
    return render_template('success.xml', title='My account', login=session.pop('usrLogin'))


if __name__ == '__main__':
    ##---Инициализация:
    pm = pmDB.pmDB()
    pmUser = pmDB.pmUsersTable(pm.get_connection())
    pmUser.init_table() #создаем пустую таблицу пользователей, если она не существует
    
    pmPwds = pmDB.pmPasswordsTable(pm.get_connection())
    pmPwds.init_table() #создаем пустую таблицу паролей, если она не существует
    
    ##---
    user_info = pmUser.user_exists('root')
    isExist = user_info[0] #проверяем, существует ли пользователь root
    
    if isExist:
        user_id = user_info[1] #id существующего пользователя, иначе = None
        #print('Уже создан root, его id=', user_id)
    else:
        #print('Пароль root: ', pmUser.add_root())
        pmUser.add_root()
    #------------------------------------------
    app.run(port=8080, host='127.0.0.1', debug=True)
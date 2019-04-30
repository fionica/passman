import sqlite3
from random import choice #для генератора паролей
from werkzeug.security import generate_password_hash #для функции generate_password_hash
from werkzeug.security import check_password_hash

PASSMAN_DB = 'passman.db' #имя файла БД
TBL_USERS = 'users' #таблица пользователей БД
TBL_PWDS = 'pwds'  #таблица записей с паролями
##------------------------------------------------------ 
class pmDB(object):
    #Конструктор:
    def __init__(self):
        #Если база данных не существует, она будет создана автоматически:
        conn = sqlite3.connect(PASSMAN_DB, check_same_thread=False) 
        #Запоминаем в классе подключение к этой базе данных:
        self.conn = conn

    def get_connection(self):
        return self.conn
    
    def __del__(self):
        self.conn.close()
##------------------------------------------------------
#Класс для работы с таблицей пользователей:        
class pmUsersTable(object):
    #----------------------------------------
    #connection - указатель, соединение с БД
    def __init__(self, connection):
        self.connection = connection
    #----------------------------------------
    def init_table(self):
        cursor = self.connection.cursor() #создаем объект для доступа к БД
        #UNUQUE - столбцец таблицы может иметь только уникальные значения (http://unetway.com/tutorial/sqlite-constraints/)
        sql = '''CREATE TABLE IF NOT EXISTS {}
                 (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 login VARCHAR(50) NOT NULL UNIQUE,
                 password_hash VARCHAR(128) NOT NULL
                 )'''.format(TBL_USERS)
        cursor.execute(sql) #Выполняем sql-запрос
        cursor.close() #Применяем (сохраняем) переданные изменения в БД
        self.connection.commit()        
    #----------------------------------------
    #Добавить пользователя:
    def add_user(self, login, password):
        password_hash = generate_password_hash(password)
        cursor = self.connection.cursor()
        sql = '''INSERT INTO {} 
                 (login, password_hash) 
                 VALUES (?,?)'''.format(TBL_USERS)      
        print(password_hash)
        res = cursor.execute(sql, (login, password_hash,))
        cursor.close()
        self.connection.commit()    
        return res
    #----------------------------------------
    #Добавить пользователя root и сгенерировать ему пароль:
    def add_root(self):
        password = self.generate_password(21)        
        self.add_user('root', password)
        return password
    #----------------------------------------
    #Проверить существование пользователя:        
    def user_exists(self, login):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM {} WHERE login=?".format(TBL_USERS), (login,)) #после login указываем ","
        row = cursor.fetchone() #пытается достать одну запись из возвращаемого значения и преобразует её в кортеж значений полей.
        
        #Возвращаем True и уникальный идентификатор пользователя, если он найден, и False в противном случае.
        return (True, row[0]) if row else (False,)      
    #----------------------------------------
    #Авторизация пользователя (true - пользователь с логином и хеш-паролем найден в БД):
    def user_auth(self, login, password):
        cursor = self.connection.cursor()                
        cursor.execute("SELECT user_id, password_hash FROM {} WHERE login=?".format(TBL_USERS), (login,))        
        row = cursor.fetchone() #пытается достать одну запись из возвращаемого значения и преобразует её в кортеж значений полей.
        if row:
            password_hash = row[1]
            #Проверяем введенный пароль и его хэш в БД:
            check_pass = check_password_hash(password_hash, password)
            return (True, row[0]) if check_pass else (False,)  
        else:
            return (False,)
        
    #----------------------------------------
    #http://www.cyberforum.ru/python/thread2218119.html:
    def generate_password(self, len):
        a = ''
        lst = '!@#%&*23456789qwertyuipasdfghjkzxcvbnmQWERTYUPASDFGHJKLZXCVBNM'
        b = ''
        for i in range(len):
            if i != 0:
                while b in list(a):
                    b = choice(lst)
                a += b
            else:
                b = choice(lst)
                a += b
        return a     
##------------------------------------------------------

#Класс для работы с таблицей паролей:        
class pmPasswordsTable(object):
    #----------------------------------------
    #connection - указатель, соединение с БД
    def __init__(self, connection):
        self.connection = connection    
    #----------------------------------------
    def init_table(self):
        cursor = self.connection.cursor() #создаем объект для доступа к БД
        #UNUQUE - столбцец таблицы может иметь только уникальные значения (http://unetway.com/tutorial/sqlite-constraints/)
        sql = '''CREATE TABLE IF NOT EXISTS {} 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name VARCHAR(256),
                 username VARCHAR(256),
                 password VARCHAR(256),
                 uri VARCHAR(256),
                 comment VARCHAR(1024),
                 user_id INTEGER
                 )'''.format(TBL_PWDS)
        cursor.execute(sql) #Выполняем sql-запрос
        cursor.close() #Применяем (сохраняем) переданные изменения в БД
        self.connection.commit()        
    #----------------------------------------
    #Добавить новую парольную запись в таблицу:
    def add_pass(self, name, username, password, uri, comment, user_id):
        cursor = self.connection.cursor()
        sql = '''INSERT INTO {} 
                 (name, username, password, uri, comment, user_id) 
                 VALUES (?,?,?,?,?,?)'''.format(TBL_PWDS)       
        res = cursor.execute(sql, (name, username, password, uri, comment, user_id,))
        cursor.close()
        self.connection.commit()    
        return res
    #----------------------------------------    
    #Показать все созданные парольные записи пользователя user_id:
    def show(self, user_id):
        
        cursor = self.connection.cursor()
        sql = '''SELECT name, username, password, uri, comment FROM {} WHERE user_id=?'''.format(TBL_PWDS) 
        cursor.execute(sql, (str(user_id), ))
        row = cursor.fetchall()
        cursor.close()
        self.connection.commit()    
        return row
    #----------------------------------------
    #Поиск фразы (без учета регистра - LIKE) в таблице парольных записей пользователя с user_id:
    def find(self, text, user_id):
        
        cursor = self.connection.cursor()
        sql = '''SELECT name, username, password, uri, comment FROM {} 
                 WHERE user_id=? 
                 AND 
                 (name LIKE ?
                 OR username LIKE ?
                 OR uri LIKE ?
                 OR comment LIKE ?)
                 '''.format(TBL_PWDS) 
        cursor.execute(sql, [str(user_id), '%'+text+'%', '%'+text+'%', '%'+text+'%', '%'+text+'%'])
        #cursor.execute(sql, [str(user_id), text])
        row = cursor.fetchall()
        cursor.close()
        self.connection.commit()    
        return row    
    #----------------------------------------
##------------------------------------------------------
##------------------------------------------------------
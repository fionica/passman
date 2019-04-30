import pmDB
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
    print('Уже создан root, его id=', user_id)
else:
    print('Пароль root: ', pmUser.add_root())
#------------------------------------------
#Тест авторизации:
print('Введите логин: ')
login = input()
print('Введите пароль: ')
password = input()
    
user_id = -1    
user_info = pmUser.user_auth(login, password) 
isAuth = user_info[0]
if isAuth:
    user_id = user_info[1] 
    print('Авторизован {}, id={}'.format(login, user_id))
else:
    print('Ошибка авторизации!')    
#------------------------------------------
if user_id >= 0:
    
    if pmPwds.add_pass('name', 'username', 'password', 'uri', 'comment', user_id):
        print('Добавлен элемент в список паролей')
    else:
        print('Ошибка при добавлении элемента в список паролей')
    
#------------------------------------------
print('Вывод всех записей пользователя:')
print(pmPwds.show(user_id))
#------------------------------------------
print('Поиск:')
print(pmPwds.find('ur', user_id))
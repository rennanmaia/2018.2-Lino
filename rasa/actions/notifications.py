import requests
import os
from pymongo import MongoClient
from rasa_core.actions.action import Action

# If you have your own database, changes to ('database', <PORT>)
client = MongoClient('mongodb://mongo-ru:27017/lino_ru')
db = client.lino_ru

# If you want to use your own bot to development add the bot token as
# second parameters
telegram_token = os.getenv('ACCESS_TOKEN', '')


class ActionStart(Action):
    def name(self):
        return "custom_start"

    def run(self, dispatcher, tracker, domain):
        a = tracker.current_state()
        id = a['sender_id']
        text = 'text'
        data = requests.get(
                f'https://api.telegram.org/bot{telegram_token}\
                /sendMessage?chat_id={id}&text={text}').json()

        print('SAVING IN THE DATABASE')
        new_user = {}
        id_user = {}
        id_user['sender_id'] = id
        new_user['sender_id'] = id
        new_user['name'] = data['result']['chat']['first_name'] + ' ' + data['result']['chat']['last_name'] # noqa E501
        users = db.users.find({}, {'sender_id': 1, '_id': 0})
        users = list(users)

        if id_user not in users:
            db.users.insert_one(new_user)
            print('SAVED IN DATABASE')
        else:
            print('ALREADY EXISTS')

        return []


class ActionAskNotification(Action):
    def name(self):
        return "action_ask_notification"

    def run(self, dispatcher, tracker, domain):
        messages = []
        a = tracker.current_state()
        id = a['sender_id']

        print('SAVING IN THE DATABASE')

        notifications = db.notifications.find_one()
        user_list = []

        if not notifications:
            new_users = []
            new_users.append(id)
            db.notifications.insert_one({
                'id': 1,
                'description': 'menu_day',
                'users_list': new_users
            })
            messages.append('A partir de agora vc receberá notificações do RU')
        else:
            user_list = notifications['users_list']
        if id not in user_list:
            user_list.append(id)
            db.notifications.update_one({'id': 1}, {
                '$set': {'users_list': user_list}
            })
            messages.append(
                        'A partir de agora vc receberá notificações do RU!')

            print('SAVED IN DATABASE')
        else:
            messages.append('Você já está na lista de usuários cadastrados!')
            print('ALREADY EXISTS')

        dispatcher.utter_message('Okay!')

        for m in messages:
            dispatcher.utter_message(m)

        return []
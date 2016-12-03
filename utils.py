import json
from zipfile import ZipFile

from tqdm import tqdm


def read_users(filename):
    with ZipFile(filename, 'r') as zfile:
        with zfile.open('users.json') as users_file:
            users_text = users_file.read()
            if type(users_text) is not str:
                users_text = users_text.decode('utf8')
            users = json.loads(users_text)
            return {u['id']: u['name'] for u in users}


def message_generator(filename, users=None, show_progress=True):
    if users is None:
        users = read_users(filename)

    msg_id = 0
    with ZipFile(filename, 'r') as zfile:
        if show_progress:
            files = tqdm(zfile.namelist())
        else:
            files = zfile.namelist()
        for name in files:
            if name.count('/') != 1 or not name.endswith('.json'):
                continue

            channel, _ = name.split('/')

            with zfile.open(name) as msgs_file:
                msgs_text = msgs_file.read()
                if type(msgs_text) is not str:
                    msgs_text = msgs_text.decode('utf8')
                messages = json.loads(msgs_text)

                for m in messages:
                    if 'user' not in m:
                        continue

                    user_id = m['user']
                    if user_id not in users:
                        continue
                    user = users[user_id]

                    ts = float(m['ts'])

                    msg_id += 1
                    text = m.get('text', "NO_TEXT")

                    if 'reactions' in m:
                        reactions = {r['name']: [users[u] for u in r['users'] if u in users] for r in m['reactions']}
                    else:
                        reactions = {}

                    yield msg_id, channel, user, text, ts, reactions

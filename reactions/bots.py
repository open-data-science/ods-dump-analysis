import json
from collections import Counter

from reactions.prepare_reactions_log import ods_dump_file
from utils import message_generator

DATA_PATH = 'bot-messages.json'


def read_bots():
    bot_names = {'mitzva_bot', 'markov-bot'}
    messages = {}
    for msg_id, channel, user, text, ts, reactions in message_generator(ods_dump_file):
        if channel != 'bots' or user not in bot_names:
            continue
        message = {'text': text, 'bot': user, 'r': reactions, 'ts': ts}
        messages[msg_id] = message
    return messages


def dump(messages):
    with open(DATA_PATH, 'w', encoding='utf8') as fout:
        json.dump(messages, fout, ensure_ascii=False)


def load():
    with open(DATA_PATH, 'r', encoding='utf8') as fout:
        return {int(k): v for k, v in json.load(fout).items()}


def reactions_count(msgs):
    return sum(map(lambda x: sum(map(len, x['r'].values())), msgs.values()))


def zero_reactions_count(msgs):
    return len(list(filter(lambda x: len(x['r']) == 0, msgs.values())))


def one_user_per_message_reactions(msgs):
    return sum(map(lambda x: len({u for r in x['r'].values() for u in r}), msgs.values()))


def is_interesting(msg):
    # if len(msg['r']) < 2:
    #     return False
    return len({u for r in msg['r'].values() for u in r}) > 1  # At least 2 reacted users


def top_reactions(msgs, top=5):
    reactions = Counter([r for msg in msgs.values() for r, u in msg['r'].items() for _ in range(len(u))])
    return dict(sorted(reactions.items(), key=lambda x: -x[1])[:top])


def describe(msgs, bot=None):
    if bot:
        print(bot, 'statistics')
        msgs = dict(filter(lambda x: x[1]['bot'] == bot, msgs.items()))
    else:
        print('Total statistics')
    msgs_count = len(msgs)
    print(msgs_count, 'messages')
    reactions = reactions_count(msgs)
    print(reactions, 'reactions')
    zero = zero_reactions_count(msgs)
    print('Average reactions', reactions / msgs_count)
    print('%.02f%%' % (100 * (msgs_count - zero) / msgs_count), 'messages with reactions')
    user_per_message = one_user_per_message_reactions(msgs)
    print('Unique reacted users per message', user_per_message)
    print('Average', user_per_message / msgs_count)

    interesting = dict(filter(lambda x: is_interesting(x[1]), msgs.items()))
    interesting_count = len(interesting)
    print(interesting_count, '(%.02f%%)' % (100 * interesting_count / msgs_count),
          'messages with reactions from more than 1 user')

    print('Top reactions')
    tr = top_reactions(msgs)
    print('\t', '\n\t'.join(['{}: {}'.format(k, v) for k, v in sorted(tr.items(), key=lambda x: -x[1])]), sep='')
    print()


if __name__ == '__main__':
    # msgs = read_bots()
    # dump(msgs)

    msgs = load()
    describe(msgs)
    describe(msgs, 'mitzva_bot')
    describe(msgs, 'markov-bot')

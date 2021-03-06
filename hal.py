# -*- coding: utf-8 -*-
import weechat
import os.path
import datetime

debug = False
userlist = '/home/user/.weechat/userlist'
users = []

options = {
    'bitchmode_chans': 'ircnet.#funfactory,ircnet.#cyberworld',
       'autoop_chans': 'ircnet.#funfactory,ircnet.#cyberworld',
}

weechat.register('HAL', 'The Hell', '6.6.6', 'GPL3', 'Hell Script', '', '')

for option, default_value in options.items():
    if not weechat.config_get_plugin(option):
        if default_value:
            weechat.config_set_plugin(option, default_value)
        else:
            error = weechat.prefix("error")
            weechat.prnt("", "%s%s: /set plugins.var.python.%s.%s" % (
                error,
                HAL,
                HAL,
                option))

def halp_cb():
    weechat.prnt('', '\n           --Start Help--          \n')
    weechat.prnt('', '/halp (display this help)')
    weechat.prnt('', '/userlist (shows the userlist)')
    weechat.prnt('', '/adduser ip/host')
    weechat.prnt('', '/deluser ip/host')
    weechat.prnt('', 'Example Usage: /adduser *!*@hostname.com | /deluser *!*@123.456.789')
    weechat.prnt('', '\n           --End Help--            \n')
    return ''

def help_cb(data, buffer, args):
    current = weechat.current_buffer()
    weechat.prnt(current, '{0}'.format(halp_cb()))
    return weechat.WEECHAT_RC_OK

weechat.hook_command('halp', '', '', '', '', 'help_cb', '')

def userlist_cb(data, buffer, args):
    global users
    current = weechat.current_buffer()
    for u in users:
        weechat.prnt(current, 'HAL\t' + u)
    return weechat.WEECHAT_RC_OK

weechat.hook_command('userlist', '', '', '', '', 'userlist_cb', '')

def adduser_cb(data, buffer, args):
    global users
    current = weechat.current_buffer()
    args = args.split()
    arg = args[0]
    if not any(arg in u for u in users):
        users.append(arg + '\n')
        weechat.prnt(current, 'HAL\t' + arg + ' added')
    else:
        weechat.prnt(current, 'HAL\t' + arg + ' already exists')
    store = True
    if store:
        weechat.prnt(current, 'HAL\tStoring ' + userlist)
        put(userlist, users)
    return weechat.WEECHAT_RC_OK

weechat.hook_command('adduser', '', '', '', '', 'adduser_cb', '')

def deluser_cb(data, buffer, args):
    global users
    current = weechat.current_buffer()
    args = args.split()
    arg = args[0]
    try:
        users.remove(arg + '\n')
    except:
        weechat.prnt(current, 'HAL\tUser does not exist')
    else:
        weechat.prnt(current, 'HAL\t' + arg + ' deleted')
    store = True
    if store:
        weechat.prnt(current, 'HAL\tStoring ' + userlist)
        put(userlist, users)
    return weechat.WEECHAT_RC_OK

weechat.hook_command('deluser', '', '', '', '', 'deluser_cb', '')

def get(filename):
    file = open(filename, 'r') 
    users = file.readlines()
    file.close()
    return users

def put(filename, users):
    file = open(filename, 'w')
    file.writelines(users)
    file.close()

def timer_cb(data, remaining_calls):
    current = weechat.current_buffer()
    global users
    if os.path.isfile(userlist):
        weechat.prnt(current, 'HAL\tReading ' + userlist)
        users = get(userlist)
    else:
        weechat.prnt(current, "HAL\tUsing default userlist")
        users = [
            '*!*@82-197-212-247.dsl.cambrium.nl',
            '*!*@80-101-145-252.ip.xs4all.nl',
            '*!*@2a01:238:4350:ff00:c53e:c819:422a:2511'
        ]
    if debug:
        for u in users:
            weechat.prnt(current, 'user\t' + u)
    weechat.prnt(current, '%s' % data)
    return weechat.WEECHAT_RC_OK

weechat.hook_timer(2000, 0, 1, 'timer_cb', 'HAL\tSystem fully operational')

def priv_cb(data, signal, signal_data):
    global users
    current = weechat.current_buffer()
    args = signal_data.split(' ')[0:3]
    nick = args[0][1:].split('!')[0]
    user = args[0][1:].split('!')[1].split('@')[0]
    host = args[0][1:].split('!')[1].split('@')[1]
    target = args[2]
    message = signal_data.split(' PRIVMSG ')[1].split(' :')[1]
    if debug:
        weechat.prnt(current, '===\t========== Debug ==========')
        weechat.prnt(current, 'raw\t' + signal_data)
        weechat.prnt(current, 'vars\tnick=' + nick + ', user=' + user + ', host=' + host + ', target=' + target)
        weechat.prnt(current, 'msg\t' + message)
    if any(host in u for u in users):
        if message[0] == '/':
            if len(message.split(' ')) > 1:
                arg = message.split(' ')[1]
            else:
                arg =''
            store = False
            if message[1:4] == 'say':
                weechat.command(current, 'Yo')
                weechat.command(current, message[5:])
            elif message[1:5] == 'quit':
                weechat.command(current, 'hihi')
            elif message[1:8] == 'adduser':
                if not any(arg in u for u in users):
                    users.append(arg + '\n')
                    weechat.prnt(current, 'HAL\t' + arg + ' added')
                    weechat.command(current, '/msg ' + nick + ' ' + arg + ' added')
                else:
                    weechat.prnt(current, 'HAL\t' + arg + ' already exists')
                    weechat.command(current, '/msg ' + nick + ' ' + arg + ' already exists')
                store = True
            elif message[1:8] == 'deluser':
                try:
                    users.remove(arg + '\n')
                except:
                    weechat.prnt(current, 'HAL\tUser does not exist')
                    weechat.command(current, '/msg ' + nick + ' User does not exist')
                else:
                    weechat.prnt(current, 'HAL\t' + arg + ' deleted')
                    weechat.command(current, '/msg ' + nick + ' ' + arg + ' deleted')
                    store = True
            elif message[1:10] == 'userlist':
                weechat.command(current, '/msg ' + nick + ' -----begin-----')
                for u in users:
                    weechat.command(current, '/msg ' + nick + ' ' + u)
                weechat.command(current, '/msg ' + nick + ' ------end------')
            else:
                weechat.command(current, message)
            if store:
                weechat.prnt(current, 'HAL\tStoring ' + userlist)
                put(userlist, users)
        if debug:
            for u in users:
                weechat.prnt(current, 'user\t' + u)
        if debug:
            weechat.prnt(current, 'match\t' + host)
            weechat.prnt(current, 'msg\t' + message)
    if 'HAL900' in message.upper():
        if 'HOE LAAT' in message.upper() or 'TIME' in message.upper():
            weechat.command(current, str(datetime.datetime.now()))
    return weechat.WEECHAT_RC_OK

weechat.hook_signal('*,irc_in2_privmsg', 'priv_cb', '')

def mode_cb(data, signal, signal_data):
    global users
    server = signal.split(",")[0]
    args = signal_data.split(' ')[0:5]
    victim = args[4]
    modus = args[3]
    target = args[2]
    nick = args[0][1:].split('!')[0]
    host = args[0][1:].split('!')[1].split('@')[1]
    msg = weechat.info_get_hashtable("irc_message_parse", {"message": signal_data})
    buffer = weechat.info_get("irc_buffer", "%s,%s" % (server, msg["channel"]))
    chan_buffer = weechat.buffer_get_string(buffer, "name")
    for active_buffer in weechat.config_get_plugin('bitchmode_chans').split(','):
        if active_buffer.lower() == chan_buffer.lower() and not any(host in u for u in users):
            if '+o' == modus:
                weechat.command(buffer, '/mode ' + target + ' -oo ' + victim + ' ' + nick)
            if '-o' == modus:
                weechat.command(buffer, '/mode ' + target + ' +o-o ' + victim + ' ' + nick)
            if '-l' == modus:
                weechat.command(buffer, '/kick ' + target + ' ' + nick)
    return weechat.WEECHAT_RC_OK

weechat.hook_signal('*,irc_in2_mode', 'mode_cb', '')

def op_join_cb(data, signal, signal_data):
    global users
    args = signal_data.split(' ')[0:3]
    server = signal.split(",")[0]
    msg = weechat.info_get_hashtable("irc_message_parse", {"message": signal_data})
    buffer = weechat.info_get("irc_buffer", "%s,%s" % (server, msg["channel"]))
    nick = args[0][1:].split('!')[0]
    host = args[0][1:].split('!')[1].split('@')[1]
    target = args[2][1:]
    chan_buffer = weechat.buffer_get_string(buffer, 'name')
    for active_buffer in weechat.config_get_plugin('autoop_chans').split(','):
         if active_buffer.lower() == chan_buffer.lower() and any(host in u for u in users):
            weechat.command(buffer, '/wait 6 /mode ' + target + ' +o ' + nick)
    return weechat.WEECHAT_RC_OK

weechat.hook_signal('*,irc_in2_join', 'op_join_cb', '')

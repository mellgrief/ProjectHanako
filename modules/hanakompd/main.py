import modules.uplot.config as config
import core.lib as lib
try:
    import mpd
except:
    print('%s requires mpd. instal it with python3 -m pip install python-mpd2'%__name__)


author = "undefined_value"
name = "HanakoMPD"
description = '''This module allows you to manage MPD, change tracks, volume, stop/resume playback and show current track. '''
version = '0.0.1'
command = '/mpc'

logger = lib.Log('HanakoMPD')

def mpd_query(rq, *args):
    mpc = mpd.MPDClient()
    try:
        mpc.connect(config.host, config.port)
        mpc.password(config.password)
    except ConnectionRefusedError as e:
        return False, repr(e)
    except mpd.CommandError as e:
        pass
    except Exception as e:
        return False, repr(e)
    finally:
        try:
            return True, getattr(mpc, rq)(*args)
        except Exception as e:
            return False, repr(e)

def handle(message, bot):
    params = shlex.split(message.text)
    if len(params) < 2:
        bot.reply_to(message, '<b>Not enough parameters</b>', parse_mode='html')
        return
    _, cmd, *params = params
    if cmd == 'play':
        s, r = mpd_query('play')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        s, r = mpd_query('status')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        if r.get('error'):
            bot.reply_to(message, '<b>ERROR: %s</b>'%r['error'], parse_mode='html')
    elif cmd in ('now', 'current', 'currentsong'):
        s, r = mpd_query('currentsong')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        bot.reply_to(message, '''\
<b>Currently playing:</b> <pre>{artist} - {title}</pre>
<b>File:</b> <pre>{file}</pre>'''.format(
    artist=r.get('artist', 'Unknown'),
    title=r.get('title', 'Unknown'),
    file=r.get('file', '--- no data ---')))

    elif cmd in ('next', 'nextsong'):
        s, r = mpd_query('next')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        s, r = mpd_query('currentsong')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r.get('file')), parse_mode='html')

    else:
        s, r = mpd_query('status')
        if not s:
            r = {'error': r}
        bot.reply_to(message, '''\
<b>HanakoMPD module by undefined_value<b>
Type /mpc help for more help
Current status: {play_state}
Error level: {error}
Volume: {volume}%'''.format(
    play_state=r.get('state', 'N/A'),
    error=r.get('error', ''),
    volume=r.get('volume', 'N/A')))


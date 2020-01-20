import json
import os


if os.name != 'nt':
    raise OSError('Bad OS "%s"; not yet implemented' % os.name)

app_name = 'tictactoe'


user_home = os.environ.get('USERPROFILE').replace('\\', '/')
user_appdata = os.environ.get('APPDATA').replace('\\', '/')
host = os.getenv('COMPUTERNAME').lower()
appdata = '/'.join([user_appdata, app_name])
os.makedirs(appdata, exist_ok=True)
config_fpath = '/'.join([appdata, 'config.json'])

defaults = {
    'home': '/'.join([user_home, app_name]),
}
if not os.path.isfile(config_fpath):
    with open(config_fpath, 'w') as fp:
        json.dump(defaults, fp, indent=4)
with open(config_fpath, 'r') as fp:
    settings = json.load(fp)

home = settings.get('home', defaults['home'])
os.makedirs(home, exist_ok=True)

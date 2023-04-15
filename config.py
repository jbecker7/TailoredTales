try:
    from flask import Flask
except:
    print("could not import Flask from flask")

from config import Config

app = Flask( __name__, static_url_path='')
app.config.from_object(Config)

from app import routes
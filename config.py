import os


BASE_URL = "http://localhost:5000"
CSS_ROOT = "/static/css/"
ADMIN_CSS_ROOT = "/static/admin/css/"
JS_ROOT = "/static/js/"
IMG_ROOT = "/static/images/"

def l(file_name):
    return BASE_URL + '/' + file_name
def css(filename):
    return BASE_URL + '/' + CSS_ROOT + filename
def admin_css(filename):
    return BASE_URL + '/' + ADMIN_CSS_ROOT + filename
def js(filename):
    return BASE_URL + '/' + JS_ROOT + filename
def img():
    return IMG_ROOT


# Database
MYSQL_HOST = "ssuet-mysql-server.mysql.database.azure.com"  # Server name
MYSQL_USER = "assvrvegff@ssuet-mysql-server"                 # Username + @server
MYSQL_PASSWORD = "87IIFMvk6tAV$FFD"
MYSQL_DB = "ssuet_db"

# OpenAI / DeepSeek
API_KEY = os.getenv("API_KEY")
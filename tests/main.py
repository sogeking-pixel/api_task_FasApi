from app.core.config import settings

fake_key = "xdfdafasdfasdfasd"
real_key = f"API GROSSO|{settings.API_KEY}"

url_sig_up =   settings.API_PREFIX+'/auth/sign-up/'
url_login =  settings.API_PREFIX+'/auth/login/'
url_logout =  settings.API_PREFIX+'/auth/logout/'


client_create = {
  "first_name": "string",
  "last_name": "string",
  "dni": "string",
  "username": "string",
  "date_born": "2025-03-17",
  "password": "string"
}

url_user =   settings.API_PREFIX+'/users/'
url_me =   settings.API_PREFIX+'/users/me'
url_create_admin =  settings.API_PREFIX+'/user/create_admin'

url_tak =   settings.API_PREFIX+'/tasks/'

task_create = {
    "title" : "title test",
    "description" : "test",
    "priority" : "medium"
}


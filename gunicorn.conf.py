bind = 'unix:/run/gunicorn.sock'
workers = 3
user = 'www-data'
group = 'www-data'
errorlog = '/var/log/gunicorn.error.log'
accesslog = '/var/log/gunicorn.access.log'
loglevel = 'info' 
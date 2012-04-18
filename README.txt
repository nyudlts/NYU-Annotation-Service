NYU Annotations service: Application Documentation

Code Sources:
    Source code located at: https://bitbucket.org/alex_bojko/nyu
    You can check it out with command 
    hg clone https://bitbucket.org/alex_bojko/nyu

To get access to the repository, create an account with 
Bitbucket and contact Alex for permission (https://bitbucket.org/alex_bojko).

You can update checked out copy just running commands:
    hg pull
    hg up
    python src/annotation_server/manage.py migrate

You need to install python-dev package.
    sudo apt-get install python-dev


Depends on database engine (it may be MySQL, PostgreSQL, SQLite3 (Oracle not tested)) 
you need to install python driver for this DB.

For MySQL it would be python-mysql and you can install it with this command:
    sudo apt-get install python-mysqldb
For PostgreSQL (you need to install postgres and postgres-dev packages before python driver installation):
    sudo apt-get install python-psycopg2
For SQLite3:
    sudo apt-get install sqlite3
For other DB engines see https://docs.djangoproject.com/en/1.3/ref/databases/


How to install the service:
    python setup.py install

Then find the project and edit settings.py file.
How to find settings.py file?
    python -c "from annotation_server import settings; print settings.__file__[:-1]"

How to check that service was installed correctly?
    python src/annotation_server/check_installation.py
This script write all info in logs. Check it.

How to update installed service to newest version?
    In the directory src/annotation_server you can find update_service.py script.
    Just run it with command:
        $python update_service.py
    That's all!

Dependencies:
    python 2.7
    mysql
All dependencies for a django you can install just run 1 command: 

    pip install -r {path_to_working_copy_directory}/pip_req.txt

Initializing the Database:

 You can use MySQL, Postrges, SQLite3 or Oracle.
 Choose one of the engines listed in ENGINE comments.
 Then setup DB name, username and password to access DB.
 If DB is not on the local host you should to setup HOST and PORT.

           ======== Example ==========
 For example you have:
   MySQL DB named                                      annotations
   username to access this DB is                       annotation_servc_user
   password                                            Annotations_11
   host where is located DB is                         192.168.1.2
   port on this host to access MySQL DB is             3310
       but if you don't know which port to use try don't set this option. In this case
       annotation service will try to connect to the DB with default port for this DB.

 So, you need to write this:

 Write next lines in settings.py file.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'annotations',
        'USER': 'annotation_servc_user',
        'PASSWORD': 'Annotations_11',
        'HOST': '192.168.1.2',
        'PORT': '3310',
    }
}

Please read comments below for correct setting up DB access.
    The first time you run the application you will need to initialize the databse:

    python manage.py syncdb

Starting and stopping the service:
    If you need to start service you can do it with just one command from the root directory of the project:
    ./annotation_service.sh start

Then you can stop service:
    ./annotation_service.sh stop

( To run the service on the django development server, you can also do:
    python server/manage.py runserver
This will start the django development server on the default port)

After service installation you should to change "Site name" in admin interface.
Go to /admin/ and login as admin. (login: admin, pwd: admin). Then go to the Sites and change one existent site.

If you will run service on test server put in
Domain name: http://127.0.0.1:8000
Display name: localhost

If you want to run service with public domain name put 
your domain name with prefix "http://" into "Domain name" field.
Display name may be any word you like.

For example:
Domain name: http://your.domain.com
Display name: my site

These options are needed for correct URLs into service.

To do ability of sending emails with confirmation links of the server you need to do few things:
1) edit settings.py file and put your email account data (something like this):

    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'your_nickname@gmail.com'
    EMAIL_HOST_PASSWORD = 'password'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'no-reply@nyu.com'
2) restert service:
    annotation_service.py restart
That's all!



            ============ Production ===========
To start service in production I propose you to use NGINX as front end server.
NGING will serve static files and proxy requests to annotation service.

To realize this you should to setup NGINX:

sudo apt-get install nginx


Then open you favorite text editor and write something like this in section http {}

  server {
    listen 8008; # Choose port. By default port is 80. 
    server_name  dev-dl-pa.home.nyu.edu; # Write here your domain name.
    index index.html;
    root   /www/sites/annotations/dev/server/nyu/media/; # Where is located folder with annotation service project?
    # static resources

    location /media {
      root /www/sites/annotations/dev/server/nyu/;
    }
 
#    location ~* ^.+\.(html|jpg|jpeg|gif|png|ico|css|zip|tgz|gz|rar|bz2|doc|xls|exe|pdf|ppt|txt|tar|mid|midi|wav|bmp|rtf|js)$
#    {
#      expires 30d;
#      root /www/sites/annotations/dev/server/nyu/media/;
#      break;
#    }
 
    location / {
      # host and port to fastcgi server
      fastcgi_pass unix:/www/sites/annotations/log/django.sock; # Where socket file is located.

      ## Don't change this 7 lines.
      fastcgi_param PATH_INFO $fastcgi_script_name;
      fastcgi_param REQUEST_METHOD $request_method;
      fastcgi_param QUERY_STRING $query_string;
      fastcgi_param CONTENT_TYPE $content_type;
      fastcgi_param CONTENT_LENGTH $content_length;
      fastcgi_pass_header Authorization;
      fastcgi_intercept_errors off;
    }
 
    location /403.html {
      root   /usr/share/nginx;
      access_log   off;
    }
 
    location /401.html {
      root   /usr/share/nginx;
      access_log   off;
    }
 
    location /404.html {
      root   /usr/local/nginx;
      access_log   off;
    }
 
    location = /_.gif {
      empty_gif;
      access_log   off;
    }

    # Here is paths to the log files where nginx should store logs.
    access_log  /www/sites/annotations/log/annotation.access_log main;
    error_log   /www/sites/annotations/log/annotation.error_log;
  }


BE AWARE!

Path to the socket file in file annotation_service.sh and in the file nginx.conf should be the same.

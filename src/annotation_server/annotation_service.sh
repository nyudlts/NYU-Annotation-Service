#!/bin/bash
PID=/www/sites/annotations/log/django.pid 
SOCKET=/www/sites/annotations/log/django.sock

PID=/tmp/annotation.pid
SOCKET=/tmp/annotation.socket


PYTHON_VERS="2.7"
PYTHON_VERS=""
PYTHON=`which python${PYTHON_VERS}`

PATH_TO_MANAGE=`${PYTHON} -c "from annotation_server import manage; print manage.__file__"` # 2>/dev/null`



if [ ! $PATH_TO_MANAGE ]
then
    echo "default manage.py path applied"
    chmod +x manage.py
    PATH_TO_MANAGE=manage.py
else
    echo $PATH_TO_MANAGE
fi

case "$1" in
    "start")
        echo "Starting annotation server"
        ${PYTHON} $PATH_TO_MANAGE runfcgi maxchildren=10 \
		maxspare=5 minspare=2 method=prefork socket=${SOCKET} pidfile=${PID}
    ;;

    "start_dev")
        $PYTHON $PATH_TO_MANAGE runserver 
    ;;
    "syncdb")
        $PYTHON $PATH_TO_MANAGE syncdb
        $PYTHON $PATH_TO_MANAGE migrate
    ;;
    "stop")
        if [ -f $PID ]
        then
            kill `cat $PID`;
            rm $PID;
        else
            echo "Server is not runned";
        fi
    ;;
    
    "restart")
        $0 stop
        sleep 1
        $0 start
    ;;
    
    *)
        echo "Usage: $0 {start|start_dev|stop|restart|syncdb}"
    ;;
esac


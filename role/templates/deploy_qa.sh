#!/bin/sh

set -e

BAK_DIR=/home/yjyx/backup/
INST_DIR=/home/yjyx/yijiao_src
NEW_SRC_DIR=/home/yjyx/yijiao_build
DB_USER=dbadmin
DB_PASSWD=yijiaoqaz

mkdir -p $BAK_DIR

TS=`date +%Y%m%d_%H%M`
# `date +%s`
# backup
echo "------- step 1 --------backuping code and database..."
cd $INST_DIR/
tar czf $BAK_DIR/yijiao_nd_${TS}.tgz yijiao_main pylib
tar czf $BAK_DIR/yijiao_cfg.tgz yijiao_main/project/settings.py yijiao_main/static/common/settings.js
mysqldump -u$DB_USER -p$DB_PASSWD --database yjyx --add-drop-database> $BAK_DIR/yjyx-nd-${TS}.sql

find $BAK_DIR/ -mtime +2 -name "*.tgz" -exec rm -rf {} \;
find $BAK_DIR/ -mtime +2 -name "*.sql" -exec rm -rf {} \;

echo "------- step 2 -------- fake migrate ..."

# delete migration files and records in DB
cd $INST_DIR
rm -fr yijiao_main/services/datamodel/*/migrations
mysql -u$DB_USER -p$DB_PASSWD --database yjyx -e 'delete from django_migrations'

# create fake migration records in DB
cd yijiao_main
MODELS=$(ls -ld services/datamodel/*/|sed  -n 's/.*\/\(.\+\)\/$/\1/p'|grep -v -e "__"|paste -d " " -s)
python36 manage.py makemigrations $MODELS
python36 manage.py migrate --fake

echo "------- step 3 -------- copy new source to source dir ..."


cd $NEW_SRC_DIR

# pack new source files
rm -f /var/tmp/patch.tgz
tar czf /var/tmp/patch.tgz --exclude='log/' --exclude='static/common/settings.js' --exclude='project/settings.py' --exclude='*.pyc' yijiao_main pylib

# extract new source files to install dir. Note, new source files does not have any migration folders.
tar xzf /var/tmp/patch.tgz -C $INST_DIR/

# restore previous setting files
cd $INST_DIR/yijiao_main
tar xzf $BAK_DIR/yijiao_cfg.tgz -C $INST_DIR/

echo "------- step 4 -------- migrate ..."

MODELS_NEW=$(ls -ld services/datamodel/*/|sed  -n 's/.*\/\(.\+\)\/$/\1/p'|grep -v -e "__"|paste -d " " -s)
yes yes | python36 manage.py makemigrations $MODELS_NEW
yes yes | python36 manage.py migrate

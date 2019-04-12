# -*- coding:utf-8 -*-
from .settings_common import *

WEB_SERVER_LISTEN_ADDR = ('{{ project_address }}', {{ project_port }})
CELERY_BROKER_URL = '{{ celery_broker_url }}'
CELERY_REDIS_PASSWD = '{{ celery_redis_passwd }}'
MQ_MGR_URL = '{{ mq_url }}'
MQ_MGR_USER = '{{ mq_user }}'
MQ_MGR_PASSWD = '{{ mq_passwd }}'
MQ_CHORD_VHOST = '{{ mq_vhost }}'
MQ_CHORD_QUEUE = '{{ mq_queue }}'
GUNICORN_WORKER_NUMBER = multiprocessing.cpu_count()
RedisInfo = {}

DATABASES['default']['NAME'] = '{{ mysql_yjyx_database }}'
DATABASES['default']['USER'] = '{{ mysql_yjyx_user }}'
DATABASES['default']['PASSWORD'] = '{{ mysql_yjyx_password }}'
DATABASES['default']['HOST'] = '{{ mysql_yjyx_host }}'
DATABASES["default"]["OPTIONS"]["init_command"] = None

DEBUG = True
ALIPAY_CALLBACK_ADDR = 'qa.zgyjyx.net'
DOMAIN_URL = "https://qa.zgyjyx.net"
CALLBACK_URL = ''


class alipay_settings():
    ALIPAY_KEY = ''
    ALIPAY_PARTNER = ''
    ALIPAY_SELLER_EMAIL = ''
    ACCOUNT_NAME = u''
    ALIPAY_INPUT_CHARSET = 'utf-8'
    ALIPAY_SIGN_TYPE = 'MD5'
    ALIPAY_MOBILE_SIGN_TYPE = 'RSA'
    ALIPAY_SHOW_URL = ''
    ALIPAY_TRANSPORT = 'https'
    ALIPAY_RETURN_URL_STUDENT_BUY_PRODUCT = 'http://%s/student/payment/alipay_buy_product_result.html' % ALIPAY_CALLBACK_ADDR
    ALIPAY_NOTIFY_URL_STUDENT_BUY_PRODUCT = 'http://%s/api/payment/ali/student_buy_product_notify' % ALIPAY_CALLBACK_ADDR
    ALIPAY_MOBILE_NOTIFY = 'http://%s/api/payment/ali/mobilepaynotify' % ALIPAY_CALLBACK_ADDR


class wx_settings():
    APP_ID = ""
    APP_SECRET = ""
    MCH_ID = ""
    MCH_SECRET = ""
    MCH_SSL_CERT_PATH = ""
    MCH_SSL_KEY_PATH = ""
    WX_AHTH_REDIRECT_DOMAIN = ''


QINIU_accessKey = ''
QINIU_secretKey = ''
QINIU_videoBucketName = 'test-video'
QINIU_videoBucketDomain = ''
QINIU_imgBucketName = 'test-img'
QINIU_imgBucketDomain = ''
QINIU_textBucketName = 'test-text'
QINIU_textBucketDomain = ''
QINIU_docBucketName = "test-img"
QINIU_docBucketDomain = ""

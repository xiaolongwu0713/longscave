from alipay import AliPay
import time, qrcode
import os
from flask import Flask, render_template
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
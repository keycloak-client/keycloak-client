#! -*- coding: utf-8 -*-
from flask import Blueprint


auth = Blueprint('auth', __name__)


@auth.route('/')
def home():
    return 'Hola!'


@auth.route('/info')
def info():
    return 'Info'

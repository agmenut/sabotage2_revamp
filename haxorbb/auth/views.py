# -*- coding: utf-8 -*-
from flask import render_template
from . import auth
#from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth/register.html')


@auth.route('/logout', methods=['POST'])
def logout():
    pass



from flask import render_template, redirect, url_for, flash, request
from ERP import app, database, bcrypt
from ERP.forms import FormLogin, FormCriarConta
from ERP.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image


from flask.views import MethodView
from flask import render_template, request


class testAPI(MethodView):
    def get(self):
        return render_template('index_loggedin.html')

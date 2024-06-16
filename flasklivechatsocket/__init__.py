from flask import Flask, render_template, flash, redirect, url_for

def create_app():
    # create a flask instance
    app = Flask(__name__)
    # secret key
    app.config['SECRET_KEY'] = 'fdsi12fer32f28h6sgfw2gt75'
    

    # custom error pages

    # invalid url
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    # internal server error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error/500.html'), 500
    
    return app
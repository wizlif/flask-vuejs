from flask import Blueprint, render_template

client_bp = Blueprint('client_app', __name__,
                      url_prefix='',
                      static_url_path='',
                      static_folder='./vue-app/dist',
                      template_folder='./vue-app/dist',
                      )


@client_bp.route('/')
def index():
    return render_template('index.html')


docs_bp = Blueprint('docs_app', __name__,
                    url_prefix='',
                    static_url_path='/docs/_static',
                    static_folder='_static',
                    template_folder='./docs',
                    )


@docs_bp.route('/docs')
def docs_index():
    return render_template('docs.html')

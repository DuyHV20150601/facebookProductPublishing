import random
import uuid

from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from rauth.service import OAuth2Service

from src.utils import oauth_decode, load_config
from src.facebook import Facebook

product_tpl = load_config(file_path='src/configs/product.yaml')
config = load_config(file_path='src/configs/configs.yaml')['config']

# Flask config
SECRET_KEY = str(random.random())
DEBUG = True
FB_CLIENT_ID = config['app_id']
FB_CLIENT_SECRET = config['app_secret']

# Flask setup
app = Flask(__name__)
app.config.from_object(__name__)
# rauth OAuth 2.0 service wrapper
graph_url = 'https://graph.facebook.com/'
facebook = OAuth2Service(name='facebook',
                         authorize_url='https://www.facebook.com/dialog/oauth',
                         access_token_url=graph_url + 'oauth/access_token',
                         client_id=app.config['FB_CLIENT_ID'],
                         client_secret=app.config['FB_CLIENT_SECRET'],
                         base_url=graph_url)


# views
@app.route('/')
def index():
    redirect_uri = url_for('authorized', _external=True)
    params = {'redirect_uri': redirect_uri,
              'scope': 'catalog_management, ads_management, pages_manage_posts, instagram_basic',
              'auth_type': 'reauthorize'}
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(facebook.get_authorize_url(**params))
    return redirect(facebook.get_authorize_url(**params))
    # return render_template('login.html')


@app.route('/fb_shop/add_new_product_fb_shop')
def add_new_product_fb_shop():
    fb = Facebook(access_token=session.get('user_access_token'))
    print('User id: %s \nAccess token: %s\n' % (session.get('id'), session.get('user_access_token')))
    page_list = fb.user_get_pages(user_id=session.get('id'),
                                  access_token=session.get('user_access_token'))
    print('***************************************************************')
    print(page_list)
    page_list_dict = {}
    for page in page_list:
        print(page)
        page_list_dict.update({page['name']: page['id']})
    session['pages'] = page_list_dict

    return render_template(template_name_or_list='add_new_product.html',
                           page_list=page_list_dict)


@app.route('/fb_shop_add', methods=['GET', 'POST'])
def fb_shop_add():
    print('----------------------------------------------------------------')
    token = session.get('user_access_token')
    print('fb_shop_add access token: %s' % token)
    fb = Facebook(access_token=token)
    fb.refresh_token(token=token)
    data = request.form
    print('SELECTED PAGE: %s' % data.get('select-page'))
    page_id = session.get('pages')[str(data.get('select-page'))]

    for k in data:
        product_tpl[k] = data.get(k) or product_tpl[k]

    product_tpl['retailer_id'] = str(uuid.uuid4().hex)
    catalog_ids = fb.product_catalog_get_id_from_page_id(page_id=page_id,
                                                         page_access_token=token)
    print('Catalog id: %s' % catalog_ids)
    for i in catalog_ids:
        for k, v in i.items():
            if str(page_id) in k:
                catalog_id = v

                fb.catalog_adds_new_product(item_data=product_tpl,
                                            page_access_token=token,
                                            catalog_id=catalog_id)

                return "Add new product to facebook shop [%s] successfully!" % i


@app.route('/facebook/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    params = {'redirect_uri': redirect_uri,
              'scope': 'catalog_management, ads_management, pages_manage_posts, instagram_basic',
              'auth_type': 'reauthorize'}
    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(facebook.get_authorize_url(**params))
    return redirect(facebook.get_authorize_url(**params))


@app.route('/facebook/redirect')
def authorize_redirect():
    return redirect('http://localhost:5000/fb_shop/add_new_product_fb_shop')


@app.route('/facebook/authorized')
def authorized():
    # check to make sure the user authorized the request
    if 'code' not in request.args:
        flash('You did not authorize the request')
        return redirect(url_for('authorize_redirect'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized', _external=True)
    data = dict(code=request.args['code'], redirect_uri=redirect_uri)
    fb_session = facebook.get_auth_session(data=data,
                                           decoder=oauth_decode)

    fb = Facebook()
    access_token = fb.extend_expired_date_user_access_token(user_access_token=fb_session.access_token)
    print('====================================================================')
    print(fb_session.access_token)
    # the "me" response
    me = fb_session.get('me').json()
    print(me)

    session['name'] = me['name']
    session['id'] = str(me['id'])
    session['user_access_token'] = access_token

    return redirect(url_for('authorize_redirect'))


if __name__ == '__main__':
    app.run()

## How to use graph-api of facebook to create programmatically publishing app

- Create 1 page
- Create shop on that page
- Create app for developer
- Use https://developers.facebook.com/tools/explorer/ for generating access token, there are 3 types of access token. 
__Note__: if you want to use catalog managements, you must enable permissions.
- Get: _page id_, _app id_, _app secret_, _catalog id_ (id).
__Note__: use this link for getting more information https://graph.facebook.com/v8.0/me/adaccounts?access_token=ACCESS_TOKEN


_ **Important urls**: 
 - https://developers.facebook.com/docs/marketing-api/reference/product-catalog
 - https://github.com/facebook/facebook-python-business-sdk
 - https://developers.facebook.com/docs/marketing-api/catalog/reference/#da-commerce
 - https://developers.facebook.com/docs/graph-api/using-graph-api/v2.4#fields
 - https://developers.facebook.com/docs/facebook-login/web
 
 - https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
 - https://developers.facebook.com/docs/facebook-login/access-tokens/refreshing/#get-a-long-lived-user-access-token
 - https://developers.facebook.com/docs/pages/access-tokens/
 
## config.yaml
```python
config:
  access_token: xxxxxxxxxxxxxx
  page_id: xxxx
  app_id: xxx
  app_secret: xxxx
  catalog_id: xxxx
```

## Flask

- Declare the Flask object is mandatory, the object Flask is WSGI application (Web server Gateway Interface)

#### Routing
- Use the `route()` decorator (Exp: `app.route('/hello/')`)

#### Variable
- Use `<variable_name>` on router
Exp: 
```python
@app.route('/hello/<name>')
def hello_name(name):
   return 'Hello %s!' % name
```

- Direct routing: 

Exp:
```python
@app.route('/hello_name/<name>')
def hello(name):
    print(name)
    if name is None:
        return redirect(url_for('test_direct'))
    return redirect(url_for('hello_name', name=name))
```

__Note__: use `redirect` and `url_for`



Along with the provider’s log-in URL, you need to send some URL parameters that tell the provider who you are and what you want to do:

- __client_id__ This tells the OAuth2 provider what your app is. You’ll need to register your app ahead of time to get a client ID.
- __redirect_uri__ This tells the provider where you want to go when you’re done. For a website, this could be back to the main page; a native app could go to a page that closes the web view.
- __response_type__ This tells the provider what you want back. Normally, this value is either token, to indicate that you want an access token, or code, to indicate that you want an access code. Providers may also extend this value to provide other types of data.
- __scope__ This tells the provider what your app wants to access. This is how Google knows that Quora is asking for access to manage your contacts. Each provider has a different set of scopes.


__The important part is that, when the provider is done, they will redirect back to you and give you a token.__

link: https://www.smashingmagazine.com/2017/05/oauth2-logging-in-facebook/
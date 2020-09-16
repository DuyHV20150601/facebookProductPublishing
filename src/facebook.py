from facebook_business.adobjects.productcatalog import ProductCatalog
from facebook_business.api import FacebookAdsApi
import requests
from src.utils import load_config


class Facebook(object):

    def __init__(self, access_token=None):
        self.config = load_config('src/configs/configs.yaml')['config']
        self.graph_api_version = self.config['graph_api_version']
        self.__access_token = self.config['access_token'] if access_token is None else access_token
        self.__app_id = self.config['app_id']
        self.__app_secret = self.config['app_secret']
        self.__app_token = self.config['app_token']

    @property
    def current_access_token(self):
        return self.__access_token

    @current_access_token.setter
    def current_access_token(self, access_token):
        self.__access_token = access_token

    def product_catalog_get_id_from_page_id(self, page_id, page_access_token=None):
        """
        Get product catalog id from page id
        :param page_id: page id
        :param page_access_token: page access token
        :return: product catalog id
        """
        print('Start %s' % self.product_catalog_get_id_from_page_id.__name__)

        url = f'https://graph.facebook.com/{self.graph_api_version}/{str(page_id)}/product_catalogs'
        params = {'access_token': self.__access_token if page_access_token is None else page_access_token}
        resp = requests.request(method='GET',
                                url=url,
                                params=params).json()

        if 'data' in resp.keys() and len(resp['data']) != 0:
            return [{r['name']: r['id']} for r in resp['data']]

        return

    def get_catalog(self, page_access_token, catalog_id):
        """Get catalog id

        Args:
            page_access_token (str): page access token
            catalog_id (str): catalog id

        Returns:
            str: ProductCatalog object
        """
        FacebookAdsApi.init(app_id=self.__app_id,
                            app_secret=self.__app_secret,
                            access_token=page_access_token)
        return ProductCatalog(fbid=catalog_id)

    def catalog_adds_new_product(self, item_data, page_access_token, catalog_id):
        product_catalog = self.get_catalog(page_access_token=page_access_token,
                                           catalog_id=catalog_id)
        return product_catalog.create_product(fields=[],
                                              params=item_data)

    def catalog_gets_all_product(self, page_access_token, catalog_id):
        catalog = self.get_catalog(page_access_token=page_access_token,
                                   catalog_id=catalog_id)

        return catalog.get_products()

    def extend_expired_date_user_access_token(self, user_access_token):
        """Extend short lived fb user token to long live user token

        Args:
            user_access_token (str): user access token

        Returns:
            str: long live access token
        """
        url = f'https://graph.facebook.com/{self.graph_api_version}/oauth/access_token'
        params = {'grant_type': 'fb_exchange_token',
                  'client_id': self.__app_id,
                  'client_secret': self.__app_secret,
                  'fb_exchange_token': user_access_token}
        resp = requests.request(method='GET',
                                url=url,
                                params=params).json()

        return resp['access_token'] if 'access_token' in resp.keys() else None

    def extend_expired_date_page_access_token(self, page_access_token, user_id):
        """Extend short lived fb page token to long live user token

        Args:
            page_access_token (str): page access token
            user_id (str): user id

        Returns:
            str: long live access token
        """
        url = f'https://graph.facebook.com/{self.graph_api_version}/{user_id}/accounts'
        params = {
            'access_token': page_access_token
        }
        resp = requests.request(method='GET',
                                url=url,
                                params=params).json()

        return resp['access_token'] if 'access_token' in resp.keys() else None

    def refresh_token(self, token):
        """Refresh access token when it's out of date

        Args:
            token (str): access token

        Raises:
            e: Refrshing error

        Returns:
            str: refreshed token
        """
        print('Refreshing token....')
        checking_url = 'https://graph.facebook.com/debug_token'
        params = {
            'input_token': token,
            'access_token': self.__app_token
        }

        resp = requests.request(method='GET',
                                url=checking_url,
                                params=params).json()
        print('resp %s' % resp)
        try:
            expired_time = resp['data']['expires_at'] or ''
            if expired_time and expired_time > 6000 and resp['data']['is_valid'] is True:
                print("This token has so much time")
                return

            if resp['data']['expires_at'] == 0:
                print('This token is never expired')
                return

        except Exception as e:
            print('Refreshing token error: %s' % resp['error'])
            raise e

        # Get refreshing code
        refreshing_code_url = f'https://graph.facebook.com/{self.graph_api_version}/oauth/client_code'
        params = {'client_id': self.__app_id,
                  'client_secret': self.__app_secret,
                  'redirect_uri': 'https://www.facebook.com/connect/login_success.html',
                  'access_token': self.__app_token}
        refreshing_code_resp = requests.request(method='GET',
                                                url=refreshing_code_url,
                                                params=params)

        print('*************************************************************************************')
        print(refreshing_code_resp.url)
        refreshing_code_resp = refreshing_code_resp.json()
        print(refreshing_code_resp)

        if 'code' in refreshing_code_resp.keys():
            refreshing_code = refreshing_code_resp['code'] or ''

        else:
            raise Exception('ERROR: %s' % refreshing_code_resp['error'])

        if refreshing_code is not None and refreshing_code != '':
            refreshing_url = f'https://graph.facebook.com/{self.graph_api_version}/oauth/access_token'
            params = {'code': refreshing_code,
                      'client_id': self.__app_id,
                      'redirect_uri': 'https://www.facebook.com/connect/login_success.html',
                      'machine_id': 'test'}
            resp = requests.request(method='GET',
                                    url=refreshing_url,
                                    params=params).json()

            print('Finish refreshing access token!')

            return resp['access_token'] if 'access_token' in resp.keys() else None

        print('Cannot refresh access token')
        return

    def user_get_pages(self, user_id, access_token=None):
        """Get pages that user manages

        Args:
            user_id (str): user id
            access_token (id, optional): access token. Defaults to None.

        Returns:
            list: list of page
        """
        print('Start %s' % self.user_get_pages.__name__)
        url = f'https://graph.facebook.com/v8.0/{user_id}/accounts'
        params = {'access_token': self.__access_token if access_token is None else access_token}

        resp = requests.request(method='GET',
                                url=url,
                                params=params)
        print('%s : %s' % ('user_get_pages', resp.url))

        resp = resp.json()
        if 'data' in resp.keys():
            return resp['data']

        print('ERROR: %s' % resp['error'])
        return

    def get_page_access_tokens(self, page_id, user_access_token=None):
        """
        If you used a short-lived User access token, the Page access token is valid for only 1 hour.
        If you used a long-lived User access token, the Page access token has no expiration date.
        :return:
        """
        print('Start %s' % self.get_page_access_tokens.__name__)
        url = f'https://graph.facebook.com/{page_id}'
        params = {'fields': 'name, access_token',
                  'access_token': user_access_token}

        resp = requests.request(method='GET',
                                url=url,
                                params=params).json()

        return resp['access_token'] if 'access_token' in resp.keys() else resp

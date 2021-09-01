from .views import *

class UrlManager:

    def __init__(self, application,api_application, *args, **kwargs):
        self.api_url = '/api/v1/'
        ##### Applications Routs #####
        application.route(self.concatenation('auth/'), methods=["POST"])(login)

        ##### REST Applications Routs #####
        api_application.add_resource(UserControl, self.concatenation('users/'))
        api_application.add_resource(ProductsApi, self.concatenation('products/'))
        api_application.add_resource(ProductApi, self.concatenation('products/<id>/'))

    def concatenation(self, url):
        return self.api_url + url

    def __str__(self):
        return "UrlManager"

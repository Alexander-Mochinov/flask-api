import os
from flask import request, jsonify, abort
from flask_restful import Resource
from flask_restful_swagger import swagger
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity
from flask_jwt_extended import create_access_token


from api.models import User, Product, ProductUser
from api.models import upload_file



def login():
    """Return AUTH JWT Token for for interaction all method"""
    email = request.authorization.username
    user = User.query.filter(User.email == email).first()
    if user.check_password(str(request.authorization.password)):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


class CommonParametersProduct:
    """Общие параметры для классов, определяющий продукт"""

    def generate_product_to_json(self, product) -> jsonify:
        """Генерация продукта в dict"""
        return {
            'name' : product.name,
            'price': [str(x.amount) + ' ' +str(x.name) for x in product.price]
        }

        
class ProductsApi(CommonParametersProduct, Resource):
    """GET METHOD"""
    @swagger.operation(
    notes='Return all product in database',
    responseMessages=[
            {
                "code": 200,
                "message": "Return all product in database"
            },
        ]
    )
    @jwt_required()
    def get(self):
        page = request.args.get('page', 1)
        products = Product.query
        paginator = products.paginate(int(page), 10).items
        resource = {}
        for product in paginator:
            resource[product.id] = self.generate_product_to_json(product)
        
        return jsonify(resource)



    """POST METHOD"""
    @swagger.operation(
    notes='Create product. The product can only be created by the administrator, F.e (json): {\
        "name" : "Самокат",\
        "price" : [\
                {\
                    "name" : "usd",\
                    "amount": 200.0\
                },\
                {\
                    "name" : "rub",\
                    "amount": 14000.0\
                },\
                {\
                    "name" : "eur",\
                    "amount": 120\
                }\
            ]\
        }',
    responseMessages=[
            {
                "code": 201,
                "message": "Product was created."
            },
            { 
                'status' : 403,
                'message' : 'Forbidden'
            }
        ]
    )
    @jwt_required()
    def post(self):
        user = self.get_current_user()
        if user.is_admin:
            Product.create_product(request)
            return { 
                'status' : 201,
                'message' : 'Product was created.'
            }
        
        return { 
            'status' : 403,
            'message' : 'Forbidden'
        }



    def get_current_user(self):
        """ Get current user """
        current_user_email = get_jwt_identity()
        user = User.query.filter(User.email == current_user_email).first()
        return user


class ProductApi(CommonParametersProduct, Resource):

    """GET METHOD"""
    @swagger.operation(
    notes='Get product from id in url-address',
    responseMessages=[
            {
                "code": 200,
                "message": "Ok"
            },
            {
                "code": 404,
                "message": "Product not found !"
            },
        ]
    )
    @jwt_required()
    def get(self, id=None):
        page = request.args.get('page', 1)
        product = Product.query.filter_by(id=id).first()
        if not product:
            abort(404)
        resource = self.generate_product_to_json(product)
        return jsonify(resource)


    """PUT METHOD"""
    @swagger.operation(
    notes='PUT method for updating the product',
    responseMessages=[
            {
                "code": 204,
                "message": "Product was update"
            },
            { 
                'status' : 403,
                'message' : 'Forbidden'
            }
        ]
    )
    @jwt_required()
    def put(self, id=None):        
        user = self.get_current_user()
        if user.is_admin:
            product = Product.query.filter_by(id=id).first()
            product.edit_product(request)
            return { 
                'status' : 204,
                'message' : 'Product was update.'
            }
        
        return { 
            'status' : 403,
            'message' : 'Forbidden'
        }


    def get_current_user(self):
        """ Get current user """
        current_user_email = get_jwt_identity()
        user = User.query.filter(User.email == current_user_email).first()
        return user


class UserControl(Resource):
    __name__ = 'MainClass'

    """GET METHOD"""
    @swagger.operation(
    notes='Return personal list product.',
    responseMessages=[
            {
                "code": 200,
                "message": "Return personal list product."
            },
        ]
    )
    @jwt_required()
    def get(self):
        page = request.args.get('page', 1)
        vendor_code = request.args.get('vendor_code', '')
        user = self.get_current_user()
        paginator = ProductUser.get_product_list(user.id, vendor_code, page)
        resource = {}
        for product in paginator:
            resource[product[0].id] = self.generate_product_to_json(product)
        return jsonify(resource)

    """POTS METHOD"""
    @swagger.operation(
    notes='Add product in user list',
    responseMessages=[
            {
                "code": 200,
                "message": "Add product in list"
            },
            {
                "code": 404,
                "message": "Not found product"
            },
        ]
    )
    @jwt_required()
    def post(self):
        user = self.get_current_user()
        product_id = request.json.get('product_id', '')
        count_product = request.json.get('count_product', '')
        exists = ProductUser.exist_product(product_id)
        if exists:
            return ProductUser.create_product_list(user.id, product_id, count_product)
        else:
            abort(404)


    """PUT METHOD"""
    @swagger.operation(
    notes='Update profile method, ',
    responseMessages=[
            {
                "code": 204,
                "message": "Profile updated successfully"
            },
            {
                "code": 404,
                "message": "Profile not found"
            },
        ]
    )
    @jwt_required()
    def put(self):
        user = self.get_current_user()
        return user.edit_profile(request)


    """DELETE METHOD"""
    @swagger.operation(
    notes='Delete product from list',
    responseMessages=[
            {
                "code": 201,
                "message": "Delete product from list"
            },
        ]
    )
    @jwt_required()
    def delete(self):
        user = self.get_current_user()
        return ProductUser.delete_product_from_list(request, user)

    def get_current_user(self):
        """ Get current user """
        current_user_email = get_jwt_identity()
        user = User.query.filter(User.email == current_user_email).first()
        return user

    def generate_product_to_json(self, product) -> jsonify:
        """Generate product to dict """
        
        return {
            'name' : product[0].name,
            'price': [str(x.amount) + ' ' +str(x.name) for x in product[0].price],
            "vendor_code" : product[1]
        }
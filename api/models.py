from datetime import datetime
from api.api import db
from werkzeug.security import generate_password_hash, check_password_hash

from flask import request, jsonify
from api.setting import ConfigServise

from sqlalchemy import insert

from werkzeug.utils import secure_filename
import string
import random
import json, os

def generate_vendor_code(product_id,users_id):
    """Generator vendor code for product"""
    return str(product_id) + ':' + str(users_id) + (''.join(random.choices(string.ascii_uppercase + string.digits, k=5)))

def upload_file(request: request):
    """Upload file on server"""
    errors = {}
    success = False
    if 'photo' not in request.files:
        response = {
                "messege" : "No file part in the request",
                "success" : success,
                "status_code" : 400
            }
        return response
    file = request.files.get('photo', '')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(ConfigServise.UPLOAD_FOLDER, filename)
        file.save(path)
        success = True
    else:
        errors = {
            "messege" : "No file part in the request",
            "success" : success,
            "status_code" : 400
        }

    if success:
        response = {
            "message" : 'Files successfully uploaded',
            "filename" : file.filename,
            "success" : success,
            "status_code" : 201
        }
        return response

    else:
        response = {
            "messege" : "No file part in the request",
            "success" : success,
            "status_code" : 400
        }
        return response
    
def allowed_file(filename):
    """File permission check"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ConfigServise.ALLOWED_EXTENSIONS



class ProductUser(db.Model):
    __tablename__ = 'product_user'

    id = db.Column(db.Integer, primary_key=True)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    vendor_code = db.Column(db.String(12), unique = True)
    count_product = db.Column(db.Integer)

    @staticmethod
    def delete_product_from_list(request, user):
        """Delete product from list"""
        products_id = request.json.get('product_id', '')
        if products_id:
            db.session.delete(ProductUser.query.filter(ProductUser.id == products_id, ProductUser.users_id == user.id).first())
            db.session.commit()
            response =  jsonify(
                {
                    "message": "Product was delete in list product"
                }
            )
            response.status_code = 200
            return response
        else:
            response = jsonify({
                "message": "Not found product"
            })
            response.status_code = 404
            return response

    @staticmethod
    def get_product_list(user_id, vendor_code, page_number):
        """Return product list"""
        product = db.session.query(Product, ProductUser.vendor_code).join(ProductUser).filter(ProductUser.users_id == user_id)
        if vendor_code:
            product = product.filter(ProductUser.vendor_code == vendor_code)
        paginator = product.paginate(int(page_number), 10).items
        return paginator

    @staticmethod
    def exist_product(id):
        """Check exist product on database"""
        exist = db.session.query(Product.id).filter_by(id = id).first() is not None
        return exist

    @staticmethod
    def create_product_list(users_id, product_id, count_product):
        """Create priduct list for user"""
        product_list = ProductUser(users_id = users_id, product_id = product_id, count_product = count_product, vendor_code = generate_vendor_code(product_id,users_id))
        db.session.add(product_list)
        db.session.commit()
         
        response =  jsonify(
            {
                "message": "Add product in list"
            }
        )
        response.status_code = 201
        return response


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), primary_key=True, unique=True)
    login = db.Column(db.String(124))
    name = db.Column(db.String(80), default="User")
    sername = db.Column(db.String(80), default="User")
    patronymic = db.Column(db.String(80), default="User")
    password_hash = db.Column(db.String(128))
    datetime_joined = db.Column(db.DateTime, default=datetime.now())
    photo = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean)


    def __init__(self, *args, password,  **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.set_password(password)

    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(self, password):
        """Generate hash for password"""
        self.password_hash = generate_password_hash(str(password))

    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password_hash, password)

    def edit_profile(self, request):
        """Edit profile, parameters are passed from request"""
        try:
            name = request.form['name']
            file = request.files.get('photo', '')

            if name:
                self.name = name
            if file:
                upload_file(request)
                self.photo = file.filename

            db.session.commit()
            response = jsonify(
                {
                    "message" : f"Profile fields successfully update"
                }
            )
            response.status_code = 204
            return response
        except Exception as e:
            response = jsonify(
                {
                    "message" : "Server internal"
                }
            )
            response.status_code = 500
            return response
         
    def __str__(self):
        return str(self.id) + ':' +str(self.name)




product_price = db.Table(
    'product_price',
    db.Column('product_id', db.Integer(), db.ForeignKey('product.id')),
    db.Column('price_id', db.Integer(), db.ForeignKey('price.id'))
)

class Price(db.Model):
    __tablename__ = 'price'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    amount  = db.Column(db.Float())

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    photo = db.Column(db.String(255))
    price = db.relationship('Price', secondary=product_price, backref=db.backref('price', lazy='dynamic'))


    def edit_product(self, request):
        """Update data product"""
        file = upload_file(request)
        json_data = json.loads(str(request.form['json']))
        if file['success']:
            self.price.clear()
            self.name = json_data['name']
            self.photo = file['filename']
            for data in json_data['price']:
                price = Price(name = data['name'], amount = data['amount'])
                self.price.append(price)
                db.session.commit()

            response = jsonify(
                {
                    "message" : f"Products fields successfully update"
                }
            )
            response.status_code = 200
            return response

        response = jsonify(
            {
                "message" : "Server internal"
            }
        )
        response.status_code = 500
        return response
    
    @staticmethod
    def create_product(request):
        """Create product"""
        file = upload_file(request)
        json_data = json.loads(str(request.form['json'])) #json.loads(str(request.args.get('json')))
        if file['success']:
            product = Product(name = json_data['name'], photo = file['filename'])
            for data in json_data['price']:
                price = Price(name = data['name'], amount = data['amount'])
                product.price.append(price)
                db.session.add(product)
                db.session.commit()
            return True
        return False

def init_db():
    """Initialize database"""
    db.create_all()
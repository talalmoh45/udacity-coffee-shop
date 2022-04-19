from crypt import methods
import os
from xml.dom.pulldom import ErrorHandler
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    return response

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():

    drinks = Drink.query.all()

    formated_drinks=[drink.short() for drink in drinks]
    
    return jsonify({
        'success':True,
        'drinks':formated_drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = Drink.query.all()

    formated_drinks=[drink.long() for drink in drinks]

    return jsonify({
        'success':True,
        'drinks':formated_drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    body=request.get_json(force=True)

    if body:
        try:
            title=json.loads(request.data)['title']
            recipe=json.loads(request.data)['recipe']
            
            new_drink = Drink(title=title , recipe=json.dumps(recipe))
            Drink.insert(new_drink)

            return jsonify({
            'success':True,
            'drinks':[new_drink.long()]
            }),201
            

        except:
            abort(422)




'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id):
    body = request.get_json()
    drink=Drink.query.filter(Drink.id==id).one_or_none()

    if drink==None:
        abort(404)

    
    try:
        drink.title=body['title']
        drink.recipe=body['recipe']

        drink.update()

        return jsonify({
            'success':True,
            'drinks':[drink.long()]
        })

    except:
        abort(422)





'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(drink_id):
    drink = Drink.query.filter(Drink.id==drink_id).one_or_none()

    if not drink:
        abort(422)

    try:
        Drink.delete(drink)

        return jsonify({
            'success':True,
            'delete':drink_id
        })

    except:
        abort(404)




# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
        jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
            }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'resource not found'
    }),404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success':False,
        'error':'auth error',
        'message':'not allowed'
    })


    


if __name__ == "__main__":
    app.debug = True
    app.run()

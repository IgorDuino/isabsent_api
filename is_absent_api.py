import json

import flask
import logging
from flask import make_response

from data import db_session
from tools import request_data_validate
from data.student import Student
from data.teacher import Teacher


blueprint = flask.Blueprint(
    'sdo_parser_api',
    __name__,
)


@blueprint.route('/teacher', methods=['POST', 'PATCH'])
def teacher_post():
    try:
        request_json = flask.request.json
        request_data_validate.teacher_post_validate(request_json)

        db_sess = db_session.create_session()

        teacher = Teacher()
        for key, value in request_json.items():
            teacher[key] = value

        db_sess.add(teacher)

        db_sess.commit()
        return make_response('HTTP 200 OK', 200)
    except (ValueError, KeyError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)


@blueprint.route('/teacher/<int:teacher_id>', methods=['GET'])
def teacher_get(teacher_id):
    try:
        db_sess = db_session.create_session()
        teacher = db_sess.query(Teacher).get(teacher_id)

        if teacher is None:
            raise ValueError

        return make_response(json.dumps(
            {
                'teacher_name': teacher.name,
                'class_name': teacher.class_name
            }), 200)
    except (ValueError, KeyError) as error:
        logging.warning(error)
        return make_response('HTTP 400 Bad Request', 400)
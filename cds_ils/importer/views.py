import json
import os
import uuid
from threading import Thread

from flask import Blueprint, copy_current_request_context, flash, jsonify, \
    redirect, request, session
from invenio_app_ils.permissions import need_permissions
from werkzeug.utils import secure_filename

from cds_ils.importer.api import import_from_xml


def create_importer_blueprint(app):
    """Add importer views to the blueprint."""
    blueprint = Blueprint("invenio_app_ils_importer", __name__)

    def allowed_files(filename):
        """Checks the extension of the files."""
        if "." not in filename:
            return False

        ext = filename.rsplit(".", 1)[1]
        if ext.upper() in app.config["IMPORTER_ALLOWED_EXTENSIONS"]:
            return True
        else:
            return False

    def rename_file(filename):
        """Renames filename with an unique name."""
        unique_filename = uuid.uuid4().hex
        ext = filename.rsplit(".", 1)[1]
        return unique_filename + "." + ext

    class RequestError(Exception):
        """Custom exception class to be thrown when error occurs."""

        def __init__(self, message, status, payload=None):
            self.message = message
            self.status = status
            self.payload = payload

    @blueprint.errorhandler(RequestError)
    def handle_request_error(error):
        """Catch RequestError exception, serialize into JSON, and respond."""
        payload = dict(error.payload or ())
        payload['status'] = error.status
        payload['message'] = error.message
        return jsonify(payload), error.status

    @blueprint.route('/importer/check', methods=['GET'])
    @need_permissions("document-importer")
    def check():
        # TODO: Retrieve from DB instead the file
        file_name = '/tmp/my_file.json'
        file = open(file_name, 'r')
        json_object = json.load(file)
        return {"reports": json_object}

    @blueprint.route('/importer', methods=['POST'])
    @need_permissions("document-importer")
    def importer():

        @copy_current_request_context
        def process_data(file, source_type, provider):
            with open(app.config["IMPORTER_UPLOADS_PATH"] + "/"
                      + file.filename) as f:
                import_from_xml([f], source_type, provider)

        if request.files:
            file = request.files["file"]
            provider = request.form.get("provider", None)
            mode = request.form.get("mode", None)

            if not provider:
                flash('Missing provider')
                raise RequestError('Missing provider', 400)

            if not mode:
                flash('Missing mode')
                raise RequestError('Missing mode', 400)

            if allowed_files(file.filename):
                file.filename = rename_file(file.filename)
                if mode == 'Delete':
                    session['name'] = "Test"
                    return redirect(request.url)
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["IMPORTER_UPLOADS_PATH"],
                                       filename))
                t = Thread(target=process_data,
                           args=(file, "marcxml", provider))
                t.start()
                return json.dumps({'success': True}), 200,\
                       {'ContentType': 'application/json'}
            else:
                flash('That file extension is not allowed')
                raise RequestError('That file extension is not allowed', 400)
        else:
            raise RequestError('Missing file', 400)

    return blueprint

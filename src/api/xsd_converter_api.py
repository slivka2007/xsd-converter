# src/api/xsd_converter_api.py
import os
from datetime import datetime
from flask import Flask, request, render_template, Blueprint, jsonify
from xsd_converter import XSDConverter


def create_app(index_html: str = "index.html", test_config=None):
    """Application factory pattern for better testing and configuration."""
    app = Flask(__name__)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload
    )
    
    # Override with test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Register blueprints
    app.register_blueprint(create_converter_blueprint(index_html))
    app.register_blueprint(create_api_blueprint())
    
    return app


def create_converter_blueprint(index_html: str):
    """Create a blueprint for the converter functionality."""
    bp = Blueprint('converter', __name__, url_prefix='/')
    
    @bp.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "GET":
            return render_template(
                index_html, 
                max_occurs=1, 
                input_string="", 
                sample_string="",
                now=datetime.now()
            )
        else:
            try:
                # Generate sample XML and JSON files
                max_occurs = int(request.form.get("max_occurs", 1))
                input_string = str(request.form.get("schema_text", ""))
                sample_string = ""

                # Validate XML Schema
                if input_string.strip():
                    is_valid, error_message = XSDConverter.validate_schema(input_string)
                    if not is_valid:
                        return render_template(
                            index_html,
                            max_occurs=max_occurs,
                            input_string=input_string,
                            sample_string=f"Error: Invalid XML Schema\n\nDetails: {error_message}",
                            now=datetime.now()
                        )

                if str(request.form.get("xml", "")) == "XML":
                    sample_string = XSDConverter.generate_sample(
                        max_occurs, input_string, "xml"
                    )
                elif str(request.form.get("json", "")) == "JSON":
                    sample_string = XSDConverter.generate_sample(
                        max_occurs, input_string, "json"
                    )

                return render_template(
                    index_html,
                    max_occurs=max_occurs,
                    input_string=input_string,
                    sample_string=sample_string,
                    now=datetime.now()
                )
            except Exception as e:
                return render_template(
                    index_html,
                    max_occurs=int(request.form.get("max_occurs", 1)),
                    input_string=str(request.form.get("schema_text", "")),
                    sample_string=f"Error: {str(e)}",
                    now=datetime.now()
                )
    
    return bp


def create_api_blueprint():
    """Create a blueprint for the API endpoints."""
    bp = Blueprint('api', __name__, url_prefix='/api')
    
    @bp.route("/convert", methods=["POST"])
    def convert():
        try:
            data = request.json
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
                
            max_occurs = int(data.get("max_occurs", 1))
            schema_text = data.get("schema_text", "")
            output_format = data.get("output_format", "xml").lower()
            
            if not schema_text:
                return jsonify({"error": "No schema text provided"}), 400
                
            if output_format not in ["xml", "json"]:
                return jsonify({"error": "Invalid output format"}), 400

            # Validate the schema
            is_valid, error_message = XSDConverter.validate_schema(schema_text)
            if not is_valid:
                return jsonify({
                    "success": False,
                    "error": f"Invalid XML Schema: {error_message}"
                }), 400
                
            result = XSDConverter.generate_sample(max_occurs, schema_text, output_format)
            
            return jsonify({
                "success": True,
                "result": result
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    return bp
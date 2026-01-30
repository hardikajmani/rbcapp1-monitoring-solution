#!/usr/bin/env python3
"""
rbcapp1 REST API - Service Status Management
Accepts JSON payloads and stores them in Elasticsearch
Provides endpoints for querying service status
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Elasticsearch configuration
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch:9200")
logger.info(f"Elasticsearch host: {ES_HOST}")

es_client = None

# Supported services
SUPPORTED_SERVICES = ["httpd", "rabbitmq", "postgresql"]


def get_elasticsearch_client():
    """Get or create Elasticsearch client"""
    global es_client

    if es_client is None:
        try:
            es_url = f"http://{ES_HOST}" if "://" not in ES_HOST else ES_HOST
            logger.info(f"Connecting to Elasticsearch at: {es_url}")
            es_client = Elasticsearch([es_url])
            logger.info("Elasticsearch client created successfully")
        except Exception as e:
            logger.error(f"Failed to create Elasticsearch client: {str(e)}")
            es_client = None

    return es_client


def is_elasticsearch_healthy():
    """Check if Elasticsearch is healthy"""
    try:
        es = get_elasticsearch_client()
        if es is None:
            logger.error("Elasticsearch client is None")
            return False

        # Ping Elasticsearch
        if es.ping(request_timeout=5):
            logger.info("Elasticsearch is healthy")
            return True
        else:
            logger.warning("Elasticsearch ping returned False")
            return False
    except Exception as e:
        logger.error(f"Error checking Elasticsearch: {str(e)}")
        return False


def get_service_status_from_elasticsearch(service_name):
    """Retrieve the latest status for a service from Elasticsearch"""
    try:
        es = get_elasticsearch_client()
        if es is None:
            logger.error("Cannot query Elasticsearch: client is None")
            return None

        # Query for the latest status of the service
        index_name = f"rbcapp1-{service_name}"

        result = es.search(
            index=index_name, size=1, sort=[{"@timestamp": {"order": "desc"}}]
        )

        if result["hits"]["total"]["value"] > 0:
            hit = result["hits"]["hits"][0]["_source"]
            logger.info(
                f"Retrieved status for {service_name}: {hit.get('service_status', 'UNKNOWN')}"
            )
            return hit
        else:
            logger.warning(f"No status found for service: {service_name}")
            return None
    except Exception as e:
        logger.error(f"Error querying Elasticsearch for {service_name}: {str(e)}")
        return None


def get_all_services_status():
    """Retrieve the latest status for all services from Elasticsearch"""
    try:
        es = get_elasticsearch_client()
        if es is None:
            logger.error("Cannot query Elasticsearch: client is None")
            return None

        all_statuses = {}

        # get status for each supported service
        for service in SUPPORTED_SERVICES:
            index_name = f"rbcapp1-{service}"

            try:
                result = es.search(
                    index=index_name, size=1, sort=[{"@timestamp": {"order": "desc"}}]
                )

                if result["hits"]["total"]["value"] > 0:
                    hit = result["hits"]["hits"][0]["_source"]
                    all_statuses[service] = {
                        "status": hit.get("service_status", "UNKNOWN"),
                        "timestamp": hit.get("@timestamp", "N/A"),
                    }
                else:
                    all_statuses[service] = {"status": "NO_DATA", "timestamp": "N/A"}
            except Exception as e:
                logger.warning(f"Could not query {service}: {str(e)}")
                all_statuses[service] = {"status": "ERROR", "timestamp": "N/A"}

        return all_statuses
    except Exception as e:
        logger.error(f"Error querying all services: {str(e)}")
        return None


@app.route("/", methods=["GET"])
def index():
    """Root endpoint - API information"""
    logger.info(f"{request.method} {request.path}")
    return (
        jsonify(
            {
                "service": "rbcapp1-api",
                "version": "2.0",
                "description": "Service Status Management API",
                "endpoints": {
                    "/health": "GET - API health check",
                    "/healthcheck": "GET - Get all services status",
                    "/healthcheck/<service>": "GET - Get specific service status",
                    "/add": "POST - Add/Insert service status to Elasticsearch",
                },
                "supported_services": SUPPORTED_SERVICES,
            }
        ),
        200,
    )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint - Verifies Elasticsearch connectivity"""
    logger.info(f"{request.method} {request.path}")

    if is_elasticsearch_healthy():
        logger.info("Health status: HEALTHY")
        return jsonify({"status": "healthy"}), 200
    else:
        logger.warning("Health status: UNHEALTHY")
        return jsonify({"status": "unhealthy"}), 503


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    """
    GET /healthcheck - Returns all application statuses
    Returns: Dictionary with status for each service (UP, DOWN, UNKNOWN, NO_DATA)
    """
    logger.info(f"{request.method} {request.path}")

    # First check if Elasticsearch is healthy
    if not is_elasticsearch_healthy():
        logger.warning("Cannot retrieve statuses: Elasticsearch unavailable")
        return jsonify({"error": "Elasticsearch unavailable", "status": "UNKNOWN"}), 503

    # Get all services status
    all_statuses = get_all_services_status()

    if all_statuses is None:
        logger.error("Failed to retrieve services status")
        return (
            jsonify({"error": "Failed to retrieve services status", "status": "ERROR"}),
            500,
        )

    # Build response with all services
    response = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": all_statuses,
    }

    logger.info(f"Returning status for all services: {all_statuses}")
    return jsonify(response), 200


@app.route("/healthcheck/<service>", methods=["GET"])
def healthcheck_service(service):
    """
    GET /healthcheck/<service> - Returns specific service status
    Args: service - Service name (httpd, rabbitmq, postgresql)
    Returns: Service status (UP, DOWN, UNKNOWN, NO_DATA)
    """
    logger.info(f"{request.method} {request.path} - service: {service}")

    # Validate service name
    if service not in SUPPORTED_SERVICES:
        logger.warning(f"Unknown service requested: {service}")
        return (
            jsonify(
                {
                    "error": f"Unknown service: {service}",
                    "available_services": SUPPORTED_SERVICES,
                }
            ),
            400,
        )

    # Check if Elasticsearch is healthy
    if not is_elasticsearch_healthy():
        logger.warning(f"Cannot retrieve {service} status: Elasticsearch unavailable")
        return (
            jsonify(
                {
                    "service": service,
                    "status": "UNKNOWN",
                    "reason": "Elasticsearch unavailable",
                }
            ),
            503,
        )

    # Get service status from Elasticsearch
    service_status = get_service_status_from_elasticsearch(service)

    if service_status is None:
        logger.info(f"No data found for {service}")
        return (
            jsonify(
                {
                    "service": service,
                    "status": "NO_DATA",
                    "message": f"No status data found for {service}",
                }
            ),
            200,
        )

    response = {
        "service": service,
        "status": service_status.get("service_status", "UNKNOWN"),
        "host_name": service_status.get("host_name", "N/A"),
        "timestamp": service_status.get("@timestamp", "N/A"),
    }

    logger.info(f"Returning status for {service}: {response}")
    return jsonify(response), 200


@app.route("/add", methods=["POST"])
def add_status():
    """
    POST /add - Accept JSON payload and store in Elasticsearch
    Expected JSON format:
    {
        "service_name": "httpd",
        "service_status": "UP",
        "host_name": "host1"
    }
    """
    logger.info(f"{request.method} {request.path}")

    # Get JSON payload
    if not request.is_json:
        logger.error("Request is not JSON")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    logger.info(f"Received JSON: {data}")

    # Validate required fields
    required_fields = ["service_name", "service_status", "host_name"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
        return (
            jsonify(
                {
                    "error": f"Missing required fields: {missing_fields}",
                    "required_fields": required_fields,
                }
            ),
            400,
        )

    service_name = data.get("service_name")

    # Validate service name
    if service_name not in SUPPORTED_SERVICES:
        logger.error(f"Unknown service: {service_name}")
        return (
            jsonify(
                {
                    "error": f"Unknown service: {service_name}",
                    "supported_services": SUPPORTED_SERVICES,
                }
            ),
            400,
        )

    # Check if Elasticsearch is healthy
    if not is_elasticsearch_healthy():
        logger.error("Cannot insert status: Elasticsearch unavailable")
        return jsonify({"error": "Elasticsearch unavailable", "status": "FAILED"}), 503

    try:
        es = get_elasticsearch_client()

        # Add timestamp
        data["@timestamp"] = datetime.utcnow().isoformat() + "Z"
        data["timestamp"] = data["@timestamp"]

        # Create index name based on service
        index_name = f"rbcapp1-{service_name}"

        # Insert into Elasticsearch
        result = es.index(index=index_name, body=data)

        logger.info(
            f"Successfully inserted status for {service_name} into {index_name}"
        )
        logger.info(f"Elasticsearch response: {result}")

        return (
            jsonify(
                {
                    "message": f"Status for {service_name} successfully added to Elasticsearch",
                    "service": service_name,
                    "status": data.get("service_status"),
                    "host_name": data.get("host_name"),
                    "timestamp": data["@timestamp"],
                    "elasticsearch_id": result.get("_id"),
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Error inserting status into Elasticsearch: {str(e)}")
        return (
            jsonify(
                {"error": f"Failed to insert status: {str(e)}", "status": "FAILED"}
            ),
            500,
        )


@app.before_request
def log_request():
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.path}")


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {request.path} not found")
    return jsonify({"error": "Endpoint not found", "path": request.path}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error", "message": str(error)}), 500


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("rbcapp1 REST API starting")
    logger.info("=" * 60)

    # Test Elasticsearch connection on startup
    if is_elasticsearch_healthy():
        logger.info("✓ Elasticsearch connection verified at startup")
    else:
        logger.warning(
            "⚠ Elasticsearch not responding at startup (will retry on requests)"
        )

    # Start Flask app
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", 5000))

    logger.info(f"Starting Flask on {api_host}:{api_port}")

    app.run(
        host=api_host,
        port=api_port,
        debug=os.getenv("FLASK_ENV", "production") == "development",
    )

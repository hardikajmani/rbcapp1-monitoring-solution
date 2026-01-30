#!/usr/bin/env python3
import os, json, logging, sys, time
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("/var/log/rbcapp1")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "monitor.log"),
    ],
)

logger = logging.getLogger(__name__)


class ServiceMonitor:
    def __init__(self):
        self.output_dir = "/var/tmp/rbcapp1-status"
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Monitor initialized")
        self.service_status_config = {
            "httpd": "UP",
            "rabbitmq": "DOWN",  # Initially simulate failure
            "postgresql": "UP",
        }

    def get_service_status(self, service_name):
        return self.service_status_config.get(service_name, "UNKNOWN")

    def generate_status_json(self, service_name, status):
        timestamp = datetime.utcnow().isoformat() + "Z"
        payload = {
            "service_name": service_name,
            "service_status": status,
            "host_name": os.uname().nodename,
            "timestamp": timestamp,
            "@timestamp": timestamp,
        }

        filename = f"{service_name}-{status}-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(payload, f, indent=2)
        logger.info(f"Generated: {filename} -> {status}")

    def monitor_all_services(self):
        services = list(self.service_status_config.keys())
        for service in services:
            status = self.get_service_status(service)
            self.generate_status_json(service, status)
        logger.info("Monitor cycle complete")


def main():
    try:
        logger.info("=" * 60)
        logger.info("rbcapp1 Service Monitor started")
        logger.info("=" * 60)

        monitor = ServiceMonitor()
        cycle = 0

        while True:
            cycle += 1
            logger.info(f"Starting monitoring cycle #{cycle}")
            monitor.monitor_all_services()
            logger.info(f"Cycle #{cycle} complete. Waiting 60 seconds...")
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Monitor interrupted. Shutting down...")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

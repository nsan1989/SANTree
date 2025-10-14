import os
import time
import logging
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'san_tree.settings')
django.setup()

from san_srm.scheduler import start

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
log = logging.getLogger(__name__)

if __name__ == "__main__":
    log.info("starting scheduler...")
    start()
    log.info("scheduler started.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("stopping scheduler...")
        
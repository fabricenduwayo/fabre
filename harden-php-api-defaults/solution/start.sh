#!/bin/sh
# HarborDesk launcher: serve every request through the front controller.
cd /app/harbordesk || exit 1
exec php -S 127.0.0.1:8080 index.php

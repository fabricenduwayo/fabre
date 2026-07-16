#!/bin/sh
# HarborDesk staging launcher.
cd /app/harbordesk || exit 1
export PHP_CLI_SERVER_WORKERS="${PHP_CLI_SERVER_WORKERS:-4}"
exec php -S 127.0.0.1:8080 index.php

#!/bin/sh
cd /app/harbordesk || exit 1
export PHP_CLI_SERVER_WORKERS="${PHP_CLI_SERVER_WORKERS:-4}"
exec php -d expose_php=0 -d default_mimetype= -S 127.0.0.1:8080 index.php

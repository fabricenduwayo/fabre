#!/bin/sh
# HarborDesk staging launcher.
cd /app/harbordesk || exit 1
exec php -S 127.0.0.1:8080

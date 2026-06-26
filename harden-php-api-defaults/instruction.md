Our HarborDesk API lives in /app/harbordesk and still ships with the loose staging
defaults. It runs under PHP's built-in server (the launcher is
/app/harbordesk/start.sh) and writes an audit ledger to
/app/harbordesk/data/audit.db. Right now the launcher doesn't even route
requests properly, and the config is wide open. I need it locked down.

Get it into a state where the server actually serves /health and
/admin/bootstrap, and where the security holes are closed: no debug traces or
internal details leaking back in responses, and the admin bootstrap must require
the bootstrap secret in /app/harbordesk/data/bootstrap_secret and only succeed
once (a second bootstrap, or one without the right secret, has to be refused).

CORS needs to be limited to the internal origin (https://harbordesk.internal)
instead of a wildcard, and it has to work for credentialed requests from that
origin and only that origin (other origins should get no CORS grant at all).

The admin token that bootstrap writes must not be world-readable, and it must not
be stored in a directly reusable form: if someone reads the token file it
shouldn't hand them a working credential. /health should still return ok for a
request carrying the bootstrapped token as a bearer credential, and otherwise be
refused.

There's also something wrong with the audit ledger at
/app/harbordesk/data/audit.db: the API answers requests fine, but the attempts
aren't actually showing up in the ledger. Figure out why nothing is being
recorded and fix it so every bootstrap attempt and health check, accepted or
denied, lands in the ledger with the right decision. Keep the existing routes and
the request/response shape.

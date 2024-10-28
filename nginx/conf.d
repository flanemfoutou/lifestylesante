upstream web_app {
    server backend:8000;
}

server {
    listen 80;
    server_name lifestylesante.org;

    location ~/.well-known/acme-challenge {
        allow all;
        root /var/www/certbot;
    }

    return 301 https://$host:$request_uri;
}
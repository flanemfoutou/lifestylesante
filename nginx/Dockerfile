FROM nginx:alpine

# Copier le fichier de configuration Nginx
COPY default.conf /etc/nginx/default.conf

# Si tu utilises un certificat auto-signé, tu peux copier ici
COPY selfsigned.crt /etc/ssl/certs/selfsigned.crt
COPY selfsigned.key /etc/ssl/private/selfsigned.key

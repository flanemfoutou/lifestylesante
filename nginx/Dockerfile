FROM nginx:alpine

# Copier le fichier de configuration Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Si tu utilises un certificat auto-signé, tu peux copier ici
COPY selfsigned.crt /etc/ssl/certs/selfsigned.crt
COPY selfsigned.key /etc/ssl/private/selfsigned.key

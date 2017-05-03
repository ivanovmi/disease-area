# Останавливаем запущенные до этого контейнеры (если они есть)
docker-compose kill
# Удаляем эти контейнеры (если они есть)
docker-compose rm -f
# Собираем контейнеры заново
docker-compose build
# Запускаем контейнеры как сервис
docker-compose up -d

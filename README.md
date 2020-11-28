# Template for RSOI lab 2 Miroservices

## Сборка и запуск

```shell script
# Запуск PostgreSQL в контейнере
docker-compose up -d postgres
```

## Тестирование
Для проверки работоспособности системы используются скрипты Postman.
В папке [postman](postman) содержится [коллекция запросов](postman/postman-collection.json) к серверу и два enviroment'а:
* [local](postman/postman-local-environment.json);
* [heroku](postman/postman-heroku-environment.json).

Для автоматизированной проверки используется [GitHub Actions](.github/workflows/main.yml), CI/CD содержит шаги:
* сборка;
* деплой _каждого_ приложения на Heroku;
* прогон скриптов postman через newman для enviroment'а herkou.
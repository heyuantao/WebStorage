docker pull redis:5.0
docker run -d --name redis --network=host -v $PWD/docker/redis/redis.conf:/usr/local/etc/redis/redis.conf redis:5.0 redis-server /usr/local/etc/redis/redis.conf

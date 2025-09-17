pip install fastapi uvicorn wakeonlan python-dotenv

docker compose up -d --build

curl http://192.168.1.20/wake




docker buildx create --use
docker buildx inspect --bootstrap
docker buildx build --platform linux/amd64,linux/arm/v7 -t oreaba/wakeonlan:latest . --push




docker pull oreaba/wakeonlan:latest
docker run -d --name wol-api --env-file .env -p 80:80 oreaba/wakeonlan:latest


MAC_ADDRESS=34:5A:60:08:AB:D2
BROADCAST_IP=192.168.1.255
# RPLib

## Running frontend
### Production
USER=$(id -u) docker-compose up -d --build production

### Staging
USER=$(id -u) docker-compose up -d --build staging

### Development environments
USER=$(id -u) docker-compose up --build <service>

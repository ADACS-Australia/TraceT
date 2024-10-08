#!/bin/bash
docker-compose down

# Perform cleanup
docker volume rm $(docker volume ls -q)
docker volume prune -f
docker container prune -f
docker system prune -a -f

# Build and run Docker containers
docker-compose build
docker-compose up
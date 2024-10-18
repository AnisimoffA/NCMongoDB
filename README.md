lp - uvicorn src.main:app --reload --port 8000 --env-file .env.dev 
sm - uvicorn src.main:app --reload --port 8001 --env-file .env.dev      
dv - docker-compose -f docker-compose.dev.yml up --build
pd - docker-compose -f docker-compose.prod.yml up --build        
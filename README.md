# FastAPI JWT Authentication Service

1. Run the docker compose file:
```bash
docker compose up -d
```

2. Register a new user:
```bash
curl -X POST "http://localhost:8000/auth/register" -H "Content-Type: application/json" -d '{"username":"user","password":"testuser","email":"user@example.com","role":"user"}'
```

3. Goto http://localhost:3000 and login with user@example.com and testuser
```bash
curl -X POST "http://localhost:8000/auth/token" -H "Content-Type: application/x-www-form-urlencoded" --data-raw 'username=user&password=testuser'
```

4. Ask the question: I want to submit a new claim for my vehicle damage

5. To upload policy document

Here's the sequence of curl commands you'll need to upload the policy:

First, register an admin user:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "testadmin",
    "email": "admin@example.com",
    "role": "admin"
  }'
```

Then, get an access token:
```bash
curl -X POST "http://localhost:8000/auth/token" -H "Content-Type: application/x-www-form-urlencoded" --data-raw 'username=admin&password=testadmin'
```

Finally, upload the policy (replace $TOKEN with the token from step 2):
```bash
curl -X POST http://localhost:8000/admin/upload-policy \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/" \
  -F "policy_number=POL-2023-001" \
  -F "user_email=user@example.com" \
  -F "policyholder_name=Example user"
```

  ### Stop the docker containers
  ```bash
  docker compose down -v
  ```
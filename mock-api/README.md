## Getting Started

First, run the development server:

```bash
npm i

npm run start
# or
yarn start
# or
pnpm start
# or
bun start
```

Open [http://localhost:3001](http://localhost:3001) with your browser to see the result.

1. Submit a New Claim:
```bash
curl --location 'http://localhost:3001/insurance/claims' \
--header 'Content-Type: application/json' \
--data '{
    "policy_id": "000011",
    "damage_description": "test",
    "vehicle": "Alto",
    "photos": []
}'
```

2. Retrieve Claim Status:
```bash
curl --location 'http://localhost:3001/insurance/claims?claim_id=3whff3anr'
```

3. Calculate Insurance Premium:
```bash
curl --location 'http://localhost:3001/insurance/premium' \
--header 'Content-Type: application/json' \
--data '{
    "policy_id": "544555",
    "current_coverage": 100,
    "new_coverage": 500
}'
```

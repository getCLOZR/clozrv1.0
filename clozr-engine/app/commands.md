# CLOZR Engine — Commands

```bash
# activate virtual environment
source ../.venv/bin/activate
bash

# create / update database tables
python -m app.create_db
bash

# load sample / Shopify products
python -m app.load_sample_products
bash

# enrich products (attribute inference)
python -m app.enrich_all_products
bash

# run FastAPI server locally
uvicorn app.main:app --reload
bash

# generate product embeddings (when enabled)
python -m app.scripts.generate_embeddings
bash

# deploy (auto-deploys via Render)
git add .
git commit -m "message"
git push


---
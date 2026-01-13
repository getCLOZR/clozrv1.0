# CLOZR Engine Architecture

## Overview
CLOZR Engine is a FastAPI-based service that processes Shopify product data, generates AI-powered overviews, and provides chat functionality for product pages.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOZR-ENGINE (FastAPI)                    │
│                  https://clozrv1-0-tz8r.onrender.com         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         API Endpoints (main.py)        │
        ├───────────────────────────────────────┤
        │  GET  /health                          │
        │  POST /products/ingest                 │
        │  GET  /products/{id}/summary           │
        │  GET  /shopify/products/{id}/summary    │
        │  POST /shopify/products/chat           │
        └───────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│  Data Layer      │                  │  AI Services     │
│  (PostgreSQL)    │                  │  (OpenAI API)    │
├──────────────────┤                  ├──────────────────┤
│ • Merchants      │                  │ • Overview Gen   │
│ • ProductRaw     │                  │ • Chat Response  │
│ • Attributes     │                  │ • Questions Gen  │
│ • AI Overviews   │                  └──────────────────┘
└──────────────────┘                            │
        │                                       │
        └───────────────────┬───────────────────┘
                            ▼
                ┌───────────────────────┐
                │   Prompt System       │
                │   (prompts/)          │
                ├───────────────────────┤
                │ • overview_context.py │
                │ • render_overview_    │
                │   prompt.py           │
                └───────────────────────┘
```

## Directory Structure

```
clozr-engine/
├── app/
│   ├── main.py                    # FastAPI app & API endpoints
│   ├── models.py                  # SQLAlchemy database models
│   ├── schemas.py                 # Pydantic request/response models
│   ├── db.py                      # Database connection & session
│   ├── config.py                  # Configuration & settings
│   │
│   ├── services/
│   │   ├── product_services.py    # Product CRUD operations
│   │   ├── ai_overview_services.py # AI overview orchestration
│   │   └── openai_overview.py     # OpenAI API integration
│   │
│   ├── prompts/
│   │   ├── overview_context.py    # Prompt configuration/context
│   │   └── render_overview_prompt.py # Prompt rendering
│   │
│   ├── attributes.py              # Rule-based attribute extraction
│   ├── ingestion.py               # Product ingestion logic
│   └── create_db.py                # Database initialization
│
├── requirements.txt
└── README.md
```

## Data Flow

### 1. Product Ingestion Flow
```
Shopify Product JSON
    ↓
POST /products/ingest
    ↓
product_services.ingest_product()
    ↓
┌─────────────────────────┐
│ 1. Create/Get Merchant  │
│ 2. Store ProductRaw     │
│ 3. Extract Attributes   │ (attributes.py - rule-based)
│ 4. Store Attributes     │
└─────────────────────────┘
    ↓
PostgreSQL Database
```

### 2. Overview Generation Flow
```
GET /shopify/products/{id}/summary
    ↓
Fetch Product + Attributes from DB
    ↓
ai_overview_services.get_or_generate_ai_overview()
    ↓
┌─────────────────────────────────────┐
│ Check ProductAIOverview cache       │
│ If exists → return cached           │
│ If not → generate new               │
└─────────────────────────────────────┘
    ↓
openai_overview.generate_short_overview()
    ↓
┌─────────────────────────────────────┐
│ 1. Build product facts dict         │
│ 2. Render system prompt             │ (prompts/render_overview_prompt.py)
│ 3. Call OpenAI API                  │
│ 4. Store in ProductAIOverview       │
│ 5. Generate suggested questions     │
└─────────────────────────────────────┘
    ↓
Return {overview, suggested_questions}
```

### 3. Chat Flow
```
POST /shopify/products/chat
    ↓
Receive: {product_id, shop_domain, initial_overview, question}
    ↓
Fetch Product + Attributes from DB (for context)
    ↓
openai_overview.generate_chat_response()
    ↓
┌─────────────────────────────────────┐
│ 1. Build product context            │
│ 2. Create system prompt             │ (hardcoded in openai_overview.py)
│ 3. Build user message with:         │
│    - Product context                │
│    - Initial overview               │
│    - User question                  │
│ 4. Call OpenAI API                  │
└─────────────────────────────────────┘
    ↓
Return {response}
```

## Database Schema

### Tables

1. **merchants**
   - `id` (UUID, PK)
   - `shop_domain` (String, unique)
   - `created_at` (Timestamp)

2. **products_raw**
   - `id` (UUID, PK)
   - `merchant_id` (UUID, FK → merchants)
   - `shop_product_id` (String) - Shopify product ID
   - `raw_json` (JSON) - Full Shopify product data
   - `created_at`, `updated_at` (Timestamp)

3. **product_attributes**
   - `id` (UUID, PK)
   - `product_id` (UUID, FK → products_raw, unique)
   - `category`, `style`, `warmth_level`, `fit`, `material_main`, `price_band` (String)
   - `primary_use` (JSON array)
   - `extra_metadata` (JSON)
   - `created_at`, `updated_at` (Timestamp)

4. **product_ai_overviews**
   - `product_id` (UUID, PK, FK → products_raw)
   - `overview` (String) - AI-generated overview text
   - `model` (String) - OpenAI model used
   - `suggested_questions` (JSON array)
   - `updated_at` (Timestamp)

## Key Components

### 1. API Layer (`main.py`)
- FastAPI application
- CORS middleware for Shopify store access
- Endpoints for ingestion, overview, and chat

### 2. Data Models (`models.py`)
- SQLAlchemy ORM models
- Relationships: Merchant → ProductRaw → Attributes/AIOverview

### 3. Services Layer

#### `product_services.py`
- `ingest_product()` - Store product and extract attributes
- `get_product_with_attributes()` - Fetch product with attributes
- `build_product_sales_summary()` - Legacy summary builder (heuristic-based)

#### `ai_overview_services.py`
- `get_or_generate_ai_overview()` - Cache-aware overview generation
- Orchestrates overview + questions generation

#### `openai_overview.py`
- `generate_short_overview()` - Generate product overview paragraph
- `generate_chat_response()` - Generate chat responses
- `generate_suggested_questions()` - Generate suggested questions
- Uses OpenAI API with structured prompts

### 4. Prompt System (`prompts/`)

#### `overview_context.py`
- Configuration dictionary for overview prompts
- Contains: writing rules, focus order, tone, fallback behavior

#### `render_overview_prompt.py`
- Renders system prompt from context configuration
- Formats prompt with rules and guidelines

### 5. Attribute Extraction (`attributes.py`)
- Rule-based extraction (heuristics)
- Extracts: category, primary_use, warmth_level, etc.
- Used during product ingestion

## Current Prompt Contracts

### Overview Generation Prompt
**Location:** `prompts/overview_context.py` + `openai_overview.py`

**System Prompt Structure:**
```
You are CLOZR, an assistant that writes product page overview paragraphs.

Tone: clear, helpful, unbiased

Writing rules:
- Write for a customer, not a developer
- Assume the shopper can already see the product title, price, and images
- Do not restate obvious information...
- [12 more rules]

Focus order:
One non-obvious but useful insight → Why that insight matters

Fallback behavior:
- If a detail is missing, say 'Not specified'
- Do not guess materials, sizing, or compatibility
```

**User Message:**
```
FACTS:
{title, vendor, product_type, description, example_variant, inferred_attributes}

Write the overview.
```

### Chat Response Prompt
**Location:** `openai_overview.py` (hardcoded)

**System Prompt:**
```
You are CLOZR, a helpful product assistant for an ecommerce store.
Answer the customer's question about the product based on the provided context.
Be concise, helpful, and accurate. Use only the information provided.
If you don't know something, say so. Keep responses to 2-3 sentences max.
No emojis. Be professional and trustworthy.
```

**User Message:**
```
Product Context:
{title, vendor, product_type, tags, description, example_variant, inferred_attributes}

Initial Product Overview:
{initial_overview}

Customer Question: {question}

Answer the customer's question about this product.
```

### Suggested Questions Prompt
**Location:** `openai_overview.py` (hardcoded)

**System Prompt:**
```
You generate shopper questions for a product page.
Return ONLY a valid JSON array of exactly 2 strings, like:
["Question 1?", "Question 2?"]

Rules:
- Each question should be specific to the facts provided
- If a key detail is missing, ask about it rather than guessing.
- No bullets, no extra text, no markdown.
```

## Configuration

- **Database:** PostgreSQL (via `DATABASE_URL` env var)
- **OpenAI:** API key via `OPENAI_API_KEY` env var
- **Model:** `gpt-4o-mini` (configurable via `OPENAI_OVERVIEW_MODEL`)
- **CORS:** Allows all origins (should be restricted in production)

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/products/ingest` | Ingest product from Shopify |
| GET | `/shopify/products/{id}/summary` | Get AI overview + questions |
| POST | `/shopify/products/chat` | Chat about product |

## Next Steps for Prompt Improvement

1. **Centralize prompt configuration** - Move chat prompt to `prompts/` directory
2. **Version control prompts** - Add versioning system for prompt updates
3. **A/B testing support** - Structure for testing different prompt variations
4. **Context management** - Better handling of product context in prompts
5. **Error handling** - Improve fallback prompts and error responses


# CLOZR Shopify App

A minimal Shopify app for integrating CLOZR AI product overviews into Shopify stores.

## Project Structure

```
clozr-app/
├── server/                 # Python FastAPI backend
│   ├── main.py            # Main FastAPI application
│   ├── shopify_oauth.py   # OAuth helper functions
│   ├── routes/            # API routes
│   │   ├── install.py     # OAuth installation route
│   │   └── auth_callback.py  # OAuth callback handler
│   ├── utils/             # Utility functions
│   │   └── session_store.py  # Session/token storage
│   └── requirements.txt    # Python dependencies
│
├── frontend/              # React + Polaris frontend
│   ├── src/
│   │   ├── App.jsx        # Main app component
│   │   ├── index.jsx      # React entry point
│   │   └── components/
│   │       └── ToggleOverview.jsx  # Toggle component
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
│
└── extensions/            # Theme app extensions
    └── product-overview/
        ├── blocks/
        │   └── overview.liquid  # Liquid template block
        ├── assets/
        │   └── overview.js      # JavaScript for fetching overviews
        └── schema.json           # Extension schema
```

## Setup Instructions

### 1. Backend Setup

```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `server/` directory (copy from `.env.example`):
```bash
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret
SHOPIFY_REDIRECT_URI=http://localhost:3000/api/auth/callback
```

Run the server:
```bash
python main.py
# Or: uvicorn main:app --reload --port 3000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Shopify App Configuration

1. Create a Shopify app in your Partner Dashboard
2. Set the App URL to: `http://localhost:3000`
3. Set the Allowed redirection URL(s) to: `http://localhost:3000/api/auth/callback`
4. Copy your API Key and API Secret to the `.env` file

### 4. Installation Flow

1. Visit: `http://localhost:3000/api/install?shop=yourstore.myshopify.com`
2. Complete OAuth flow
3. App will redirect to embedded app

## Development Notes

- **OAuth Flow**: Basic OAuth implementation with nonce verification and HMAC validation
- **Token Storage**: Currently using in-memory storage. Replace with database in production.
- **Frontend**: React app with Shopify Polaris components, ready for App Bridge integration
- **Theme Extension**: Basic liquid block that injects a container for AI overviews

## Next Steps

- [ ] Add database for token storage
- [ ] Implement App Bridge authentication
- [ ] Connect to CLOZR Engine API
- [ ] Add settings persistence
- [ ] Deploy to production

## License

Proprietary - CLOZR


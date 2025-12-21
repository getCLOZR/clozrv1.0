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

## Development Workflow

### Prerequisites

1. Install Python dependencies:

```bash
cd server
pip install -r requirements.txt
```

2. Install Node dependencies:

```bash
cd frontend
npm install
```

3. Create a `.env` file in the `server/` directory:

```bash
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret
HOST=https://your-ngrok-url.ngrok-free.dev  # Or your deployment URL
SCOPES=read_products,write_products
```

### Running the App (4 Terminal Windows)

**Start terminals in this order: 1 → 3 → 2**

#### Terminal 1 - Backend (FastAPI) - Start First

```bash
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app
uvicorn server.main:app --reload --port 3000 --host 0.0.0.0
```

- Runs FastAPI server on port 3000
- `--host 0.0.0.0` allows external connections (needed for Shopify/ngrok)

#### Terminal 3 - Shopify CLI (Deploys Extensions) - Start Second

**Important: Start this after Terminal 1, before Terminal 2**

```bash
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app
shopify app dev --use-localhost
```

- **Required** for theme extensions to appear in theme editor
- Deploys and watches for extension changes
- Handles OAuth, tunneling, and extension deployment

#### Terminal 2 - Frontend (React/Vite) - Start Third

```bash
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app/frontend
npm run dev
```

- Runs Vite dev server (usually port 5173)
- Hot reload for frontend changes
- Can start anytime after Terminal 1 and 3

#### Terminal 4 - Ngrok (Only if needed)

```bash
ngrok http 127.0.0.1:3000
```

- Only needed if you require a public URL for testing
- Provides HTTPS tunnel to localhost:3000

### Installation & Setup

1. **Start terminals in this order**:
   - Terminal 1 (Backend) - start first
   - Terminal 3 (Shopify CLI) - start second (deploys extensions)
   - Terminal 2 (Frontend) - can start anytime
2. **Install the app**:
   - Visit: `http://localhost:3000/install?shop=yourstore.myshopify.com`
   - Or access via Shopify admin → Apps → Your app
   - Complete OAuth flow
3. **Add theme extension**:
   - Go to Shopify Admin → Online Store → Themes
   - Click "Customize" on your active theme
   - Navigate to a product page
   - Click "Add block" → Look for "CLOZR AI Overview"
   - Add the block to your product template

### Important Notes

- **Token Storage**: Currently in-memory only. If server restarts, you'll need to reinstall the app.
- **Extension Deployment**: Terminal 3 (`shopify app dev`) must be running for extensions to appear in theme editor.
- **Port 3000**: Backend must run on port 3000 for Shopify app configuration.

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

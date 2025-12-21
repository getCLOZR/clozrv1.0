# CLOZR Troubleshooting Guide

## Issue 1: Product Count Not Showing / 500 Errors

### Problem
- Dashboard doesn't show product count initially
- `/api/products` returns 500 errors intermittently
- After server restart, product count disappears

### Root Cause
Tokens are stored **in-memory** only. When the server restarts, all tokens are lost.

### Solution
1. **Reinstall the app** after server restarts:
   - Visit: `http://localhost:3000/install?shop=yourstore.myshopify.com`
   - Complete OAuth flow again
   - Token will be saved in memory

2. **Check terminal logs** for token status:
   - Look for `✅ Token saved for shop: ...` after installation
   - Look for `❌ No token found for shop: ...` if products fail

3. **Future fix**: Move to database storage (PostgreSQL/Redis) for persistence

### Quick Fix Workflow
```bash
# 1. Start server
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app
uvicorn server.main:app --reload --port 3000 --host 0.0.0.0

# 2. Reinstall app (if token missing)
# Visit: http://localhost:3000/install?shop=yourstore.myshopify.com

# 3. Check logs for token confirmation
```

---

## Issue 2: Theme Extension Not Showing in Theme Editor

### Problem
- CLOZR block doesn't appear in theme editor
- Can't add CLOZR AI Overview block to product pages

### Root Cause
Theme extensions need to be **deployed** to Shopify before they appear in the theme editor.

### Solution

#### Option 1: Using `shopify app dev` (Recommended for Development)
```bash
# Terminal 3 - Run this command
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app
shopify app dev --use-localhost
```

This command:
- Deploys the extension automatically
- Watches for changes and redeploys
- Makes the extension available in theme editor

#### Option 2: Manual Deployment
```bash
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app
shopify app deploy
```

### After Deployment

1. **Go to Shopify Admin** → Online Store → Themes
2. **Click "Customize"** on your active theme
3. **Navigate to a product page** in the theme editor
4. **Click "Add block"** or "Add section"
5. **Look for "CLOZR AI Overview"** in the block list
6. **Add the block** to your product template

### Verification
- Extension should appear in theme editor
- Block should be named "CLOZR AI Overview"
- Target: "section" (can be added to product pages)

---

## Complete Development Workflow

### Terminal 1: Backend
```bash
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app
uvicorn server.main:app --reload --port 3000 --host 0.0.0.0
```

### Terminal 2: Frontend
```bash
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app/frontend
npm run dev
```

### Terminal 3: Shopify CLI (Deploys Extensions)
```bash
cd ~/Desktop/CLOZR/clozrv1.0/clozr-app
shopify app dev --use-localhost
```

### Terminal 4: Ngrok (If needed)
```bash
ngrok http 127.0.0.1:3000
```

---

## Common Issues & Fixes

### "No access token" Error
- **Fix**: Reinstall app via `/install?shop=...`
- **Prevent**: Use database for token storage (future)

### Extension Not Appearing
- **Fix**: Run `shopify app dev` in Terminal 3
- **Check**: Extension is in `extensions/product-ai-overview/`
- **Verify**: `shopify.extension.toml` exists and is valid

### Product Count Shows Then Disappears
- **Cause**: Server restart cleared in-memory tokens
- **Fix**: Reinstall app after each server restart (until we add DB)

---

## Next Steps (Future Improvements)

1. **Persistent Token Storage**
   - Move from in-memory to PostgreSQL/Redis
   - Tokens survive server restarts

2. **Better Error Handling**
   - Show user-friendly messages in frontend
   - Auto-redirect to install if token missing

3. **Extension Auto-Deployment**
   - Ensure extension deploys on app install
   - Add extension deployment to OAuth callback


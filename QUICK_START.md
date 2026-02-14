# Quick Reference - Minifig Builder Frontend

## 🚀 Start Here

### 1. Configure Credentials (First Time Only)
```bash
# Copy example config
cp .env.example .env

# Edit with your BrickLink API credentials
# BRICKLINK_CONSUMER_KEY=xxx
# BRICKLINK_CONSUMER_SECRET=xxx
# BRICKLINK_TOKEN=xxx
# BRICKLINK_TOKEN_SECRET=xxx
```

### 2. Start Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
✅ Backend: `http://localhost:8000`
✅ API Docs: `http://localhost:8000/docs`

### 3. Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend: `http://localhost:3000`

## 📱 Frontend Pages

| Page | Purpose | Features |
|------|---------|----------|
| **Upload** 📤 | Upload inventory | Drag-drop XML upload |
| **Results** 📊 | View matches | Filter, search, details |
| **Cache** 💾 | Manage cache | Status, price updates |
| **Settings** ⚙️ | API config | Credential management |

## 🔌 API Reference

### Configuration
```js
api.checkConfig()          // Check if configured
api.setConfig(creds)       // Save credentials
```

### Analysis
```js
api.analyzeInventory(file) // Upload & analyze
api.getResults()           // Get latest results
```

### Cache
```js
api.getCacheStatus()       // Cache info
api.updatePrices()         // Update prices
```

### Search
```js
api.searchMinifigs(q, theme)  // Search minifigs
api.getThemes()               // Get themes
api.getStats()                // Overall stats
```

## 📂 File Locations

```
Frontend: frontend/src/
├── App.jsx           ← Main app logic
├── App pages
│  ├── pages/Upload.jsx
│  ├── pages/Results.jsx
│  ├── pages/CacheManager.jsx
│  └── pages/Settings.jsx
├── Reusable
│  ├── components/Header.jsx
│  ├── components/MinifigCard.jsx
│  └── api/client.js
└── Styles
   └── index.css

Backend: backend/
├── app.py              ← REST API (11 endpoints)
└── src/core/
   ├── cache_manager.py
   ├── inventory_parser.py
   └── minifig_finder.py
```

## 🔄 Typical Workflow

```
1. Settings (⚙️)
   └─→ Enter BrickLink API key

2. Cache Manager (💾)
   └─→ View minifigs in cache
       └─→ Update prices (optional)

3. Upload (📤)
   └─→ Upload inventory XML
       └─→ Click "Analyze"

4. Results (📊)
   └─→ See what you can build
       └─→ Filter by theme/quality
           └─→ View part details
```

## 💡 Tips

- **First use?** Run `python3 src/cache_valuable_minifigs.py --theme sw` to populate cache
- **Mobile friendly** - Full responsive design (test on phone!)
- **API docs** - Visit `/docs` for interactive Swagger UI
- **Hot reload** - Frontend auto-refreshes on code changes
- **Credentials safe** - All API keys stored server-side only

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 3000 in use | `lsof -ti:3000 \| xargs kill -9` |
| Port 8000 in use | Change `BACKEND_PORT` in `.env` |
| Credentials not work | Check `.env` file, restart backend |
| No cache data | Run `cache_valuable_minifigs.py` first |
| CORS error | Check backend is running on 8000 |
| npm install fails | Delete `node_modules`, retry |

## 📚 Full Docs

- **Setup Guide**: See [SETUP.md](SETUP.md)
- **Backend Docs**: See [backend/README.md](backend/README.md)
- **Frontend Docs**: See [frontend/README.md](frontend/README.md)
- **Full Summary**: See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **API Docs**: http://localhost:8000/docs (when running)

## ⚡ One-Command Start

```bash
bash start.sh
```
Auto-installs everything and starts both services!

---

**Happy building! 🧱**

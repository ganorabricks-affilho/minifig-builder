# Frontend - React Web Application

The web-based user interface for Minifig Builder.

## Features

- **Upload & Analyze** - Upload your BrickLink inventory XML and find buildable minifigures
- **View Results** - Browse complete and partial matches with detailed part information
- **Filter & Search** - Filter by theme, match percentage, and search by name/ID
- **Manage Cache** - Monitor cached minifigures and update prices
- **Secure Configuration** - Configure BrickLink API credentials safely

## Technology Stack

- **React** 18 - UI framework
- **Vite** - Build tool and dev server
- **Axios** - HTTP client for API calls
- **CSS3** - Modern responsive styling

## Project Structure

```
src/
├── App.jsx                    # Main application component
├── main.jsx                   # React entry point
├── index.css                  # Global styles
├── api/
│   └── client.js             # Axios API client
├── pages/
│   ├── Upload.jsx            # Inventory upload page
│   ├── Results.jsx           # Results viewing and filtering
│   ├── CacheManager.jsx      # Cache management
│   └── Settings.jsx          # API configuration
└── components/
    ├── Header.jsx            # Navigation header
    └── MinifigCard.jsx       # Minifigure display card
```

## Development

### Install Dependencies
```bash
npm install
```

### Start Dev Server
```bash
npm run dev
```

Server runs at `http://localhost:3000` with hot reload.

### Build for Production
```bash
npm run build
```

Creates optimized production build in `dist/`

### Preview Production Build
```bash
npm run preview
```

## API Integration

The frontend communicates with the FastAPI backend via REST API endpoints:

- **Config**: `/api/config/*` - Manage API credentials
- **Analysis**: `/api/analyze`, `/api/results` - Process and retrieve results
- **Cache**: `/api/cache/*` - Manage cached data
- **Search**: `/api/search`, `/api/themes` - Browse minifigures
- **Stats**: `/api/stats` - Get overall statistics

See [Vite Config](vite.config.js) for proxy settings to `/api` endpoints.

## Styling

- Custom CSS with CSS variables for theming
- Responsive grid layouts
- Mobile-optimized UI
- Accessibility considerations

## Environment Variables

Frontend can use:
```
VITE_API_URL=http://localhost:8000
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

# Frontend Documentation

## Overview

The frontend is a modern React + Vite application providing a user interface for the Power Disparity Predictor. It allows users to make real-time energy consumption predictions via an intuitive web interface.

## Tech Stack

- **React 19.2** - UI framework
- **Vite 6.2** - Build tool and dev server
- **TypeScript 5.8** - Static typing
- **React Router 7.13** - Client-side routing
- **CSS3** - Styling (modular CSS)

## Directory Structure

```
frontend/
├── src/
│   ├── App.tsx                  # Main app component
│   ├── index.tsx                # Entry point
│   ├── constants.tsx            # API endpoints and constants
│   ├── types.ts                 # TypeScript type definitions
│   ├── metadata.json            # App metadata
│   ├── components/              # Reusable components
│   │   └── *.tsx               # Individual components
│   └── pages/                   # Page components
│       └── *.tsx               # Individual pages
├── public/                      # Static assets
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
├── package.json                # Dependencies and scripts
├── index.html                  # HTML template
├── .env.local                  # Environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # Frontend README
```

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Server runs on `http://localhost:5173` with hot module replacement (HMR).

### Production Build

```bash
npm run build
```

Creates optimized `dist/` folder for deployment.

### Preview Built App

```bash
npm run preview
```

Serves the production build locally for testing.

## Configuration

### API Endpoint

Edit `src/constants.tsx`:

```typescript
export const API_BASE_URL = 'http://localhost:8001';
```

For production, point to your deployed backend:
```typescript
export const API_BASE_URL = 'https://api.yourdomain.com';
```

### Environment Variables

Create or edit `.env.local`:

```env
VITE_API_URL=http://localhost:8001
VITE_APP_NAME=Power Disparity Predictor
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```

## Features

### 1. Real-time Predictions
- Single prediction interface
- Input validation
- Real-time result display with confidence scores
- Risk level visualization

### 2. Batch Processing
- Process multiple predictions simultaneously
- JSON input support
- Results export functionality

### 3. Model Information
- Live model status monitoring
- Performance metrics display
- Feature information
- Model accuracy details

### 4. Appliance Management
- View all supported appliances
- Category filtering
- Appliance details and specs

### 5. API Documentation
- Interactive API reference
- Example requests/responses
- Endpoint descriptions

## Component Structure

### Main Components

- **App.tsx** - Root component with routing
- **Header** - Navigation and branding
- **PredictionForm** - Single prediction input
- **BatchPredictor** - Batch prediction interface
- **Results** - Result display component
- **ModelInfo** - Model metadata display
- **APIGuide** - API documentation

### Pages

- **Home** - Landing page
- **Predictor** - Prediction interface
- **Dashboard** - Model metrics and stats
- **Documentation** - API and usage docs

## API Integration

### Making Predictions

```typescript
const response = await fetch(`${API_BASE_URL}/predict`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    hour: 12,
    day_of_week: 3,
    appliance_id: 'fridge_207',
    appliance_category: 'kitchen',
    power_reading: 1000,
    power_max: 1500,
    power_std_12h: 100,
    power_mean_12h: 950,
    // ... other fields
  }),
});

const data = await response.json();
console.log(data); // { predicted_disparity_w: 125.45, confidence: 92.50, ... }
```

### Batch Predictions

```typescript
const response = await fetch(`${API_BASE_URL}/predict/batch`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    predictions: [
      { /* prediction 1 */ },
      { /* prediction 2 */ },
      // ... more predictions
    ],
  }),
});
```

### Getting Model Info

```typescript
const response = await fetch(`${API_BASE_URL}/model/info`);
const modelInfo = await response.json();
console.log(modelInfo);
// {
//   model_type: 'GradientBoostingRegressor',
//   accuracy: 96.74,
//   features: 15,
//   status: 'ready'
// }
```

## Styling

### CSS Organization

- **Global styles** in `index.css` or `App.css`
- **Component styles** in `*.module.css` for scoped styling
- **Responsive design** using CSS media queries
- **Tailwind CSS** (optional, if configured)

### Theme Colors

```typescript
const colors = {
  primary: '#667eea',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  dark: '#1a1a1a',
  light: '#f5f5f5',
};
```

## Performance Optimization

### Code Splitting

Routes are automatically code-split by Vite:

```typescript
import { lazy, Suspense } from 'react';

const PredictorPage = lazy(() => import('./pages/Predictor'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <PredictorPage />
    </Suspense>
  );
}
```

### Image Optimization

```typescript
// Use Vite's image imports for optimization
import logo from '/src/assets/logo.svg';
```

### Lazy Loading

```typescript
<img loading="lazy" src="image.png" alt="description" />
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 12+, Chrome Android

## Testing

### Unit Tests

```bash
npm install --save-dev vitest @testing-library/react
npm run test
```

### E2E Tests

```bash
npm install --save-dev playwright
npx playwright test
```

## Deployment

### Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod --dir dist
```

### Vercel

```bash
npm install -g vercel
vercel --prod
```

### Traditional Hosting

1. Build: `npm run build`
2. Upload `dist/` folder to web host
3. Configure web server to serve `index.html` for all routes

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

## Development Tips

### Hot Module Replacement (HMR)

Changes are instantly reflected in the browser during development.

### Debugging

- Use VS Code Debugger
- React DevTools browser extension
- Chrome DevTools Network tab for API debugging

### Console Logging

```typescript
console.log('Debug info:', variable);
console.error('Error:', error);
console.table(dataArray); // Pretty print arrays
```

### Network Tab

- Monitor API calls in Chrome DevTools > Network
- Check request/response payloads
- View status codes and timing

## Common Issues

### CORS Errors

**Error:** "Access to XMLHttpRequest blocked by CORS policy"

**Solution:** Backend must have CORS enabled (it does by default in `serve_model.py`)

### API Not Responding

**Check:**
1. Backend is running: `http://localhost:8001/health`
2. Correct API URL in `constants.tsx`
3. Browser console for detailed error message

### Build Size Too Large

**Optimize:**
```bash
npm run build -- --analyze
```

Remove unused dependencies:
```bash
npm prune
```

### Hot Reload Not Working

**Solution:**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Restart dev server
npm run dev
```

## Contributing

1. Create a feature branch: `git checkout -b feature/feature-name`
2. Make changes and test locally
3. Commit: `git commit -m "feat: add feature"`
4. Push: `git push origin feature/feature-name`
5. Create a Pull Request

## Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [React Router Guide](https://reactrouter.com)

## Support

For frontend issues or questions:
1. Check browser console (F12) for errors
2. Review API response in Network tab
3. Check backend is running and responding
4. Review NetworkError or CORS issues

## License

MIT License - See LICENSE file

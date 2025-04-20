# Chrome Extension with React, TypeScript, and TailwindCSS

A modern Chrome extension built using React, TypeScript, TailwindCSS, and Vite.

## Features

- Modern React with TypeScript
- TailwindCSS for styling
- Vite for fast development and building
- Chrome Extension Manifest V3

## Development

### Prerequisites

- Node.js (>= 18.x)
- npm (>= 9.x)
- ImageMagick (for icon generation)

### Setup

1. Clone the repository
2. Install dependencies

```bash
npm install
```

3. Generate icons (requires ImageMagick)

```bash
npm run icons
```

4. Start development server

```bash
npm run dev
```

### Building for Production

```bash
npm run build
```

This will create a `dist` folder with the compiled extension.

## Loading the Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in the top-right corner)
3. Click "Load unpacked" and select the `dist` folder from this project
4. The extension should now appear in your extensions list and toolbar

## Project Structure

- `src/` - Source files
  - `assets/` - Static assets like icons
  - `App.tsx` - Main application component
  - `Popup.tsx` - Popup UI component
  - `background.ts` - Background script
  - `main.tsx` - Entry point
- `manifest.json` - Extension manifest
- `index.html` - HTML template
- `vite.config.ts` - Vite configuration

## License

MIT

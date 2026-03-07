# Cook Recipe Importer

A web application for importing recipes from URLs using the `cook` tool. Built with FastAPI backend and Vue 3 frontend with Tailwind CSS (Solarized Light theme).

## Features

- 🔗 Import recipes from any URL
- 🎨 Beautiful Solarized Light theme
- ⚡ Real-time import status updates
- 🔄 Background job processing
- 📁 Automatic file naming and duplicate handling
- 🚀 Subpath deployment support
- 🧩 Extensible architecture for future features

## Technology Stack

**Backend:**
- FastAPI
- Python 3.8+
- Pydantic for data validation
- BackgroundTasks for async job processing

**Frontend:**
- Vue 3 (Composition API)
- Vue Router
- Vite
- Tailwind CSS
- Axios

## Project Structure

```
cook-import-server/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── import_routes.py      # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── job.py                # Data models
│   ├── services/
│   │   ├── __init__.py
│   │   └── import_service.py     # Business logic
│   ├── main.py                   # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── import/
│   │   │       └── ImportForm.vue
│   │   ├── composables/
│   │   │   ├── useApi.js
│   │   │   └── useImport.js
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── views/
│   │   │   └── ImportView.vue
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── recipes/
│   └── import/                   # Imported recipes saved here
├── cook-toy                      # Mock cook tool for testing
└── .env.example
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

1. **Create a virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp ../.env.example ../.env
   # Edit .env if needed (optional for development)
   ```

4. **Run the backend:**
   ```bash
   # From the backend directory
   python -m backend.main
   
   # Or use uvicorn directly
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 7395
   ```

   The API will be available at `http://localhost:7395`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment variables (optional):**
   ```bash
   cp .env.example .env
   # Edit .env if deploying to a subpath
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

### Testing with cook-toy

The project includes a mock `cook-toy` script for testing without the actual cook tool:

```bash
# Make it executable (already done)
chmod +x cook-toy

# Test it directly
./cook-toy import "https://example.com/chocolate-cake"
```

The mock generates dynamic recipe titles from URLs:
- From URL fragment: `https://example.com#chocolate-cake` → "Chocolate Cake"
- From path segment: `https://example.com/recipes/apple-pie` → "Apple Pie"

## Usage

1. Open the frontend at `http://localhost:3000`
2. Enter a recipe URL in the input field
3. Click "Import Recipe"
4. Wait for the import to complete
5. The recipe will be saved to `recipes/import/` with a `.cook` extension

## API Endpoints

### POST /api/import
Create a new import job.

**Request:**
```json
{
  "url": "https://example.com/recipe"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "pending"
}
```

### GET /api/import/{job_id}
Get the status of an import job.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "url": "https://example.com/recipe",
  "filename": "recipe-name.cook"
}
```

Status values: `pending`, `processing`, `completed`, `failed`

### GET /api/health
Health check endpoint.

## Configuration

### Environment Variables

**Backend (.env):**
```bash
BASE_PATH=           # Subpath for deployment (e.g., /import)
COOK_PATH=cook-toy   # Path to cook executable
RECIPES_DIR=../recipes/import  # Directory for saved recipes
```

**Frontend (.env):**
```bash
VITE_BASE_PATH=      # Must match backend BASE_PATH
```

### Subpath Deployment

To deploy under a subpath (e.g., `/import`):

1. Set `BASE_PATH=/import` in backend `.env`
2. Set `VITE_BASE_PATH=/import` in frontend `.env`
3. Configure your reverse proxy to route the subpath to the application

Example nginx configuration:
```nginx
location /import/ {
    proxy_pass http://localhost:8000/;
}

location /import {
    proxy_pass http://localhost:3000;
}
```

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
python -m backend.main
```

The API includes auto-reload for development.

### Frontend Development

```bash
cd frontend
npm run dev
```

Vite provides hot module replacement for instant updates.

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`.

## Future Extensibility

The application is designed to support additional features:

- **Manual Recipe Entry**: Add a new route and view for manual input
- **File Management**: Browse and manage imported recipes
- **Content Display**: View recipe content in the browser
- **Recipe Editing**: Edit imported recipes

To add new features:
1. Add new routes in `frontend/src/router/index.js`
2. Create new view components in `frontend/src/views/`
3. Add corresponding API endpoints in `backend/api/`
4. Implement business logic in `backend/services/`

## Production Deployment

**Key Features:**
- Backend serves both API and compiled frontend static files
- Single process to manage with supervisord
- Supports subpath deployment (e.g., `/import`)
- Includes deployment scripts and configuration templates

**Quick Production Setup:**
```bash
# Build frontend
cd frontend && npm run build

# Start backend (serves both API and static files)
cd .. && python -m backend.main
```

The backend will automatically serve the compiled frontend from `frontend/dist/` if it exists.

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.8+)
- Verify virtual environment is activated
- Check if port 7395 is available

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and run `npm install` again
- Check if port 3000 is available

**Import fails:**
- Verify `cook-toy` is executable: `chmod +x cook-toy`
- Check `recipes/import/` directory exists and is writable
- Review backend logs for error messages

## License

MIT

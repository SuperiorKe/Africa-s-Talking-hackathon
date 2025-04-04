# Supabase Database Interface

A simple web interface for performing CRUD operations on a Supabase database table.

## Features

- View all records in a clean, responsive interface
- Add new records with name and email
- Edit existing records
- Delete records
- Real-time updates when data changes

## Setup

1. Install required Python packages:
   ```bash
   pip install flask python-dotenv
   ```

2. Create a `.env` file in the project root with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_api_key
   ```

3. Make sure you have a table named 'users' in your Supabase database with columns:
   - id (uuid, primary key)
   - name (text)
   - email (text)

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

- `app.py` - Flask backend with API routes
- `static/`
  - `index.html` - Main web interface
  - `styles.css` - CSS styling
  - `script.js` - Frontend JavaScript code
- `supabase_client.py` - Supabase client configuration

## API Endpoints

- GET `/api/records` - Fetch all records
- POST `/api/records` - Create new record
- PUT `/api/records/<id>` - Update existing record
- DELETE `/api/records/<id>` - Delete record

## Technologies Used

- Backend: Python / Flask
- Database: Supabase
- Frontend: HTML, CSS, JavaScript
- CSS Framework: Custom responsive design

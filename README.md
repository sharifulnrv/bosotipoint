# Bosoti Point Landing Page

This is a dynamic landing page application built with Flask. The application features a robust admin dashboard that allows for complete control over the site's content, including the Hero section, Features, Payment Plan, Footer, Booking options, and third-party tracking scripts.

## Requirements

- Python 3.8+
- Flask and other dependencies (see `requirements.txt` if available)

## Running the Application

1. Open a terminal and navigate to the project directory:
   ```bash
   cd path/to/bosotipoint
   ```
2. Start the Flask application:
   ```bash
   python app.py
   ```
3. The application will be accessible at http://localhost:8000.

## Admin Dashboard

The admin dashboard provides a complete no-code solution to manage the landing page content.

### Accessing the Dashboard

- **URL:** http://localhost:8000/admin
- **Username:** `admin`
- **Password:** `bosoti2026`

### Features

- **Live Content Editing**: Update site text, features, payment timelines, and footer details.
- **Media Management**: Upload, optimize, and manage site images using the built-in Image Manager.
- **Tracking & Analytics**: Easily inject and manage Meta (Facebook) Pixel, Google Analytics (GA4), Google Tag Manager (GTM), and TikTok Pixel directly from the UI without modifying any code.
- **Global Settings**: Control SEO metadata, contact numbers (WhatsApp/Phone), and admin credentials.

## Deploying / Updating on Server

If you are running the application on a production server (e.g., using Gunicorn and systemd), follow these steps to apply new code updates and database changes:

1. **Activate your virtual environment and run the `init_db` function** to create any new database tables:
   ```bash
   cd ~/bosotipoint
   source venv/bin/activate
   python -c "from app import init_db; init_db()"
   ```

2. **Restart the Gunicorn service** to apply the code changes:
   ```bash
   sudo systemctl restart bosotipoint
   ```
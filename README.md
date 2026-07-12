# Child Dev

## Quick start

### Backend
1. Create and activate a virtual environment.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure PostgreSQL is installed and running.
4. Create a database named `childdev_db`.
5. Create a `.env` file from [.env.example](.env.example) and set the PostgreSQL values.
6. Run database migrations:
   ```bash
   python manage.py migrate
   ```
7. Start the Django server:
   ```bash
   python manage.py runserver
   ```

### Flutter app
1. Open the mobile folder.
2. Install Flutter dependencies:
   ```bash
   cd mobile
   flutter pub get
   ```
3. Run the app:
   ```bash
   flutter run -d chrome
   ```

### API base URL
The Flutter app uses the Django API at:
- `http://10.0.2.2:8000/api` for Android emulators
- `http://localhost:8000/api` for web/local testing

If you need to point to a different backend, update the base URL in [mobile/lib/core/api_client.dart](mobile/lib/core/api_client.dart).

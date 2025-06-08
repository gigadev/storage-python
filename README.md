# Home Storage Product Tracker

A Flask web application to track home storage products, with Google SSO authentication and MongoDB backend.

---

## Features

- **Google SSO** authentication
- **CRUD** for storage locations and items
- Modern, responsive UI with **dark/light mode**
- MongoDB backend

---

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/storage-python.git
cd storage-python
```

### 2. Set Up Python Environment

```sh
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### 3. Set Up MongoDB

#### Local MongoDB

- [Download and install MongoDB Community Edition](https://www.mongodb.com/try/download/community)
- Start MongoDB server:
  ```sh
  mongod
  ```
- (Optional) Create database and collections:
  ```sh
  mongo
  use home_storage
  db.createCollection("locations")
  db.createCollection("storage_items")
  ```

#### MongoDB Atlas (Cloud)

- [Sign up for MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Create a cluster and database named `home_storage`
- Whitelist your IP and create a database user
- Copy the connection string and update your `.env` file

### 4. Set Up Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create/select a project.
3. Navigate to **APIs & Services > Credentials**.
4. Click **Create Credentials > OAuth client ID**.
5. Configure the consent screen if prompted.
6. Choose **Web application**.
7. Add the following to **Authorized redirect URIs**:
   ```
   http://localhost:5000/login/authorized
   ```
8. Click **Create** and copy your **Client ID** and **Client Secret**.

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```properties
SECRET_KEY=your_secret_key_here
MONGO_URI=mongodb://localhost:27017/home_storage
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 6. Run the Application

```sh
flask run
```
or
```sh
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## Usage

- **Login** with Google SSO
- **Manage Locations:** Add, view, edit, delete storage locations
- **Manage Storage Items:** Add, view, edit, delete items with details (brand, size, nutrition, etc.)
- **Switch between dark and light mode** in the UI

---

## Deployment

- Update `MONGO_URI` and Google OAuth redirect URIs for your production domain.
- Set secure values for all secrets in your production environment.

---

## License

MIT License

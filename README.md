# Videoflix Backend Project

Videoflix is a Django/DRF-Backend application for streaming video inspired by Netflix. Uploaded videos are automatically transcoded to 480p/720p/1080p and delivered as HLS (M3U8 + segments). Authentication uses JWT stored in HttpOnly cookies, and heavy work runs asynchronously via Redis/RQ.

## Features
- User authentication with JWT Token
- Email-based account activation
- Password reset via email with secure token
- Video transcoding to multiple resolutions (480p, 720p, 1080p)
- Generation of HLS (M3U8 + segments) per resolution
- Automatic deletion of old source files, thumbnails, and HLS folders during updates/deletions


## Technology Stack
- Language: Python
- Framework: Django, Django REST Framework
- Auth: djangorestframework-simplejwt (JWT) mit HttpOnly Cookies
- Database: PostgreSQL
- Background Jobs: Redis + RQ (django-rq)
- Video Processing: FFmpeg (Transcoding & HLS)
- Static Files: WhiteNoise
- Containerization: Docker (Compose)
- Deployment: Gunicorn
- Testing: pytest, coverage.py
- Config: python-dotenv (.env)


## Backend-Setup Introduction

### Prerequisites
- Python (3.10+ recommended) and pip

- ffmpeg installed and on your PATH <br> 
   Check: ffmpeg -version

- Docker Desktop

### Setup

1. **Clone the repository and navigate to this folder in your editor e.g Visual Studio Code**
```bash
git clone https://github.com/Fabian-85/videoflix.git
cd videoflix
```

2. **Configure .env**
```bash
cp .env.template .env # edit the .env file
# in windows: copy .env.template .env
```

3. **Start the backend server (Docker must be open)**
```bash
docker-compose up --build
```
---


## API Endpoints

### Authentication

  <details>
  <summary><strong>POST</strong> <code>/api/register/</code></summary>
  
  **Description:**
  Register a new user in the system. After successful registration, an activation email will be sent. The response, including the token, has no use in the front end, as we work with HTTP-ONLY COOKIES here. This is only for demonstration and information.

  **Request Body:**
  
  ```json
  {
  "email": "user@example.com",
  "password": "securepassword",
  "confirmed_password": "securepassword"
  }
  ```
  </details>

  <details>
  <summary><strong>GET</strong> <code>/api/activate/&lt;uidb64&gt;/&lt;token&gt;/</code></summary>

  **Description:**
  Activates the user account using the token sent by email. 

  **Request Body:**
  
  ```json
  {}
  ```
  </details>

  <details>
  <summary><strong>POST</strong> <code>/api/login/</code></summary>

  **Description:**
  Authenticates the user and returns JWT tokens. The Response has no use in frontend as we work with HTTP-ONLY COOKIES.
   
  **Request Body:**
  
  ```json
  {
  "email": "your_email",
  "password": "your_password"
  }
  ```
  </details>

  <details>
  <summary><strong>POST</strong> <code>/api/logout/</code></summary>
  
  **Description:**
  Log the user out and delete token from cookies. Blacklist the refresh-token.
   
  **Request Body:**
  
  ```json
  {}
  ```  
  <details>
  <summary><strong>POST</strong> <code>/api/token/refresh/</code></summary>

  **Description:**
  Issues a new access token when the old access token has expired. 
   
  **Request Body**
  
  ```json
  {}
  ```
  </details>
 
  </details>

  <details>
  <summary><strong>POST</strong> <code>/api/password_reset/</code></summary>

  **Description:**
  Sends a link to reset the password to the user's email address.
   
  **Request Body**
  
  ```json
  {
    "email":"your_email"
  }
  ```
  </details>

 <details>
  <summary><strong>POST</strong> <code>/api/password_confirm/&lt;uidb64&gt;/&lt;token&gt;/</code></summary>

  **Description:**
  Confirm the password change with the token included in the email.
   
  **Request Body**
  
  ```json
  {
  "new_password": "new_password",
  "confirm_password": "new_password"
  }
  ```
  </details>
 

### Video Management

<details>
  <summary><strong>GET</strong> <code>/api/video/</code></summary>

  **Description:**
  Returns a list of all available videos.
   
  **Request Body:**
  
  ```json
  {}
  ```
</details>

<details>
  <summary><strong>GET</strong> <code>/api/video/&lt;int:movie_id&gt;/&lt;str:resolution&gt;/index.m3u8</code></summary>

  **Description:**
   Returns the HLS master playlist for a specific movie and selected resolution.
   
  **Request Body:**
  
  ```json
  {}
  ```
</details>
 
<details>
  <summary><strong>GET</strong> <code>/api/video/&lt;int:movie_id&gt;/&lt;str:resolution&gt;/&lt;str:segment&gt;/</code></summary>

  **Description:**
  Returns a single HLS video segment for a specific movie in the selected resolution.
   
  **Request Body:**
  
  ```json
  {}
  ```
</details>
 

  
## Frontend-Setup

1. Open the frontend quizly project in a editor e.g. Visual Studio Code
2. Right-click on the file `index.html` at the top level and select Open with  **Open with Live Server** to start the project.
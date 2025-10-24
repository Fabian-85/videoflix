# Videoflix Backend Project

Videoflix is a video streaming plattform.

## Features
- User authentication with JWT Token


## Technology Stack
- Django, Django REST Framework
- Authentication JWT (JSON Web Token) and HTTP-Only-COOKIES
- Database: PostgreSQL


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

2. **Start the backend server (Docker must be open)**
```bash
docker-compose up --build
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
  <summary><strong>GET</strong> <code>/api/activate/<uidb64>/<token>/</code></summary>

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
  <summary><strong>POST</strong> <code>/api/password_confirm/<uidb64>/<token>/</code></summary>

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
  <summary><strong>GET</strong> <code>/api/video/<int:movie_id>/<str:resolution>/index.m3u8</code></summary>

  **Description:**
   Returns the HLS master playlist for a specific movie and selected resolution.
   
  **Request Body:**
  
  ```json
  {}
  ```
</details>
 
<details>
  <summary><strong>GET</strong> <code>/api/video/<int:movie_id>/<str:resolution>/index.m3u8</code></summary>

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
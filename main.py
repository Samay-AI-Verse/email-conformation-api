import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr, ConfigDict  # <-- THE FIX IS HERE
from pydantic_settings import BaseSettings
from starlette.middleware.cors import CORSMiddleware
import os

# 1. Model to validate incoming form data
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

# 2. Settings class to load credentials from .env
# Get the absolute path to the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build the full path to the .env file
ENV_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    # This is the new Pydantic V2 way to specify configuration
    model_config = ConfigDict(
        env_file=ENV_PATH,  # Use the absolute path
        extra='ignore'      # Ignores any extra fields
    )
    
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str

# Load settings
settings = Settings()

# 3. FastAPI-Mail configuration
conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = False, # Set to False for Port 465
    MAIL_SSL_TLS = True,   # Set to True for Port 465
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

app = FastAPI()

# 4. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# 5. The email-sending endpoint
@app.post("/send-email")
async def send_email(form_data: ContactForm):
    
    # This is the email you want to send *to*
    admin_email = "teamsamayai01@gmail.com" 

    # Prepare the message with HTML line breaks
    message_with_breaks = form_data.message.replace("\n", "<br>")
    
    # Now, use that new, clean variable inside the f-string.
    html_content = f"""
    <html>
    <body>
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> {form_data.name}</p>
        <p><strong>Email:</strong> <a href="mailto:{form_data.email}">{form_data.email}</a></p>
        <hr>
        <p><strong>Message:</strong></p>
        <p>{message_with_breaks}</p>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=f"New Website Message from {form_data.name}",
        recipients=[admin_email],  # The person who receives the email
        body=html_content,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        print(f"Error sending email: {e}") # Print error to server console
        raise HTTPException(status_code=500, detail="Failed to send email.")

# 6. Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)






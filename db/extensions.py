from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialize extensions without app binding
db = SQLAlchemy()
bcrypt = Bcrypt()
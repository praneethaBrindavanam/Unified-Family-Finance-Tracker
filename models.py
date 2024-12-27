from flask_sqlalchemy import SQLAlchemy
import enum
from datetime import datetime

db=SQLAlchemy()
class Budget(db.Model):
    __tablename__="budgets"
    budget_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    category_id=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,nullable=False)
    limit=db.Column(db.DECIMAL)
    start_date=db.Column(db.Date)
    end_date=db.Column(db.Date)

class AlertType(enum.Enum):
    WARNING = 'Warning'
    CRITICAL = 'Critical'

class Alert(db.Model):
    __tablename__ = "alert"
    alert_id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, nullable=False)
    alert_type = db.Column(db.Enum(AlertType), nullable=False)
    alert_message = db.Column(db.String(255), nullable=False)
    alert_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    
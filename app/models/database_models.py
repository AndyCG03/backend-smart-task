from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, DECIMAL, Date, LargeBinary, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    preferences = Column(JSONB, default={
        "notifications": True,
        "energy_tracking": False,
        "default_view": "priority"
    })
    energy_level = Column(String(20), default='medium')
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # ← NUEVO CAMPO
    
    __table_args__ = (
        CheckConstraint("energy_level IN ('low', 'medium', 'high')", name="ck_user_energy_level"),
    )

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    color = Column(String(7), default='#007bff')
    description = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='SET NULL'))
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    urgency = Column(String(20))
    impact = Column(String(20))
    estimated_duration = Column(Integer)
    deadline = Column(DateTime)
    
    priority_score = Column(Integer)
    priority_level = Column(String(20))
    completion_probability = Column(DECIMAL(5,4))
    
    status = Column(String(20), default='pending')
    energy_required = Column(String(20))
    
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    completed_at = Column(DateTime)
    actual_duration = Column(Integer)
    
    __table_args__ = (
        CheckConstraint("urgency IN ('low', 'medium', 'high')", name="ck_task_urgency"),
        CheckConstraint("impact IN ('low', 'medium', 'high')", name="ck_task_impact"),
        CheckConstraint("priority_score >= 1 AND priority_score <= 100", name="ck_task_priority_score"),
        CheckConstraint("priority_level IN ('low', 'medium', 'high')", name="ck_task_priority_level"),
        CheckConstraint("completion_probability >= 0 AND completion_probability <= 1", name="ck_task_completion_prob"),
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'archived', 'postponed')", name="ck_task_status"),
        CheckConstraint("energy_required IN ('low', 'medium', 'high')", name="ck_task_energy_required"),
    )

class TaskHistory(Base):
    __tablename__ = "task_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    change_type = Column(String(50), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    change_description = Column(Text)
    
    created_at = Column(DateTime, default=func.current_timestamp())

class DailyRecommendation(Base):
    __tablename__ = "daily_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    
    recommendation_reason = Column(Text, nullable=False)
    confidence_score = Column(DECIMAL(5,4))
    
    status = Column(String(20), default='pending')
    was_completed = Column(Boolean)
    completed_on_time = Column(Boolean)
    
    recommendation_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="ck_recommendation_confidence"),
        CheckConstraint("status IN ('pending', 'accepted', 'rejected', 'postponed')", name="ck_recommendation_status"),
    )

class EnergyLog(Base):
    __tablename__ = "energy_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='SET NULL'))
    
    energy_level = Column(String(20), nullable=False)
    notes = Column(Text)
    
    logged_at = Column(DateTime, default=func.current_timestamp())
    
    __table_args__ = (
        CheckConstraint("energy_level IN ('low', 'medium', 'high')", name="ck_energy_log_level"),
    )

class AIModel(Base):
    __tablename__ = "ai_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    
    model_type = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    
    model_data = Column(LargeBinary)
    feature_weights = Column(JSONB)
    accuracy_metrics = Column(JSONB)
    
    is_active = Column(Boolean, default=False)
    trained_at = Column(DateTime, default=func.current_timestamp())

class AIFeedback(Base):
    __tablename__ = "ai_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    
    predicted_priority = Column(String(20))
    actual_priority = Column(String(20))
    predicted_completion_probability = Column(DECIMAL(5,4))
    actual_completed = Column(Boolean)
    completed_on_time = Column(Boolean)
    
    feedback_date = Column(DateTime, default=func.current_timestamp())
    used_for_training = Column(Boolean, default=False)
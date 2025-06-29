#!/usr/bin/env python3
"""
Database Models and Schemas
Generated by Autonomous AGI Development Pipeline
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Database setup
DATABASE_URL = "postgresql://user:password@localhost/dbname"  # Configure appropriately
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=1)  # 1=low, 2=medium, 3=high
    status = Column(String, default="pending")  # pending, in_progress, completed
    owner_id = Column(Integer, ForeignKey("users.id"))
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")

# Add relationships
User.owned_tasks = relationship("Task", foreign_keys=[Task.owner_id], back_populates="owner")
User.assigned_tasks = relationship("Task", foreign_keys=[Task.assigned_to_id], back_populates="assigned_to")

# Pydantic Schemas
class UserBase(BaseModel):
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Unique username")
    full_name: Optional[str] = Field(None, description="User full name")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="User password")

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: int = Field(1, ge=1, le=3, description="Task priority (1=low, 2=medium, 3=high)")
    status: str = Field("pending", description="Task status")
    due_date: Optional[datetime] = Field(None, description="Task due date")

class TaskCreate(TaskBase):
    assigned_to_id: Optional[int] = Field(None, description="User ID to assign task to")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=3)
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    owner_id: int
    assigned_to_id: Optional[int]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Create tables
Base.metadata.create_all(bind=engine)
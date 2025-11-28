"""User Pydantic schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    # TODO: Define base user fields
    pass


class UserCreate(UserBase):
    """Schema for creating a user"""
    # TODO: Define fields for user creation
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    # TODO: Define fields for user update
    pass


class User(UserBase):
    """Schema for user response"""
    # TODO: Define fields for user response
    
    class Config:
        from_attributes = True

"""User Pydantic schemas"""
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., description="Unique username for the user", max_length=50)
    email: Optional[EmailStr] = Field(None, description="User's email address")
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    is_active: bool = Field(default=False, description="Indicates if the user is active")

    @field_validator('username')
    def validate_username(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters long')
        return v


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., description="Password for the user", min_length=6)
    is_admin: bool = Field(default=False, description="Indicates if the user is an admin")

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] =  Field(None, description="Unique username for the user", max_length=50)
    email: Optional[EmailStr] = Field(None, description="User's email address")
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    password: Optional[str] = Field(None, description="Password for the user", min_length=6)
    is_active: Optional[bool] = Field(None, description="Indicates if the user is active")
    is_admin: Optional[bool] = Field(None, description="Indicates if the user is an admin")
    
    @field_validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters long')
            if len(v) > 50:
                raise ValueError('Username must be less than 50 characters long')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if v is not None and len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class User(UserBase):
    """Schema for user response"""
    id: int = Field(..., description="Unique identifier for the user")
    is_admin: bool = Field(..., description="Indicates if the user is an admin")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: Optional[datetime] = Field(None, description="When the user was last updated")
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of the token, e.g., Bearer")


class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = Field(None, description="Username contained in the token")

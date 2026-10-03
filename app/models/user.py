from pydantic import BaseModel

class User(BaseModel):
    id: int = Field(default_factory=lambda: uuid.uuid4())
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(unique=True)
    password: str = Field(min_length=8, max_length=100, regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


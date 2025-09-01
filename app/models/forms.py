from pydantic import BaseModel, Field

class CreateApp(BaseModel):
    name: str = Field(max_length=255, min_length=1)
    motto: str = Field(max_length=1024, min_length=3)
    key: str = Field(max_length=28, min_length=28)
    
class Status(BaseModel):
    name: str = Field(max_length=255, min_length=1)
    status: str = Field(max_length=255, min_length=3)
    key: str = Field(max_length=28, min_length=28)

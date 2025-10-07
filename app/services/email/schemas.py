from pydantic import BaseModel, Field
from app.services.email.style_config import EmailStyleConfig
from typing import Optional

class UserInput(BaseModel):
  email_info: str = Field(description="Informacje od user, które mają służyć kreacji maila")
  email_style: EmailStyleConfig
    
class ResponseModel(BaseModel):
  user_query: str = Field(description="Original user query")
  output_MD: str = Field(description="Agent response. Format MD")
  validation_pass: Optional[bool] = None
  email_title: Optional[str] = None
  credtis: int = Field(description="User credits number")
from pydantic import BaseModel

class ProductCreate(BaseModel):
    url: str
    title: str
    price: str
    description: str
    features: str
    images: str
    category: str
    source: str

class ProductRead(ProductCreate):
    id: int

    class Config:
        from_attributes = True  

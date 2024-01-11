from typing import List
from pydantic import BaseModel

class Khu(BaseModel):
    ten: str

class DbKhu(Khu):
    id: int

    class Config:
        orm_mode = True

class Phong(BaseModel):
    ten: str
    khu_id: int
    don_vi_id: int

class DbPhong(Phong):
    id: int

    class Config:
        orm_mode = True

class DonVi(BaseModel):
    ten: str

class DbDonVi(DonVi):
    id: int

    class Config:
        orm_mode = True

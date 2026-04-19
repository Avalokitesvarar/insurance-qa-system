"""
产品数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class Coverage(BaseModel):
    """保障项"""
    name: str = Field(description="保障项名称")
    amount: str = Field(description="保额")
    description: Optional[str] = Field(default=None, description="说明")


class Premium(BaseModel):
    """保费信息"""
    age_range: str = Field(description="年龄段")
    male_price: Optional[float] = Field(default=None, description="男性保费")
    female_price: Optional[float] = Field(default=None, description="女性保费")
    payment_period: str = Field(description="缴费期限")


class Product(BaseModel):
    """保险产品"""
    product_id: str = Field(description="产品ID")
    name: str = Field(description="产品名称")
    company: str = Field(description="保险公司")
    product_type: str = Field(description="产品类型：重疾险/医疗险/寿险/意外险")

    # 核心信息
    coverages: List[Coverage] = Field(description="保障项列表")
    premiums: List[Premium] = Field(description="保费信息")

    # 详细信息
    features: List[str] = Field(default_factory=list, description="产品特色")
    exclusions: List[str] = Field(default_factory=list, description="责任免除")
    waiting_period: Optional[str] = Field(default=None, description="等待期")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    source_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "P001",
                "name": "超级玛丽9号重疾险",
                "company": "信泰人寿",
                "product_type": "重疾险",
                "coverages": [
                    {"name": "重大疾病", "amount": "50万", "description": "120种重疾"}
                ],
                "premiums": [
                    {"age_range": "30岁", "male_price": 5000, "female_price": 4500, "payment_period": "30年"}
                ],
                "features": ["重疾额外赔", "轻症豁免"],
                "exclusions": ["既往症", "战争"],
                "waiting_period": "90天"
            }
        }


class Article(BaseModel):
    """公众号文章"""
    article_id: str
    title: str
    author: str
    publish_date: datetime
    content: str
    tags: List[str] = Field(default_factory=list)
    source_url: Optional[str] = None

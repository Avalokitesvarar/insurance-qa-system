"""
示例产品数据
"""

SAMPLE_PRODUCTS = [
    {
        "product_id": "P001",
        "name": "超级玛丽9号重疾险",
        "company": "信泰人寿",
        "product_type": "重疾险",
        "coverages": [
            {"name": "重大疾病", "amount": "50万", "description": "120种重疾，赔付100%基本保额"},
            {"name": "中症", "amount": "30万", "description": "20种中症，赔付60%基本保额"},
            {"name": "轻症", "amount": "15万", "description": "40种轻症，赔付30%基本保额"}
        ],
        "premiums": [
            {"age_range": "30岁", "male_price": 5280, "female_price": 4850, "payment_period": "30年交"},
            {"age_range": "40岁", "male_price": 8650, "female_price": 7920, "payment_period": "30年交"}
        ],
        "features": [
            "60岁前额外赔80%",
            "重疾多次赔付可选",
            "轻中症豁免保费",
            "可附加恶性肿瘤二次赔"
        ],
        "exclusions": ["既往症", "遗传性疾病", "战争", "核辐射", "故意犯罪"],
        "waiting_period": "90天"
    },
    {
        "product_id": "P002",
        "name": "达尔文8号重疾险",
        "company": "国富人寿",
        "product_type": "重疾险",
        "coverages": [
            {"name": "重大疾病", "amount": "50万", "description": "110种重疾"},
            {"name": "中症", "amount": "25万", "description": "25种中症，赔付50%"},
            {"name": "轻症", "amount": "15万", "description": "50种轻症，赔付30%"}
        ],
        "premiums": [
            {"age_range": "30岁", "male_price": 4980, "female_price": 4520, "payment_period": "30年交"},
            {"age_range": "40岁", "male_price": 8120, "female_price": 7450, "payment_period": "30年交"}
        ],
        "features": [
            "60岁前额外赔100%",
            "重疾关爱金",
            "癌症二次赔间隔期短",
            "保费相对便宜"
        ],
        "exclusions": ["既往症", "遗传性疾病", "战争", "核辐射"],
        "waiting_period": "90天"
    },
    {
        "product_id": "P003",
        "name": "蓝医保长期医疗险",
        "company": "太平洋健康",
        "product_type": "医疗险",
        "coverages": [
            {"name": "一般医疗", "amount": "200万", "description": "免赔额1万"},
            {"name": "重疾医疗", "amount": "400万", "description": "0免赔"},
            {"name": "质子重离子", "amount": "400万", "description": "100%报销"}
        ],
        "premiums": [
            {"age_range": "30岁", "male_price": 286, "female_price": 286, "payment_period": "1年"},
            {"age_range": "40岁", "male_price": 486, "female_price": 486, "payment_period": "1年"}
        ],
        "features": [
            "保证续保20年",
            "外购药报销",
            "重疾津贴1万/年",
            "增值服务丰富"
        ],
        "exclusions": ["既往症", "美容整形", "牙科"],
        "waiting_period": "30天"
    },
    {
        "product_id": "P004",
        "name": "大黄蜂9号少儿重疾险",
        "company": "北京人寿",
        "product_type": "重疾险",
        "coverages": [
            {"name": "重大疾病", "amount": "50万", "description": "120种重疾"},
            {"name": "少儿特疾", "amount": "100万", "description": "20种少儿特疾额外赔100%"},
            {"name": "罕见病", "amount": "150万", "description": "10种罕见病额外赔200%"}
        ],
        "premiums": [
            {"age_range": "0岁", "male_price": 850, "female_price": 780, "payment_period": "30年交"},
            {"age_range": "5岁", "male_price": 920, "female_price": 850, "payment_period": "30年交"}
        ],
        "features": [
            "少儿特疾高额赔付",
            "罕见病保障",
            "重疾多次赔可选",
            "保费豁免"
        ],
        "exclusions": ["既往症", "遗传性疾病"],
        "waiting_period": "90天"
    }
]

from bson import ObjectId
from utils.response import ResponseHandler

class ProductService:
    def __init__(self, db):
        self.db = db
        self.collection = db["products"]

    # 檢查dict value 是否有空值    
    def _check_all_items(self, d: dict) -> bool:
        for v in d.values():
            if not v:
                return True
        return False
    
    # 提取並轉換 _id 值的方法
    def _convert_objectid_to_str(self, data):
        for item in data:
            # 將 MongoDB 的 ObjectId 轉換成字串格式
            item["_id"] = str(item["_id"])
        return data
    
    
    #! 會重複加資料
    #todo: 驗證商品格式
    def add_product(self, product_data):
        try:
            # 商品資料不能為空
            if not product_data:
                return {
                    "code": 400,
                    "message":"商品資料是空的",
                    "body": {}
                }
            
            if self._check_all_items(product_data):
                return {
                    "code": 400,
                    "message":"商品資料不能包含空值",
                    "body": {}
                }
            
            # Success
            self.collection.insert_one(product_data)
            return {
                "code": 200,
                "message":"商品新增成功",
                "body": {}
            }
            
        except Exception as e:
            return {
                "code": 500,
                "message":f"Sever Error(product_service.py): {str(e)}",
                "body": {}
            }

    # 返回所有商品
    def get_products(self):
        try:
            products = list(self.collection.find())
            converted_body = self._convert_objectid_to_str(products)
            
            return {
                "code":200,
                "message":"成功取得所有商品",
                "body": converted_body
            }
            
        except Exception as e:
            return {
                "code": 500,
                "message":f"Sever Error(product_service.py): {str(e)}",
                "body": {}
            }
            
    # 根據product_id, 取得一筆資料
    def get_one_product_by_id(self, product_id: str):
        try:    
            product = self.collection.find_one({"_id": ObjectId(product_id)})
            if not product:
                return {
                    "code": 404,
                    "message": "找不到該商品",
                    "body": {}
                }
                
            product["_id"] = str(product["_id"])
            return {
                "code":200,
                "message":"成功取得該商品",
                "body": product
            }
            
        except Exception as e:
            return {
                "code": 500,
                "message":f"Sever Error(product_service.py): {str(e)}",
                "body": {}
            }

    # 更新商品資料
    def update_product(self, product_data):
        try:
            # 商品資料不能為空
            if not product_data:
                return {
                    "code": 400,
                    "message":"商品資料是空的",
                    "body": {}
                }
            
            if self._check_all_items(product_data):
                return {
                    "code": 400,
                    "message":"商品資料不能包含空值",
                    "body": {}
                }
            
            # Success
            product_id = product_data.get("_id")
            product_data.pop("_id")
            update_data = self.collection.update_one({"_id": ObjectId(product_id)}, {"$set": product_data})
            if update_data.matched_count == 0:
                return {
                    "code": 400,
                    "message":"找不到該商品資料",
                    "body": {
                        "matched_count": update_data.matched_count,  # 匹配到的數量
                        "modified_count": update_data.modified_count  # 修改的數量
                    }
                }
            
            return {
                "code": 200,
                "message":"商品更新成功",
                "body": {
                    "matched_count": update_data.matched_count,  # 匹配到的數量
                    "modified_count": update_data.modified_count  # 修改的數量
                }
            }
            
        except Exception as e:
            return {
                "code": 500,
                "message":f"Sever Error(product_service.py): {str(e)}",
                "body": {}
            }
    # 加入購物車    
    def add_to_cart(self, request_data):
        try:
            if not request_data:
                return ResponseHandler(400,"沒有取得任何資料").response()
                
            user_id = request_data["user_id"]
            product_id = request_data["product_id"]
            quantity = request_data["quantity"]
            if not (user_id and product_id and quantity):
                return ResponseHandler(400,"需要提供user_id, product_id, quantity").response()
                
            user = self.db["users"].find_one({"_id": ObjectId(user_id)})
            product = self.collection.find_one({"_id":ObjectId(product_id)})
            if not (user and product):
                message ="User not found" if not user else "Product not found"
                return ResponseHandler(404,message).response()
            
            # 確定使用者有沒有購物車
            user_cart_id = user.get("cart_id","") 
            # 有存在
            if user_cart_id:
                # 加入products list中
                cart = self.db["cart"].find_one({"_id": ObjectId(user_cart_id)})
                if not cart:
                    return ResponseHandler(404,"無法找到購物車資料").response()
                
                products = list(cart.get("products"))
                # 要避免重複加入不然會有相同的ObjectId(product_id)
                if any(ObjectId(product_id) == d.get("product_id") for d in products):
                    return ResponseHandler(400, "商品重複加入").response()
                    
                # 更新cart
                new_product = {
                    "product_id": ObjectId(product_id),
                    "quantity": quantity
                }
                products.append(new_product)
                self.db["cart"].update_one(
                    {"_id": ObjectId(user_cart_id)},
                    {"$set": {"products": products}}
                )
                
            # 不存在
            else:
                # 創建新購物車
                new_cart = {
                    "user_id": ObjectId(user_id),
                    "products":[
                        {
                            "product_id": ObjectId(product_id),
                            "quantity": quantity
                        }
                    ]
                }
                result = self.db["cart"].insert_one(new_cart)
                new_cart_id = str(result.inserted_id) # str

                # 更新使用者的 cart_id
                self.db["users"].update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"cart_id": new_cart_id}}
                )
            return ResponseHandler(200,"商品成功新增到購物車").response()
            
        except Exception as e:
            message=f"Sever Error(product_service.py: {str(e)}"
            return ResponseHandler(message=message).response()
        
    # 加入收藏
    def add_to_favorite(self, request_data):
        try:
            if not request_data:
                return {
                    "code": 400,
                    "message":"沒有取得任何資料",
                    "body": {}
                }
                
            user_id = request_data["user_id"]
            product_id = request_data["product_id"]
            if not (user_id and product_id):
                return {
                    "code": 400,
                    "message":"需要提供user_id 跟 product_id",
                    "body": {}
                }
                
            user = self.db["users"].find_one({"_id": ObjectId(user_id)})
            product = self.collection.find_one({"_id":ObjectId(product_id)})
            if not (user and product):
                if not user:
                    message = "user not find"
                else:
                    message = "product not find"
                return {
                    "code": 404,
                    "message":message,
                    "body": {}
                }
            # 確定使用者有沒有收藏資料
            user_favorites_id = user.get("favorites_id","")
            # 有存在
            if user_favorites_id:
                # 加入product_id list中
                favorites = self.db["favorites"].find_one({"_id": ObjectId(user_favorites_id)})
                if not favorites:
                    return {
                        "code": 400,
                        "message": "找不到使用者的收藏資料",
                        "body": {}
                    }
                favorites_product_ids = favorites.get("product_id")
                # 更新favorites
                if ObjectId(product_id) not in favorites_product_ids:
                    favorites_product_ids.append(ObjectId(product_id))
                    self.db["favorites"].update_one(
                        {"_id": ObjectId(user_favorites_id)},
                        {"$set": {"product_id": favorites_product_ids}}
                    )
                else:
                    return {
                        "code": 400,
                        "message": "商品重複加入",
                        "body": {}
                    }
                
            # 不存在
            else:
                # 創建使用者收藏
                new_favorites = {
                    "user_id": ObjectId(user_id),
                    "product_id": [ObjectId(product_id)]
                }
                result = self.db["favorites"].insert_one(new_favorites)
                new_favorites_id = str(result.inserted_id)# 存進去用str

                # 更新使用者的 favorites_id
                self.db["users"].update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"favorites_id": new_favorites_id}}
                )
            return {
                "code": 200,
                "message": "商品成功加到收藏",
                "body": {}
            }
            
        except Exception as e:
            return {
                "code": 500,
                "message":f"Sever Error(product_service.py): {str(e)}",
                "body": {}
            }
            
    # 更新購物車商品數量
    def update_cart(self, request_data):
        try:
            if not request_data:
                return ResponseHandler(400,"沒有取得任何request資料").response()
            
            user_id = request_data.get("user_id")
            product_id = request_data.get("product_id")
            quantity = request_data.get("quantity")
            if not (user_id and product_id and (quantity is not None)):
                return ResponseHandler(400,"請提供user_id, product_id, quantity").response()
            
            user = self.db["users"].find_one({"_id":ObjectId(user_id)})
            if not user:
                return ResponseHandler(404,"沒有該使用者").response()
            
            product = self.db["products"].find_one({"_id":ObjectId(product_id)})
            if not product:
                return ResponseHandler(404,"沒有該商品").response()
            
            cart_id = user.get("cart_id")
            if not cart_id:
                return ResponseHandler(404,"沒有cart_id(沒有購物車資料)").response()
            
            cart = self.db["cart"]
            find_cart = cart.find_one({"_id":ObjectId(cart_id)})
            if not find_cart:
                return ResponseHandler(404,"沒有該購物車資料").response()
            
            products = list(find_cart.get("products"))
            # 數量是零刪除該商品資料
            if quantity != 0:
                for d in products:
                    if d.get("product_id") == ObjectId(product_id):
                        d["quantity"] = quantity
                        break
            else:
                for d in products:
                    if d.get("product_id") == ObjectId(product_id):
                        products.remove(d)
                
            
            update_cart = cart.update_one({"_id": ObjectId(cart_id)},{"$set": {"products": products}})
            response_body ={
                "matched_count": update_cart.matched_count,  # 匹配到的數量
                "modified_count": update_cart.modified_count  # 修改的數量
            }
            return ResponseHandler(200,"已更新該購物車商品數量資料",response_body).response()
            
        except Exception as e:
            message=f"Sever Error(product_service.py: {str(e)}"
            return ResponseHandler(message=message).response()
    
    # 從收藏刪除
    def delete_from_favorites(self, request_data):
        try:
            if not request_data:
                return {
                    "code": 400,
                    "message":"沒有取得任何request資料",
                    "body": {}
                }
                
            user_id = request_data.get("user_id")
            delete_product_id = request_data.get("product_id")
            if not (user_id and delete_product_id):
                return {
                    "code": 400,
                    "message":"需要提供user_id, product_id",
                    "body": {}
                }
                
            user = self.db["users"].find_one({"_id": ObjectId(user_id)})
            if not user:
                return {
                    "code": 404,
                    "message":"沒有該使用者",
                    "body": {}
                }
                
            delete_product = self.db["products"].find_one({"_id":ObjectId(delete_product_id)})
            if not delete_product:
                return {
                    "code": 404,
                    "message":"沒有該商品",
                    "body": {}
                }
            
            user_favorites_id = user.get("favorites_id")
            if not user_favorites_id:
                return {
                    "code": 404,
                    "message":"使用者沒有favorites_id(沒有收藏資料)",
                    "body": {}
                }
            # 從favorites找到porduct_id[]，刪掉delete_product_id
            favorites = self.db["favorites"].find_one({"_id":ObjectId(user_favorites_id)})
            all_produt_id = list(favorites.get("product_id"))
            all_produt_id.remove(ObjectId(delete_product_id))      
            if all_produt_id == None:
                all_produt_id = []
            self.db["favorites"].update_one({"_id":ObjectId(user_favorites_id)},{"$set":{"product_id":all_produt_id}})
            return {
                "code": 200,
                "message": "成功刪除該收藏商品",
                "body": {}
            }
            
        except Exception as e:
            return {
                "code": 500,
                "message":f"Sever Error(product_service.py): {str(e)}",
                "body": {}
            }
    
    # user_id找收藏商品
    def get_favorites_by_user_id(self, request_data):
        try:
            if not request_data:
                return {
                    "code": 400,
                    "message":"沒有取得任何request資料",
                    "body": {}
                }
                
            user_id = request_data["user_id"]
            if not user_id:
                return {
                    "code": 400,
                    "message":"需要提供user_id",
                    "body": {}
                }
                
            user = self.db["users"].find_one({"_id": ObjectId(user_id)})
            if not user:
                return {
                    "code": 404,
                    "message":"沒有該使用者",
                    "body": {}
                }
            user_favorites_id = user.get("favorites_id")
            if not user_favorites_id:
                return {
                    "code": 404,
                    "message":"使用者沒有favorites_id(沒有收藏資料)",
                    "body": {}
                }
            favorites = self.db["favorites"].find_one({"_id":ObjectId(user_favorites_id)})
            all_product_id = list(favorites.get("product_id"))
            result = list(map(lambda x:str(x), all_product_id))
            return {
                "code": 200,
                "message": "成功取得該使用者收藏的所有product_id資料",
                "body": result
            }
            
        except Exception as e:
            return {
                "code": 500,
                "message":f"Sever Error(product_service.py): {str(e)}",
                "body": {}
            }
            
    # user_id找購物車
    def get_cart_by_user_id(self, request_data):
        try:
            if not request_data:
                return ResponseHandler(400,"沒有取得任何request資料").response()
                
            user_id = request_data["user_id"]
            if not user_id:
                return ResponseHandler(400,"需要提供user_id").response()
                
            user = self.db["users"].find_one({"_id": ObjectId(user_id)})
            if not user:
                return ResponseHandler(404,"沒有該使用者").response()
            
            user_cart_id = user.get("cart_id")
            if not user_cart_id:
                return ResponseHandler(404,"使用者沒有cart_id(沒有購物車資料)").response()

            # Success
            cart = self.db["cart"].find_one({"_id":ObjectId(user_cart_id)})
            products = list(cart.get("products"))
            result = list(map(lambda d:str(d["product_id"]), products))
            return ResponseHandler(200,"成功取得該使用者購物車的所有product_id資料",result).response()
            
        except Exception as e:
            message=f"Sever Error(product_service.py: {str(e)}"
            return ResponseHandler(message=message).response()
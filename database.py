from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Optional, List, Dict, Any
from datetime import datetime

class Database:
    def __init__(self, client: AsyncIOMotorClient, db_name: str):
        self.client = client
        self.db = client[db_name]
        self.orders = self.db.orders
        self.stores = self.db.stores
        self.users = self.db.users

    async def create_indexes(self):
        # Create indexes for orders collection
        await self.orders.create_index("shopifyOrderId", unique=True)
        await self.orders.create_index("orderNumber")
        await self.orders.create_index("status")
        await self.orders.create_index("callStatus")
        await self.orders.create_index("createdAt")

        # Create indexes for stores collection
        await self.stores.create_index("shopifyDomain", unique=True)
        await self.stores.create_index("accessToken")

        # Create indexes for users collection
        await self.users.create_index("email", unique=True)
        await self.users.create_index("store_id")

    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        return await self.orders.find_one({"_id": ObjectId(order_id)})

    async def get_orders(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        call_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = {}
        if status:
            query["status"] = status
        if call_status:
            query["callStatus"] = call_status

        cursor = self.orders.find(query).skip(skip).limit(limit).sort("createdAt", -1)
        return await cursor.to_list(length=limit)

    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.orders.insert_one(order_data)
        return await self.get_order(str(result.inserted_id))

    async def update_order(self, order_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        await self.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
        return await self.get_order(order_id)

    async def get_store(self, store_id: str) -> Optional[Dict[str, Any]]:
        return await self.stores.find_one({"_id": ObjectId(store_id)})

    async def get_store_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        return await self.stores.find_one({"shopifyDomain": domain})

    async def create_store(self, store_data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.stores.insert_one(store_data)
        return await self.get_store(str(result.inserted_id))

    async def update_store(self, store_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        update_data["updatedAt"] = datetime.utcnow()
        await self.stores.update_one(
            {"_id": ObjectId(store_id)},
            {"$set": update_data}
        )
        return await self.get_store(store_id)

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.users.find_one({"_id": ObjectId(user_id)})

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return await self.users.find_one({"email": email})

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.users.insert_one(user_data)
        return await self.get_user(str(result.inserted_id))

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        await self.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return await self.get_user(user_id) 
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status

from app.models.shopping_list import (
    ShoppingListCreate,
    ShoppingListUpdate,
    ShoppingListResponse,
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListStatus,
    ShoppingListItemResponse
)


class ShoppingListService:
    def __init__(self, db):
        self.db = db
        self.collection = db.shopping_lists

    async def create_shopping_list(self, shopping_list: ShoppingListCreate, user_id: str) -> Dict:
        """
        Create a new shopping list.
        
        Args:
            shopping_list: Shopping list data
            user_id: ID of the user creating the list
            
        Returns:
            Created shopping list
        """
        # Generate item IDs for any initial items
        items = []
        for item in shopping_list.items:
            item_dict = item.dict()
            item_dict["id"] = str(ObjectId())
            item_dict["created_at"] = datetime.now()
            item_dict["updated_at"] = datetime.now()
            items.append(item_dict)
            
        # Create the shopping list document
        now = datetime.now()
        shopping_list_dict = {
            "name": shopping_list.name,
            "family_id": shopping_list.family_id,
            "date": shopping_list.date or now,
            "total_cost": shopping_list.total_cost or 0,
            "status": shopping_list.status,
            "items": items,
            "shared_with": [],
            "plan_id": shopping_list.plan_id,
            "creator_id": user_id,
            "created_at": now,
            "updated_at": now,
            "completed_at": None
        }
        
        # Insert the document
        result = await self.collection.insert_one(shopping_list_dict)
        
        # Get the created shopping list
        created_list = await self.collection.find_one({"_id": result.inserted_id})
        
        # Transform MongoDB _id to string id
        created_list["id"] = str(created_list.pop("_id"))
        
        return created_list

    async def get_shopping_lists(
        self,
        user_id: str,
        status: Optional[ShoppingListStatus] = None,
        family_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get shopping lists with optional filters.
        
        Args:
            user_id: User ID
            status: Filter by status
            family_id: Filter by family ID
            plan_id: Filter by plan ID
            date_from: Filter by date (from)
            date_to: Filter by date (to)
            
        Returns:
            List of shopping lists
        """
        # Build query
        query = {
            "$or": [
                {"creator_id": user_id},
                {"shared_with": user_id}
            ]
        }
        
        if status:
            query["status"] = status
            
        if family_id:
            query["family_id"] = family_id
            
        if plan_id:
            query["plan_id"] = plan_id
            
        date_query = {}
        if date_from:
            date_query["$gte"] = date_from
        if date_to:
            date_query["$lte"] = date_to
        if date_query:
            query["date"] = date_query
        
        # Execute query
        cursor = self.collection.find(query).sort("date", -1)
        
        # Process results
        shopping_lists = await cursor.to_list(length=100)
        
        # Transform MongoDB _id to string id
        for shopping_list in shopping_lists:
            shopping_list["id"] = str(shopping_list.pop("_id"))
        
        return shopping_lists

    async def get_shopping_list_by_id(self, shopping_list_id: str, user_id: str) -> Optional[Dict]:
        """
        Get a shopping list by ID.
        
        Args:
            shopping_list_id: Shopping list ID
            user_id: User ID for permission check
            
        Returns:
            Shopping list or None if not found or no permission
        """
        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(shopping_list_id)
        except:
            # Invalid ID format
            return None
        
        # Query with permission check
        shopping_list = await self.collection.find_one({
            "_id": obj_id,
            "$or": [
                {"creator_id": user_id},
                {"shared_with": user_id}
            ]
        })
        
        if not shopping_list:
            return None
        
        # Transform MongoDB _id to string id
        shopping_list["id"] = str(shopping_list.pop("_id"))
        
        return shopping_list

    async def update_shopping_list(
        self, 
        shopping_list_id: str, 
        shopping_list_update: ShoppingListUpdate, 
        user_id: str
    ) -> Optional[Dict]:
        """
        Update a shopping list.
        
        Args:
            shopping_list_id: Shopping list ID
            shopping_list_update: Update data
            user_id: User ID for permission check
            
        Returns:
            Updated shopping list or None if not found or no permission
        """
        # Get the shopping list (with permission check)
        shopping_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Check if the user is the creator (only creator can update core properties)
        if shopping_list["creator_id"] != user_id:
            # Non-creators can only check/uncheck items
            return None
        
        # Build update document
        update_data = shopping_list_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.now()
        
        # Special handling for status change to COMPLETED
        if "status" in update_data and update_data["status"] == ShoppingListStatus.COMPLETED:
            update_data["completed_at"] = datetime.now()
        
        # Execute update
        try:
            obj_id = ObjectId(shopping_list_id)
        except:
            return None
            
        await self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        
        # Get updated document
        updated_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        return updated_list

    async def delete_shopping_list(self, shopping_list_id: str, user_id: str) -> bool:
        """
        Delete a shopping list.
        
        Args:
            shopping_list_id: Shopping list ID
            user_id: User ID for permission check
            
        Returns:
            True if deleted, False if not found or no permission
        """
        # Get the shopping list (with permission check)
        shopping_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        if not shopping_list:
            return False
        
        # Check if the user is the creator (only creator can delete)
        if shopping_list["creator_id"] != user_id:
            return False
        
        # Execute delete
        try:
            obj_id = ObjectId(shopping_list_id)
        except:
            return False
            
        result = await self.collection.delete_one({
            "_id": obj_id,
            "creator_id": user_id
        })
        
        return result.deleted_count > 0

    async def add_item_to_shopping_list(
        self, 
        shopping_list_id: str, 
        item: ShoppingListItemCreate, 
        user_id: str
    ) -> Optional[Dict]:
        """
        Add an item to a shopping list.
        
        Args:
            shopping_list_id: Shopping list ID
            item: Item data
            user_id: User ID for permission check
            
        Returns:
            Updated shopping list or None if not found or no permission
        """
        # Get the shopping list (with permission check)
        shopping_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Create item with ID and timestamps
        now = datetime.now()
        item_dict = item.dict()
        item_dict["id"] = str(ObjectId())
        item_dict["created_at"] = now
        item_dict["updated_at"] = now
        
        # Execute update
        try:
            obj_id = ObjectId(shopping_list_id)
        except:
            return None
            
        await self.collection.update_one(
            {"_id": obj_id},
            {
                "$push": {"items": item_dict},
                "$set": {"updated_at": now}
            }
        )
        
        # Get updated document
        updated_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        return updated_list

    async def update_shopping_list_item(
        self, 
        shopping_list_id: str, 
        item_id: str, 
        item_update: ShoppingListItemUpdate, 
        user_id: str
    ) -> Optional[Dict]:
        """
        Update an item in a shopping list.
        
        Args:
            shopping_list_id: Shopping list ID
            item_id: Item ID
            item_update: Update data
            user_id: User ID for permission check
            
        Returns:
            Updated shopping list or None if not found or no permission
        """
        # Get the shopping list (with permission check)
        shopping_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Find the item in the list
        item_index = None
        for i, item in enumerate(shopping_list["items"]):
            if item["id"] == item_id:
                item_index = i
                break
        
        if item_index is None:
            return None
        
        # Build update operations
        update_operations = {}
        update_data = item_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                update_operations[f"items.{item_index}.{field}"] = value
        
        # Add updated timestamp
        now = datetime.now()
        update_operations[f"items.{item_index}.updated_at"] = now
        update_operations["updated_at"] = now
        
        # Execute update
        try:
            obj_id = ObjectId(shopping_list_id)
        except:
            return None
            
        await self.collection.update_one(
            {"_id": obj_id},
            {"$set": update_operations}
        )
        
        # Get updated document
        updated_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        return updated_list

    async def remove_item_from_shopping_list(
        self, 
        shopping_list_id: str, 
        item_id: str, 
        user_id: str
    ) -> Optional[Dict]:
        """
        Remove an item from a shopping list.
        
        Args:
            shopping_list_id: Shopping list ID
            item_id: Item ID
            user_id: User ID for permission check
            
        Returns:
            Updated shopping list or None if not found or no permission
        """
        # Get the shopping list (with permission check)
        shopping_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Execute update
        try:
            obj_id = ObjectId(shopping_list_id)
        except:
            return None
            
        await self.collection.update_one(
            {"_id": obj_id},
            {
                "$pull": {"items": {"id": item_id}},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        # Get updated document
        updated_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        return updated_list

    async def complete_shopping_list(self, shopping_list_id: str, user_id: str) -> Optional[Dict]:
        """
        Mark a shopping list as completed.
        
        Args:
            shopping_list_id: Shopping list ID
            user_id: User ID for permission check
            
        Returns:
            Updated shopping list or None if not found or no permission
        """
        # Create an update object with the COMPLETED status
        shopping_list_update = ShoppingListUpdate(status=ShoppingListStatus.COMPLETED)
        
        # Use the existing update method
        return await self.update_shopping_list(shopping_list_id, shopping_list_update, user_id)

    async def share_shopping_list(
        self, 
        shopping_list_id: str, 
        user_ids: List[str], 
        user_id: str
    ) -> Optional[Dict]:
        """
        Share a shopping list with other users.
        
        Args:
            shopping_list_id: Shopping list ID
            user_ids: List of user IDs to share with
            user_id: User ID for permission check
            
        Returns:
            Updated shopping list or None if not found or no permission
        """
        # Get the shopping list (with permission check)
        shopping_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Check if the user is the creator (only creator can share)
        if shopping_list["creator_id"] != user_id:
            return None
        
        # Execute update - add users to shared_with array without duplicates
        try:
            obj_id = ObjectId(shopping_list_id)
        except:
            return None
            
        await self.collection.update_one(
            {"_id": obj_id},
            {
                "$addToSet": {"shared_with": {"$each": user_ids}},
                "$set": {"updated_at": datetime.now()}
            }
        )
        
        # Get updated document
        updated_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        return updated_list

    async def batch_update_items(
        self,
        shopping_list_id: str,
        item_ids: List[str],
        checked: bool,
        user_id: str
    ) -> Optional[Dict]:
        """
        Batch update multiple items in a shopping list.
        
        Args:
            shopping_list_id: Shopping list ID
            item_ids: List of item IDs to update
            checked: Whether to mark items as checked or unchecked
            user_id: User ID for permission check
            
        Returns:
            Updated shopping list or None if not found or no permission
        """
        # Get the shopping list (with permission check)
        shopping_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        if not shopping_list:
            return None
        
        # Prepare the update operations for each item
        now = datetime.now()
        update_operations = {}
        
        for i, item in enumerate(shopping_list["items"]):
            if item["id"] in item_ids:
                update_operations[f"items.{i}.checked"] = checked
                update_operations[f"items.{i}.updated_at"] = now
                
                # If marking as checked, record who and when
                if checked:
                    update_operations[f"items.{i}.purchased_by"] = user_id
                    update_operations[f"items.{i}.purchased_at"] = now
                else:
                    # If unchecking, clear purchase info
                    update_operations[f"items.{i}.purchased_by"] = None
                    update_operations[f"items.{i}.purchased_at"] = None
        
        # Execute update if there are items to update
        if update_operations:
            update_operations["updated_at"] = now
            
            try:
                obj_id = ObjectId(shopping_list_id)
            except:
                return None
                
            await self.collection.update_one(
                {"_id": obj_id},
                {"$set": update_operations}
            )
        
        # Get updated document
        updated_list = await self.get_shopping_list_by_id(shopping_list_id, user_id)
        
        return updated_list
    
    async def generate_shopping_list_from_menu(
        self,
        name: str,
        plan_ids: List[str],
        family_id: Optional[str],
        user_id: str,
        db
    ) -> Optional[Dict]:
        """
        Generate a shopping list from menu plans.
        
        Args:
            name: Name for the new shopping list
            plan_ids: List of menu plan IDs to generate from
            family_id: Optional family ID
            user_id: ID of the user generating the list
            db: Database connection
            
        Returns:
            Created shopping list
        """
        # First, retrieve all the menu plans
        menu_plans_collection = db.menu_plans
        
        menu_plans = []
        for plan_id in plan_ids:
            try:
                plan = await menu_plans_collection.find_one({
                    "_id": ObjectId(plan_id),
                    "$or": [
                        {"creator_id": user_id},
                        {"collaborators.userId": user_id}
                    ]
                })
                if plan:
                    plan["id"] = str(plan.pop("_id"))
                    menu_plans.append(plan)
            except:
                # Skip invalid IDs
                continue
        
        if not menu_plans:
            return None
        
        # Use family_id from the first plan if not provided
        if not family_id and menu_plans:
            family_id = menu_plans[0].get("family_id")
        
        # Extract all recipes from the menu plans
        recipe_ids = []
        for plan in menu_plans:
            for meal in plan.get("meals", []):
                for dish in meal.get("dishes", []):
                    recipe_id = dish.get("recipeId")
                    servings = dish.get("servings", 1)
                    if recipe_id:
                        recipe_ids.append((recipe_id, servings))
        
        # Get recipe details to extract ingredients
        recipes_collection = db.recipes
        
        # Aggregate ingredients from all recipes
        ingredients_map = {}  # Map of ingredient name to details
        
        for recipe_id, servings in recipe_ids:
            try:
                recipe = await recipes_collection.find_one({"_id": ObjectId(recipe_id)})
                if not recipe:
                    continue
                
                # Calculate servings ratio
                recipe_servings = recipe.get("servings", 1)
                ratio = servings / recipe_servings if recipe_servings > 0 else 1
                
                # Add ingredients with adjusted quantities
                for ingredient in recipe.get("ingredients", []):
                    name = ingredient.get("name", "").strip().lower()
                    if not name:
                        continue
                    
                    # Skip optional ingredients
                    if ingredient.get("optional", False):
                        continue
                    
                    # Adjust quantity by servings ratio
                    amount = ingredient.get("amount", 0) * ratio
                    
                    # Initialize or update ingredient in the map
                    if name in ingredients_map:
                        ingredients_map[name]["amount"] += amount
                    else:
                        ingredients_map[name] = {
                            "name": name,
                            "amount": amount,
                            "unit": ingredient.get("unit", ""),
                            "category": ingredient.get("category", "Other"),
                            "checked": False,
                            "note": "",
                            "sources": []
                        }
                    
                    # Add source info
                    ingredients_map[name]["sources"].append({
                        "recipe_id": str(recipe["_id"]),
                        "title": recipe.get("title", "Unknown Recipe"),
                        "amount": amount,
                        "unit": ingredient.get("unit", "")
                    })
            except:
                # Skip problematic recipes
                continue
        
        # Convert ingredients map to list
        items = []
        for ingredient in ingredients_map.values():
            item = ShoppingListItemCreate(
                name=ingredient["name"].capitalize(),
                amount=round(ingredient["amount"], 2),
                unit=ingredient["unit"],
                category=ingredient["category"],
                checked=False,
                note=ingredient.get("note", ""),
                priority="medium"  # Default priority
            )
            items.append(item)
        
        # Create the shopping list
        shopping_list_create = ShoppingListCreate(
            name=name,
            family_id=family_id,
            plan_id=plan_ids[0] if plan_ids else None,  # Link to the first plan
            date=datetime.now(),
            items=items,
            status=ShoppingListStatus.ACTIVE
        )
        
        # Use our existing method to create the shopping list
        return await self.create_shopping_list(shopping_list_create, user_id) 
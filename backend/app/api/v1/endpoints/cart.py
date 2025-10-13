from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from app.db.mongodb import get_database
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import UserResponse
from app.core.security import get_current_user

router = APIRouter()

@router.get("")
async def get_cart(current_user: UserResponse = Depends(get_current_user)):
    db = get_database()
    cart = await db.carts.find_one({"user_id": current_user.id})
    if not cart:
        cart = Cart(user_id=current_user.id).dict()
        await db.carts.insert_one(cart)
    
    # Populate product details
    cart_items = []
    for item in cart.get('items', []):
        product = await db.products.find_one({"id": item['product_id']})
        if product:
            cart_items.append({
                **item,
                "product": Product(**product).dict()
            })
    
    return {"items": cart_items}

@router.post("/add")
async def add_to_cart(item: CartItem, current_user: UserResponse = Depends(get_current_user)):
    db = get_database()
    # Check if product exists
    product = await db.products.find_one({"id": item.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get or create cart
    cart = await db.carts.find_one({"user_id": current_user.id})
    if not cart:
        cart = Cart(user_id=current_user.id).dict()
        await db.carts.insert_one(cart)
    
    # Update cart items
    items = cart.get('items', [])
    existing_item = next((i for i in items if i['product_id'] == item.product_id), None)
    
    if existing_item:
        existing_item['quantity'] += item.quantity
    else:
        items.append(item.dict())
    
    await db.carts.update_one(
        {"user_id": current_user.id},
        {"$set": {"items": items, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Item added to cart"}

@router.post("/remove/{product_id}")
async def remove_from_cart(product_id: str, current_user: UserResponse = Depends(get_current_user)):
    db = get_database()
    cart = await db.carts.find_one({"user_id": current_user.id})
    if cart:
        items = [i for i in cart.get('items', []) if i['product_id'] != product_id]
        await db.carts.update_one(
            {"user_id": current_user.id},
            {"$set": {"items": items, "updated_at": datetime.utcnow()}}
        )
    return {"message": "Item removed from cart"}

@router.post("/update")
async def update_cart_item(item: CartItem, current_user: UserResponse = Depends(get_current_user)):
    db = get_database()
    cart = await db.carts.find_one({"user_id": current_user.id})
    if cart:
        items = cart.get('items', [])
        for i in items:
            if i['product_id'] == item.product_id:
                i['quantity'] = item.quantity
                break
        await db.carts.update_one(
            {"user_id": current_user.id},
            {"$set": {"items": items, "updated_at": datetime.utcnow()}}
        )
    return {"message": "Cart updated"}

@router.delete("/clear")
async def clear_cart(current_user: UserResponse = Depends(get_current_user)):
    db = get_database()
    await db.carts.update_one(
        {"user_id": current_user.id},
        {"$set": {"items": [], "updated_at": datetime.utcnow()}}
    )
    return {"message": "Cart cleared"}

import datetime
import os
import re

from flask import Flask,request,render_template,redirect,session
app = Flask(__name__)
app.secret_key="cloth"
import pymongo
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT + "/static"
from bson import ObjectId

connection = pymongo.MongoClient("mongodb://localhost:27017/")
database = connection['ClothInventory']
category_collection = database['categories']
admin_collection=database['admin']
supplier_collection = database['suppliers']
retailer_collection = database['retailer']
purchase_collection = database['purchases']
purchase_item__collection = database['purchases_items']
purchase_payment__collection = database['purchases_payments']
cloth_inventory_collection = database['cloth_inventory']
order_collection = database['orders']
order_item_collection = database['order_items']
order_payment_collection = database['order_payments']



@app.route("/")
def home():
    category_id = request.args.get("category_id")
    keyword = request.args.get("keyword")
    if category_id == None:
        category_id = ''
    if keyword == None:
        keyword = ''
    if category_id == '':
        rgx = re.compile(".*" + keyword + ".*", re.IGNORECASE)
        query = {"$or": [{"item_name": rgx}, {"cloth_color": rgx}, {"cloth_type": rgx}]}
    else:
        rgx = re.compile(".*" + keyword + ".*", re.IGNORECASE)
        query = {"$or": [{"item_name": rgx}, {"cloth_color": rgx}, {"cloth_type": rgx}],
                 "category_id": ObjectId(category_id)}
    categories = category_collection.find()
    clothInventories = cloth_inventory_collection.find()
    return render_template("index.html",category_id=category_id,categories=categories,clothInventories=clothInventories,str=str,get_category_by_id=get_category_by_id)

@app.route("/AdminLogin")
def AdminLogin():
    return render_template("AdminLogin.html")

@app.route("/SupplierLogin")
def SupplierLogin():
    return render_template("SupplierLogin.html")

@app.route("/RetailerLogin")
def RetailerLogin():
    return render_template("RetailerLogin.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/aLoginAction",methods=['post'])
def aLoginAction():
    userName = request.form.get("userName")
    password = request.form.get('password')
    count = admin_collection.count_documents({"userName":userName,"password":password})
    if count >0:
        session['role'] = 'admin'
        return redirect("/AdminHome")
    else:
        return render_template("msg.html",message="Invalid Details",color="text-danger")

@app.route("/AdminHome")
def AdminHome():
    return render_template("AdminHome.html")

@app.route("/categories")
def categories():
    categories = category_collection.find()
    return render_template("categories.html",categories=categories)


@app.route("/addCategory",methods=['post'])
def addCategory():
    category_name = request.form.get("category_name")
    count = category_collection.count_documents({"category_name":category_name})
    if count>0:
        return render_template("msg.html",message="Category Exists",color="text-danger")
    else:
        category_collection.insert_one({"category_name":category_name})
        return redirect("/categories")


@app.route("/suppliers")
def suppliers():
    suppliers = supplier_collection.find()
    return render_template("suppliers.html",suppliers=suppliers)

@app.route("/sReg")
def sReg():
    return render_template("sReg.html")

@app.route("/sReg1",methods=['post'])
def sReg1():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    company_name = request.form.get("company_name")
    location = request.form.get("location")
    query = {"$or":[{"email":email},{"phone":phone}]}
    count = supplier_collection.count_documents(query)
    if count >0 :
        return render_template("msg.html",message='Duplicate Details',color='text-danger')
    supplier_collection.insert_one({"name":name,"email":email,"phone":phone,"password":password,"address":address,"company_name":company_name,"location":location,"status":"Not Verified"})
    return render_template("msg.html", message='Supplier Registered Successfully', color='text-success')


@app.route("/verifySupplier")
def verifySupplier():
    supplierId = request.args.get("supplierId")
    query = {"$set":{"status":'Verified'}}
    supplier_collection.update_one({"_id":ObjectId(supplierId)},query)
    return redirect("/suppliers")


@app.route("/verifySupplier1")
def verifySupplier1():
    supplierId = request.args.get("supplierId")
    query = {"$set":{"status":'Not Verified'}}
    supplier_collection.update_one({"_id":ObjectId(supplierId)},query)
    return redirect("/suppliers")

@app.route("/clothInventory")
def clothInventory():
    category_id = request.args.get("category_id")
    keyword = request.args.get("keyword")
    if category_id == None:
        category_id = ''
    if keyword == None:
        keyword = ''
    if category_id =='':
        rgx = re.compile(".*" + keyword + ".*", re.IGNORECASE)
        query = {"$or":[{"item_name":rgx},{"cloth_color":rgx},{"cloth_type":rgx}]}
    else:
        rgx = re.compile(".*" + keyword + ".*", re.IGNORECASE)
        query = {"$or": [{"item_name": rgx}, {"cloth_color": rgx}, {"cloth_type": rgx}],"category_id":ObjectId(category_id)}
    categories = category_collection.find()
    categories2 = category_collection.find()
    clothInventories = cloth_inventory_collection.find(query)
    return render_template("clothInventory.html",category_id=category_id,str=str,categories2=categories2,categories=categories,clothInventories=clothInventories,get_category_by_id=get_category_by_id)

def get_category_by_id(category_id):
    category = category_collection.find_one({"_id":ObjectId(category_id)})
    return category

@app.route("/addClothInventory",methods=['post'])
def addClothInventory():
    item_name = request.form.get("item_name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    cloth_type = request.form.get("cloth_type")
    cloth_color = request.form.get('cloth_color')
    picture = request.files.get("picture")
    path = APP_ROOT + "/cloth/" + picture.filename
    picture.save(path)
    category_id = request.form.get("category_id")
    description = request.form.get("description")
    cloth_inventory_collection.insert_one({"item_name":item_name,"price":price,"quantity":quantity,"cloth_type":cloth_type,"cloth_color":cloth_color,"picture":picture.filename,"category_id":ObjectId(category_id),"description":description})
    return redirect("/clothInventory")

@app.route("/editItem")
def editItem():
    item_id = request.args.get("item_id")
    clothInventory = cloth_inventory_collection.find_one({"_id":ObjectId(item_id)})
    return render_template("editItem.html",clothInventory=clothInventory,item_id=item_id)


@app.route("/updatedClothInventory",methods=['post'])
def updatedClothInventory():
    item_id = request.form.get("item_id")
    item_name = request.form.get("item_name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    cloth_type = request.form.get("cloth_type")
    cloth_color = request.form.get("cloth_color")
    query = {"$set":{"item_name":item_name,"price":price,"quantity":quantity,"cloth_type":cloth_type,"cloth_color":cloth_color}}
    cloth_inventory_collection.update_one({"_id":ObjectId(item_id)},query)
    return redirect("/clothInventory")

@app.route("/sLoginAction",methods=['post'])
def sLoginAction():
    email = request.form.get("email")
    password = request.form.get("password")
    count = supplier_collection.count_documents({"email":email,"password":password})
    if count>0:
        supplier = supplier_collection.find_one({"email":email,"password":password})
        if supplier['status'] =='Verified':
           session['supplierId'] = str(supplier['_id'])
           session['role'] = 'supplier'
           return redirect("/supplierHome")
        else:
            return render_template("msg.html",message="Account Not Verified admin ☹",color="text-primary")
    else:
        return render_template("msg.html", message="Invalid Login Details", color="text-danger")

@app.route("/supplierHome")
def supplierHome():
    category_id = request.args.get("category_id")
    keyword = request.args.get("keyword")
    if category_id == None:
        category_id = ''
    if keyword == None:
        keyword = ''
    if category_id == '':
        rgx = re.compile(".*" + keyword + ".*", re.IGNORECASE)
        query = {"$or": [{"item_name": rgx}, {"cloth_color": rgx}, {"cloth_type": rgx}]}
    else:
        rgx = re.compile(".*" + keyword + ".*", re.IGNORECASE)
        query = {"$or": [{"item_name": rgx}, {"cloth_color": rgx}, {"cloth_type": rgx}],
                 "category_id": ObjectId(category_id)}
    categories = category_collection.find()
    clothInventories = cloth_inventory_collection.find(query)
    return render_template("supplierHome.html",categories=categories,str=str,category_id=category_id,clothInventories=clothInventories,get_category_by_id=get_category_by_id)


@app.route("/supplierAddToCart",methods=['post'])
def supplierAddToCart():
    cloth_inventory_id = request.form.get("cloth_inventory_id")
    quantity = request.form.get("quantity")
    supplierId = session['supplierId']
    count = purchase_collection.count_documents({"supplierId":ObjectId(supplierId),'status':'cart'})
    if count ==0:
        purchase = purchase_collection.insert_one({"supplierId":ObjectId(supplierId),"status":'cart',"date":datetime.datetime.now()})
        purchase_id = purchase.inserted_id
    else:
        purchase = purchase_collection.find_one({"supplierId":ObjectId(supplierId),'status':'cart'})
        purchase_id = purchase['_id']
    count2 = purchase_item__collection.count_documents({"purchase_id":ObjectId(purchase_id),"cloth_inventory_id":ObjectId(cloth_inventory_id)})
    if count2>0:
        purchase_item = purchase_item__collection.find_one({"purchase_id":ObjectId(purchase_id),"cloth_inventory_id":ObjectId(cloth_inventory_id)})
        quantity2 = int(purchase_item['quantity']) + int(quantity)
        query = {'$set': {"quantity": quantity2}}
        item = purchase_item__collection.update_one({"purchase_id":ObjectId(purchase_id),"cloth_inventory_id":ObjectId(cloth_inventory_id)}, query)
        cloth_inventory = cloth_inventory_collection.find_one({"_id":ObjectId(cloth_inventory_id)})
        quantity3 = int(cloth_inventory['quantity']) - int(quantity)
        query2 = {'$set': {"quantity": quantity3}}
        cloth_inventory = cloth_inventory_collection.update_one({"_id": ObjectId(cloth_inventory_id)},query2)
        return render_template("msg.html",message="Item Updated",color="text-primary")

    else:
        purchase_item__collection.insert_one({"purchase_id":ObjectId(purchase_id),"cloth_inventory_id":ObjectId(cloth_inventory_id),"quantity":quantity})
        cloth_inventory = cloth_inventory_collection.find_one({"_id": ObjectId(cloth_inventory_id)})
        quantity3 = int(cloth_inventory['quantity']) - int(quantity)
        query2 = {'$set': {"quantity": quantity3}}
        cloth_inventory = cloth_inventory_collection.update_one({"_id": ObjectId(cloth_inventory_id)}, query2)
        return render_template("msg.html", message="Item Add To Cart", color="text-success")


@app.route("/purchasedItems")
def purchasedItems():
    status = request.args.get("status")
    query = {}
    if session['role'] == 'supplier':
        if status == 'cart':
            query = {"supplierId":ObjectId(session['supplierId']),"status":'cart'}
        elif status == 'ordered':
            query = {"supplierId": ObjectId(session['supplierId']),"$or":[{"status": 'ordered'},{"status":'dispatched'}]}
        elif status == 'history':
            query = {"status":'received',"supplierId": ObjectId(session['supplierId'])}
    elif session['role'] == 'admin':
          if status == 'ordered':
              query = {"$or":[{"status": 'ordered'},{"status":'dispatched'}]}
          elif status == 'history':
            query = {"status": 'received'}
    purchases = purchase_collection.find(query)
    purchases = list(purchases)
    if len(purchases) == 0:
        return render_template("msg.html",message="Orders Not Available")
    return render_template("purchasedItems.html",float=float,str=str,get_cloth_inventory_by_id=get_cloth_inventory_by_id,purchases=purchases,get_supplier_by_id=get_supplier_by_id,get_purchase_item_by_id=get_purchase_item_by_id)

def get_purchase_item_by_id(purchase_id):
    purchase_items = purchase_item__collection.find({"purchase_id":ObjectId(purchase_id)})
    return purchase_items

def get_cloth_inventory_by_id(cloth_inventory_id):
    cloth_inventory = cloth_inventory_collection.find_one({"_id":ObjectId(cloth_inventory_id)})
    return cloth_inventory

def get_supplier_by_id(supplierId):
    supplier = supplier_collection.find_one({"_id":ObjectId(supplierId)})
    return supplier

@app.route("/removePurchaseItem")
def removePurchaseItem():
    purchase_item_id = request.args.get("purchase_item_id")
    purchase_id = request.args.get("purchase_id")
    purchase_item = purchase_item__collection.find_one({"_id":ObjectId(purchase_item_id)})
    cloth_inventory = cloth_inventory_collection.find_one({"_id":ObjectId(purchase_item['cloth_inventory_id'])})
    quantity = purchase_item['quantity']
    quantity3 = int(cloth_inventory['quantity']) + int(quantity)
    query = {"$set":{"quantity":quantity3}}
    cloth_inventory_collection.update_one({"_id":ObjectId(purchase_item['cloth_inventory_id'])},query)
    purchase_item__collection.delete_one({"_id":ObjectId(purchase_item_id)})
    count = purchase_item__collection.count_documents({"purchase_id":ObjectId(purchase_id)})
    if count ==0:
        purchase_collection.delete_one({"_id":ObjectId(purchase_id)})
        return render_template("msg.html",message="Order Removed",color="text-danger")
    else:
        return redirect("/purchasedItems?status=cart")


@app.route("/orderPurchaseItem",methods=['post'])
def orderPurchaseItem():
    amount = request.form.get("amount")
    purchase_id = request.form.get("purchase_id")
    return render_template("orderPurchaseItem.html",purchase_id=purchase_id,amount=amount)

@app.route("/orderPurchaseItem1",methods=['post'])
def orderPurchaseItem1():
    amount = request.form.get("amount")
    purchase_id = request.form.get("purchase_id")
    query = {"$set":{"status":'ordered'}}
    purchase_collection.update_one({"_id":ObjectId(purchase_id)},query)
    purchase_payment__collection.insert_one({"amount":amount,"purchase_id":ObjectId(purchase_id),"status":'Amount Paid',"date":datetime.datetime.now()})
    return redirect("/purchasedItems?status=ordered")

@app.route("/dispatchPurchaseOrder",methods=['post'])
def dispatchPurchaseOrder():
    purchase_id = request.form.get("purchase_id")
    query = {"$set":{"status":'dispatched'}}
    purchase_collection.update_one({"_id":ObjectId(purchase_id)},query)
    return redirect("/purchasedItems?status=ordered")

@app.route("/markAsReceived",methods=['post'])
def markAsReceived():
    purchase_id = request.form.get("purchase_id")
    query = {"$set":{"status":'received'}}
    purchase_collection.update_one({"_id":ObjectId(purchase_id)},query)
    return redirect("/purchasedItems?status=history")


@app.route("/view_purchase_payment")
def view_purchase_payment():
    purchase_id = request.args.get("purchase_id")
    payment = purchase_payment__collection.find_one({"purchase_id":ObjectId(purchase_id)})
    return render_template("view_purchase_payment.html",payment=payment)

@app.route("/rReg")
def rReg():
    return render_template("rReg.html")

@app.route("/rReg1",methods=['post'])
def rReg1():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    location = request.form.get("location")
    query = {"$or":[{"email":email},{"phone":phone}]}
    count = retailer_collection.count_documents(query)
    if count >0 :
        return render_template("msg.html",message='Duplicate Details',color='text-danger')
    retailer_collection.insert_one({"name":name,"email":email,"phone":phone,"password":password,"address":address,"location":location})
    return render_template("msg.html", message='Retailer Registered Successfully', color='text-success')


@app.route("/rLoginAction",methods=['post'])
def rLoginAction():
    email = request.form.get("email")
    password = request.form.get("password")
    count = retailer_collection.count_documents({"email":email,"password":password})
    if count>0:
       retailer = retailer_collection.find_one({"email":email,"password":password})
       session['retailerId'] = str(retailer['_id'])
       session['role'] = 'retailer'
       return redirect("/retailerHome")
    else:
        return render_template("msg.html", message="Invalid Login Details", color="text-danger")

@app.route("/retailerHome")
def retailerHome():
    category_id = request.args.get("category_id")
    keyword = request.args.get("keyword")
    if category_id == None:
        category_id = ''
    if keyword == None:
        keyword = ''
    if category_id == '':
        rgx = re.compile(".*" + keyword + ".*", re.IGNORECASE)
        query = {"$or": [{"item_name": rgx}, {"cloth_color": rgx}, {"cloth_type": rgx}]}
    else:
        rgx = re.compile(".*" + keyword + ".*", re.IGNORECASE)
        query = {"$or": [{"item_name": rgx}, {"cloth_color": rgx}, {"cloth_type": rgx}],
                 "category_id": ObjectId(category_id)}
    categories = category_collection.find()
    clothInventories = cloth_inventory_collection.find(query)
    return render_template("retailerHome.html",clothInventories=clothInventories,categories=categories,str=str,category_id=category_id,get_category_by_id=get_category_by_id)


@app.route("/retailerAddToCart",methods=['post'])
def retailerAddToCart():
    cloth_inventory_id = request.form.get("cloth_inventory_id")
    quantity = request.form.get("quantity")
    retailerId = session['retailerId']
    count = order_collection.count_documents({"retailerId":ObjectId(retailerId),'status':'cart'})
    if count ==0:
        order = order_collection.insert_one({"retailerId":ObjectId(retailerId),"status":'cart',"date":datetime.datetime.now()})
        order_id = order.inserted_id
    else:
        order = order_collection.find_one({"retailerId":ObjectId(retailerId),'status':'cart'})
        order_id = order['_id']
    count2 = order_item_collection.count_documents({"order_id":ObjectId(order_id),"cloth_inventory_id":ObjectId(cloth_inventory_id)})
    if count2>0:
        order_item = order_item_collection.find_one({"order_id":ObjectId(order_id),"cloth_inventory_id":ObjectId(cloth_inventory_id)})
        quantity2 = int(order_item['quantity']) + int(quantity)
        query = {'$set': {"quantity": quantity2}}
        item = order_item_collection.update_one({"order_id":ObjectId(order_id),"cloth_inventory_id":ObjectId(cloth_inventory_id)}, query)
        cloth_inventory = cloth_inventory_collection.find_one({"_id":ObjectId(cloth_inventory_id)})
        quantity3 = int(cloth_inventory['quantity']) - int(quantity)
        query2 = {'$set': {"quantity": quantity3}}
        cloth_inventory = cloth_inventory_collection.update_one({"_id": ObjectId(cloth_inventory_id)},query2)
        return render_template("msg.html",message="Item Updated",color="text-primary")

    else:
        order_item_collection.insert_one({"order_id":ObjectId(order_id),"cloth_inventory_id":ObjectId(cloth_inventory_id),"quantity":quantity})
        cloth_inventory = cloth_inventory_collection.find_one({"_id": ObjectId(cloth_inventory_id)})
        quantity3 = int(cloth_inventory['quantity']) - int(quantity)
        query2 = {'$set': {"quantity": quantity3}}
        cloth_inventory = cloth_inventory_collection.update_one({"_id": ObjectId(cloth_inventory_id)}, query2)
        return render_template("msg.html", message="Item Add To Cart", color="text-success")


@app.route("/viewOrders")
def viewOrders():
    status = request.args.get("status")
    query = {}
    if session['role'] == 'retailer':
        if status == 'cart':
            query = {"retailerId":ObjectId(session['retailerId']),"status":'cart'}
        elif status == 'ordered':
            query = {"retailerId": ObjectId(session['retailerId']),"$or": [{"status": 'ordered'}, {"status": 'dispatched'}]}
        elif status == 'history':
            query = {"status": 'received', "retailerId": ObjectId(session['retailerId'])}
    elif session['role'] == 'admin':
        if status == 'ordered':
            query = {"$or": [{"status": 'ordered'}, {"status": 'dispatched'}]}
        elif status == 'history':
            query = {"status": 'received'}
    orders = order_collection.find(query)
    orders = list(orders)
    if len(orders) ==0:
        return render_template("msg.html",message="Orders Not Available")
    return render_template("viewOrders.html",orders=orders,get_retailer_by_id=get_retailer_by_id,get_order_item_by_id=get_order_item_by_id,get_cloth_inventory_by_id=get_cloth_inventory_by_id,float=float)

def get_retailer_by_id(retailerId):
    retailer = retailer_collection.find_one({"_id":ObjectId(retailerId)})
    return retailer

def get_order_item_by_id(order_id):
    order_items = order_item_collection.find({"order_id":ObjectId(order_id)})
    return order_items

@app.route("/removeOrderItem")
def removeOrderItem():
    order_item_id = request.args.get("order_item_id")
    order_id = request.args.get("order_id")
    order_item = order_item_collection.find_one({"_id":ObjectId(order_item_id)})
    cloth_inventory = cloth_inventory_collection.find_one({"_id":ObjectId(order_item['cloth_inventory_id'])})
    quantity = order_item['quantity']
    quantity3 = int(cloth_inventory['quantity']) + int(quantity)
    query = {"$set":{"quantity":quantity3}}
    cloth_inventory_collection.update_one({"_id":ObjectId(order_item['cloth_inventory_id'])},query)
    order_item_collection.delete_one({"_id":ObjectId(order_item_id)})
    count = order_item_collection.count_documents({"order_id":ObjectId(order_id)})
    if count ==0:
        order_collection.delete_one({"_id":ObjectId(order_id)})
        return render_template("msg.html",message="Order Removed",color="text-danger")
    else:
        return redirect("/viewOrders?status=cart")

@app.route("/orderNow",methods=['post'])
def orderNow():
    amount = request.form.get("amount")
    order_id = request.form.get("order_id")
    return render_template("orderNow.html",order_id=order_id,amount=amount)

@app.route("/orderNow1",methods=['post'])
def orderNow1():
    amount = request.form.get("amount")
    order_id = request.form.get("order_id")
    query = {"$set":{"status":'ordered'}}
    order_collection.update_one({"_id":ObjectId(order_id)},query)
    order_payment_collection.insert_one({"amount":amount,"order_id":ObjectId(order_id),"date":datetime.datetime.now(),"status":'Amount Paid'})
    return render_template("msg.html",message="Order Placed")


@app.route("/view_order_payment")
def view_order_payment():
    order_id = request.args.get("order_id")
    payment = order_payment_collection.find_one({"order_id":ObjectId(order_id)})
    return render_template("view_order_payment.html",payment=payment)

@app.route("/dispatchRetailerOrder",methods=['post'])
def dispatchRetailerOrder():
    order_id = request.form.get("order_id")
    query = {"$set":{"status":'dispatched'}}
    order_collection.update_one({"_id":ObjectId(order_id)},query)
    return redirect("/viewOrders?status=ordered")

@app.route("/markAsReceived1",methods=['post'])
def markAsReceived1():
    order_id = request.form.get("order_id")
    print(order_id)
    query = {"$set": {"status": 'received'}}
    order_collection.update_one({"_id": ObjectId(order_id)}, query)
    return redirect("/viewOrders?status=history")

@app.route("/allOrdersHistory")
def allOrdersHistory():
    orders = order_collection.find({"status":'received'})
    purchases = purchase_collection.find({"status":'received'})
    return render_template("allOrdersHistory.html",orders=orders,purchases=purchases,get_cloth_inventory_by_id=get_cloth_inventory_by_id,get_retailer_by_id=get_retailer_by_id,get_order_item_by_id=get_order_item_by_id,float=float,get_supplier_by_id=get_supplier_by_id,get_purchase_item_by_id=get_purchase_item_by_id)

count = admin_collection.count_documents({"userName":"admin","password":'admin'})
if count == 0:
    admin_collection.insert_one({"userName":'admin',"password":'admin'})




app.run(debug=True)
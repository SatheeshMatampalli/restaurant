import os
import random,string,json
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask import session as login_session
from login_decorator import login_required
from flask import make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from database_setup import *
from flask_login import LoginManager,login_user,current_user,logout_user,login_required


engine = create_engine("sqlite:///restaurantmenu.db",connect_args={'check_same_thread':False},echo=True)
Base.metadata.bind = engine


secret_file = json.loads(open('client_secret.json', 'r').read())
CLIENT_ID = secret_file['web']['client_id']
APPLICATION_NAME='Restaurant'


DBSession = sessionmaker(bind=engine)
session = DBSession()
app=Flask(__name__)
app.config['SECRET_KEY'] = 'e7a9804ba98684deefd88d6a6c8cd0db'


photos =UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/upload_files'
configure_uploads(app, photos)


@app.route('/signup',methods=["GET","POST"])
def signup():
	if request.method == "POST":
		try:
			name=request.form["name"]
			mobile=request.form["mobile"]
			email=request.form["email"]
			address=request.form["address"]
			password=request.form["password"]
			owner = Owner(name=name,
						  mobile=mobile,
						  address=address,
						  email=email,
						  password=password)
			session.add(owner)
			session.commit()
			flash("details saved","info")
			return redirect("/")
		except Exception as e:
			return str(e)
		else:
			pass
	else:
		return render_template('signup.html')



# login routing
@app.route('/login',methods=["GET","POST"])
def login():
	if current_user.is_authenticated:
		flash("already loggedin","danger")
		return redirect(url_for('showRestaurant'))
	try:
		if request.method == "POST":
			owner = session.query(Owner).filter_by(email=request.form['mail'], password=request.form['password']).first()
			if owner:
				login_user(owner)
				next_page=request.args.get('next')
				flash("loggedin successfully","success")
				return redirect(next_page) if next_page else redirect(url_for('showRestaurant'))
			else:
				flash("Login Failed, please check & Try Again ...!","danger")
				return redirect("/login")
		else:
			return render_template("login1.html", title="Login")
	except Exception as e:
		flash("Login Failed,please chack & Try Again ...!","danger")
		return render_template("login1.html", title="Login")
	# else:
	# 	return render_template("login1.html", title="Login")


@app.route('/logout')
def logout():
	logout_user()
	flash("loggedout successfully","success")
	return redirect(url_for('showRestaurant'))



@app.route('/')
@app.route("/restaurants")
def showRestaurant():
	restaurants= session.query(Restaurant).all()
	# ratings=[resturant.ratings.value for restaurant in restaurants]
	ratings=[]
	for restaurant in restaurants:
		values=[]
		for rating in restaurant.ratings:
			values.append(rating.value)
		# print("\n\n\n\n\n",sum(values),sum(values)/len(values))
		if len(values)!=0:
			ratings.append(sum(values)/len(values))
		else:
			ratings.append(0)
	print(ratings)
	return render_template("restaurants.html",myrestaurants=zip(restaurants,ratings))


@app.route("/restaurantsbylocation",methods=["POST","GET"])
def showRestaurantByLocation():
	location = request.form['location']
	restaurants= session.query(Restaurant).filter_by(location=location).all()
	# ratings=[resturant.ratings.value for restaurant in restaurants]
	ratings=[]
	for restaurant in restaurants:
		values=[]
		for rating in restaurant.ratings:
			values.append(rating.value)
		# print("\n\n\n\n\n",sum(values)/len(values))
		if len(values)!=0:
			ratings.append(sum(values)/len(values))
		else:
			ratings.append(0)
	print(ratings)
	return render_template("restaurants.html",myrestaurants=zip(restaurants,ratings))



@app.route('/restaurant/<int:rest_id>')
def restaurantdetails(rest_id):
    restaurant = session.query(Restaurant).get(rest_id)
    return  render_template("restaurantdetails.html",restaurant=restaurant)



@app.route('/addRestaurant',methods=["GET","POST"])
def addRestaurant():
	if request.method == "POST":
		filename= photos.save(request.files['image'])
		restaurant=Restaurant(name=request.form['name'],
							location=request.form['location'],
							address=request.form['address'],
							chairs_2=request.form['chairs_2'],
							chairs_3=request.form['chairs_3'],
							chairs_4=request.form['chairs_4'],
							chairs_8=request.form['chairs_8'],
							image=filename,
							owner_id=current_user.id)



		session.add(restaurant)
		session.commit()
		flash("New Restaurant Created","success")
		return redirect('/restaurants')
	else:
	    return render_template("addRestaurant.html")


@app.route('/addWaiter/<int:rest_id>',methods=["GET","POST"])
def addWaiter(rest_id):
	if request.method == "POST":
		filename= photos.save(request.files['image'])
		waiter=Waiter(name=request.form['name'],
							restaurant_id=request.form['restaurant_id'],
							experience=request.form['experience'],
							image=filename,
							)



		session.add(waiter)
		session.commit()
		flash("New waiter Created","success")
		return redirect('/restaurants')
	else:
		restaurant=session.query(Restaurant).get(rest_id)
		return render_template("addWaiter.html",restaurant=restaurant)

@app.route('/delwaiter/<int:waiter_id>', methods=["GET"] )
def deleteWaiter(waiter_id):
	deleteWaiter = session.query(Waiter).filter_by(id=waiter_id)
	deleteWaiter.delete()
	session.commit()
	flash("Deleted Waiter","info")
	return redirect('/')

@app.route('/editWaiter/<int:waiter_id>',methods=["GET" ,"POST"])
def editWaiter(waiter_id):
	if request.method =="POST":
		if 'photo' in request.files:
			filename=photos.save(request.files['photo'])
			editWaiter = session.query(Waiter).filter_by(id=waiter_id).one()
			editWaiter.name=request.form['name']
			editWaiter.experience=request.form['experience']
						
			editWaiter.image=filename
			session.commit()
			flash("Edited Waiter","success")
			return redirect('/waiters')
		else:
			editWaiter=session.query(Waiter).filter_by(id=waiter_id).one()
			editWaiter.name=request.form['name']
			editWaiter.experience=request.form['experience']
			session.commit()
			flash("Edited Waiter","info")
			return redirect('/')

	else:
		waiter = session.query(Waiter).filter_by(id=waiter_id).one()
		return render_template("editWaiter.html", waiter=waiter)




@app.route('/editRestaurant/<int:rest_id>',methods=["GET" ,"POST"])
def editRestaurant(rest_id):
	if request.method =="POST":
		if 'photo' in request.files:
			filename=photos.save(request.files['photo'])
			editRest = session.query(Restaurant).filter_by(id=rest_id).one()
			editRest.name=request.form['name']
			editRest.location=request.form['location']
			editRest.address=request.form['address']
			
			editRest.image=filename
			session.commit()
			flash("Edited Restaurant","success")
			return redirect('/restaurants')
		else:
			editRest=session.query(Restaurant).filter_by(id=rest_id).one()
			editRest.name=request.form['name']
			editRest.location=request.form['location']
			editRest.address=request.form['address']
			session.commit()
			flash("Edited Restaurant","info")
			return redirect('/restaurants')

	else:
		restaurant = session.query(Restaurant).filter_by(id=rest_id).one()
		return render_template("editRestaurant.html", restaurant=restaurant)

@app.route('/delrestaurant/<int:restaurant_id>', methods=["GET"] )
def deleteRestaurant(restaurant_id):
	deleteRes = session.query(Restaurant).filter_by(id=restaurant_id)
	deleteRes.delete()
	session.commit()
	flash("Deleted Restaurant","info")
	return redirect('/restaurants')


@app.route('/addMenuItem',methods=["GET","POST"])
def addMenuItem():
	if request.method == "POST":
		filename= photos.save(request.files['image'])
		item=MenuItem(name=request.form['name'],
							price=request.form['price'],
							course=request.form['course'],
							image=filename,
							description=request.form['description'],
							restaurant_id=current_user.restaurants[-1].id
							# adding this item into loggedin user recent restaurant
							)



		session.add(item)
		session.commit()
		flash("Item Added","success")
		return redirect('/restaurants')
	else:
	    return render_template("addMenuItem.html")


@app.route("/menuItems/<int:rest_id>")
def menuItems(rest_id):
	items= session.query(MenuItem).filter_by(restaurant_id=rest_id).all()
	return render_template("menuItems.html",items=items)

@app.route('/editItem/<int:item_id>',methods=["GET" ,"POST"])
def editItem(item_id):
	if request.method =="POST":
		if 'photo' in request.files:
			filename=photos.save(request.files['photo'])
			editRest = session.query(MenuItem).filter_by(id=item_id).one()
			editRest.name=request.form['name']
			editRest.price=request.form['price']
			editRest.description=request.form['description']
			editRest.image=filename
			session.commit()
			flash("Edited MenuItem","info")
			return redirect('/restaurants')
		else:
			editRest=session.query(MenuItem).filter_by(id=item_id).one()
			editRest.name=request.form['name']
			editRest.price=request.form['price']
			editRest.description=request.form['description']
			session.commit()
			flash("Edited MenuItem","info")
			return redirect('/restaurants')

	else:
		restaurant = session.query(MenuItem).filter_by(id=item_id).one()
		return render_template("editItem.html", item=restaurant)


@app.route('/deleteItem/<int:item_id>', methods=["GET"] )
def deleteItem(item_id):
	item = session.query(MenuItem).filter_by(id=item_id)
	item.delete()
	session.commit()
	flash("Deleted MenuItem","info")
	return redirect('/restaurants')


@app.route("/waiterinfo/<int:rest_id>")
def waiterinfo(rest_id):
	restaurant = session.query(Restaurant).get(rest_id)
	waiters=restaurant.waiters
	print("\n\n\n\n",len(waiters))
	return render_template("waiters.html",waiters=waiters,restaurant=restaurant)



@app.route("/feedback/<int:rest_id>",methods=["POST","GET"])
def feedback(rest_id):
	restaurant=session.query(Restaurant).get(rest_id)
	if request.method=="POST":
		comment = request.form["comment"]
		rating = request.form["rating"]
		rating=Rating(comment=comment,value=rating,restaurant_id=restaurant.id)
		session.add(rating)
		session.commit()
		flash("review saved","info")
		return redirect("/")
	return render_template("feedback.html")


@app.route("/addtocart/<int:item_id>",methods=["POST","GET"])
def addtocart(item_id):
	item=session.query(MenuItem).get(item_id)
	# print("\n\n\nquantity",request.form['quantity'])
	cart=Cart(quantity=1,
		item=item,
		restaurant=item.restaurant,
		user_id=current_user.id)
	session.add(cart)
	session.commit()
	flash("added into cart","info")
	return redirect("")

@app.route("/showcart",methods=["POST","GET"])
def showcart():
	# user=session.query(Owner).get(current_user.id)
	# user=session.query(Owner).get(1)
	cart_items=current_user.cart_items
	return render_template('showcartitems.html',cart_items=cart_items)


@app.route("/restaurantorders",methods=["POST","GET"])
def restaurantorders():
	# user=session.query(Owner).get(current_user.id)
	# user=session.query(Owner).get(1)
	orders=(session.query(Order)
	        .join(Restaurant)
	        .filter(Restaurant.owner_id == current_user.id)
	        ).all()
	print(orders)
	# orders=session.query(Order).filter_by(restaurant_id=current_user.restaurants[-1].id).all()
	#we need to get all restaurnts of loggedin restaurant user
	return render_template('restaurantorders.html',orders=orders)


@app.route('/home')
def home():
	return render_template('parent.html')

@app.route("/myorders",methods=["POST","GET"])
def myorders():
	# user=session.query(Owner).get(current_user.id)
	# user=session.query(Owner).get(1)
	orders=session.query(Order).filter_by(user_id=current_user.id).all()
	#we need to get all restaurnts of loggedin restaurant user
	return render_template('showorders.html',orders=orders)

@app.route("/cartdelete/<int:id>",methods=["POST","GET"])
def cartdelete(id):
	# user=session.query(Owner).get(current_user.id)
	cart_item=session.query(Cart).filter_by(id=id)
	# user=session.query(Owner).get(1)
	cart_item.delete()
	session.commit()
	return redirect("/showcart")  

@app.route("/cartdeleteall/",methods=["POST","GET"])
def cartdeleteall():
	# user=session.query(Owner).get(current_user.id)
	cart_items=session.query(Cart).filter_by(user_id=current_user.id).all()
	# user=session.query(Owner).get(1)
	for item in cart_items:
		item=session.query(Cart).filter_by(id=item.id)
		item.delete()
	session.commit()
	return redirect("/myorders")

@app.route("/carttoorder/",methods=["POST","GET"])
def carttoorder():
	# item=session.query(MenuItem).get(item_id)
	cart_items=session.query(Cart).filter_by(user_id=current_user.id).all()
	for item in cart_items:
		# cartdelete(item.id)
		order=Order(quantity=item.quantity,
					item=item.item,
					restaurant=item.restaurant,
					user_id=item.user_id)
		session.add(order)
	session.commit( )
	flash("Order Booked","info")
	return redirect("/cartdeleteall/")

@app.route('/reservedelete/<int:id>/reserve', methods=['GET','POST'])
def reservedelete(id):
	table=session.query(ReserveTable).filter_by(id=id)
	table.delete()
	session.commit()
	flash("table cleared","success")
	return redirect("/")


@app.route('/restaurant/<int:res_id>/reserve_details', methods=['GET','POST'])
def reserve_details(res_id):
    restObj = session.query(Restaurant).filter_by(id=res_id).one_or_none()
    if not restObj:
        flash('No restaurant found')
        return redirect(url_for('home'))    
    if request.method == "GET":
    	print("\n\n\n\n\nchairs_2:",restObj.name,restObj.chairs_2)
    	chairs_2 = restObj.chairs_2
    	chairs_3 = restObj.chairs_3
    	chairs_4 = restObj.chairs_4
    	chairs_8 = restObj.chairs_8
    	print('ayyappa',type(chairs_8),chairs_8)
    	restaurant=session.query(Restaurant).get(res_id)
    	res_tables=[obj.reserved_table_name.replace('C',"") for obj in restaurant.reserved_tables]
    	return render_template(
            "reservedetails.html",
            chairs_2= chairs_2,
            chairs_3=chairs_3,
            chairs_4=chairs_4,
            chairs_8=chairs_8,
            restaurant_id=res_id,reserved_tables=res_tables,res_objects=restaurant.reserved_tables
            )



@app.route('/restaurant/<int:res_id>/reserve', methods=['GET','POST'])
def reserve(res_id):
    restObj = session.query(Restaurant).filter_by(id=res_id).one_or_none()
    if not restObj:
        flash('No restaurant found')
        return redirect(url_for('home'))    
    if request.method == "GET":
    	print("\n\n\n\n\nchairs_2:",restObj.name,restObj.chairs_2)
    	chairs_2 = restObj.chairs_2
    	chairs_3 = restObj.chairs_3
    	chairs_4 = restObj.chairs_4
    	chairs_8 = restObj.chairs_8
    	print('ayyappa',type(chairs_8),chairs_8)
    	restaurant=session.query(Restaurant).get(res_id)
    	res_tables=[obj.reserved_table_name.replace('C',"") for obj in restaurant.reserved_tables]
    	return render_template(
            "reserve.html",
            chairs_2= chairs_2,
            chairs_3=chairs_3,
            chairs_4=chairs_4,
            chairs_8=chairs_8,
            restaurant_id=res_id,reserved_tables=res_tables,res_objects=restaurant.reserved_tables
            )
    if request.method == "POST":
        items = request.form
        print('\n'*5,items,dir(items))
        finalList=[]
        rest_id = request.form['rest_id']
        for k in items:
            if k.startswith('ch_chairs2_') and items[k]=="OK":
                sp = k.split('_')[-1]
                value = '2C_'+str(sp)
                finalList.append(value)
            if k.startswith('ch_chairs3_') and items[k]=="OK":
                sp = k.split('_')[-1]
                value = '3C_'+str(sp)
                finalList.append(value)
            if k.startswith('ch_chairs4_') and items[k]=="OK":
                sp = k.split('_')[-1]
                value = '4C_'+str(sp)
                finalList.append(value)
            if k.startswith('ch_chairs8_') and items[k]=="OK":
                sp = k.split('_')[-1]
                value = '8C_'+str(sp)
                finalList.append(value)
        date_time=request.form["time"]
        print("\n\n\n\n\n",date_time,"\n\n\n")
        for each in finalList:
            session.add(ReserveTable(
                user=current_user,
                reserved_table_name = each,
                restaurant_id= rest_id,
                date_time= date_time
                )
            )
        if finalList:
            session.commit()
        print('final','\n'*3,finalList)
        flash('successfully reseved',"success")
    return redirect('/')


app.jinja_env.globals.update(sum=sum,len=len,round=round,int=int)

if __name__=="__main__":
	app.config['SECRET_KEY']='priya varma'

	login_manager=LoginManager(app)
	login_manager.login_view='login'
	login_manager.login_message_category='info'

	@login_manager.user_loader
	def load_user(user_id):
		return session.query(Owner).get(int(user_id))
	app.debug = True
	app.run(host = '0.0.0.0',port = 5000)
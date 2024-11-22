import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

current_dir = os.path.abspath(os.path.dirname( __file__ ))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(current_dir,'Household_services.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

aEmail="admin12@mail.com"
aPass="admin123"

class Service(db.Model):
    __tablename__= "services"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    time_reqd = db.Column(db.String)
    description = db.Column(db.String)

class Professional(db.Model):
    __tablename__="professionals"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    passw = db.Column(db.String, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    service_name = db.Column(db.String, nullable=False)
    experience = db.Column(db.Integer)
    address = db.Column(db.String)
    pincode = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)

class Customer(db.Model):
    __tablename__="customers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    passw = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    pincode = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)

class Service_Request(db.Model):
    __tablename__="service_requests"
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    cust_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    prof_id = db.Column(db.Integer, db.ForeignKey('professionals.id'), nullable=False)
    status = db.Column(db.String, nullable=False)

@app.route('/', methods=['GET','POST'])
def sign_in():
    if request.method=='POST':
        email=request.form['email']
        passw=request.form['pass']
        user=request.form.get('user')
        var=''

        if(email==aEmail and passw==aPass):
            return redirect('/admin/home')
        
        elif(user=='professional'):
            prof=Professional.query.filter_by(email=email).first()
            if(prof):
                if(passw==prof.passw):
                    return redirect(url_for('prof_home',id=prof.id))
                else:
                    var='w_pass'
                    return render_template('index.html', var=var)
            else:
                var='register'
                return render_template('index.html', var=var)

        elif(user=='customer'):
            cust=Customer.query.filter_by(email=email).first()
            if(cust):
                if(passw==cust.passw):
                    return redirect(url_for('customer_home', id=cust.id))
                else:
                    var='w_pass'
                    return render_template('index.html', var=var)
            else:
                var='register'
                return render_template('index.html', var=var)
        
    return render_template('index.html')

@app.route('/customer/signup', methods=['GET','POST'])
def signup():
    var=False
    
    if (request.method=='POST'):
       
        email=request.form['email']
        passw=request.form['pass']
        name=request.form['name']
        add=request.form['add']
        pin=request.form['pin']
        
        customer=Customer.query.filter_by(email=email).first()
        if(customer):
            var=True
            return render_template('register_customer.html', var=var)
        
        new_cust=Customer(name=name,email=email,passw=passw,address=add,pincode=pin,status='working')
        
        db.session.add(new_cust)
        db.session.commit()
        
        return redirect('/')
    
    return render_template('register_customer.html', var=var)

@app.route('/professional/register', methods=['GET','POST'])
def prof_register():
    services=Service.query.all()
    var=''
    
    if(request.method=='POST'):
        email=request.form['email']
        passw=request.form['pass']
        name=request.form['name']
        service_id=request.form.get('services')
        exp=request.form['exp']
        docs=request.files['docs']
        add=request.form['add']
        pin=request.form['pin']

        docs_name=(docs.filename).split('.')
        if(docs_name[1]!='pdf'):
            var='file'
            return render_template('register_professional.html', services=services, var=var)

        prof=Professional.query.filter_by(email=email).first()
        if(prof):
            var='mail'
            return render_template('register_professional.html', services=services, var=var)
        
        service=Service.query.filter_by(id=service_id).first()
        status='Approval Pending'
        
        new_prof=Professional(id=2,email=email,passw=passw,name=name,
                              service_id=service.id,
                              service_name=service.name,
                              experience=exp,
                              address=add,
                              pincode=pin, 
                              status=status)
        
        db.session.add(new_prof)
        db.session.commit()

        docs_name=f'{new_prof.id}.pdf'
        docs_path=os.path.join('static','docs',docs_name)
        docs.save(docs_path)
        
        return redirect('/')

    return render_template('register_professional.html', services=services, var=var)

@app.route('/admin/home', methods=['GET','POST'])
def admin_home():
    services=Service.query.all()
    profs=Professional.query.all()
    reqs=Service_Request.query.all()
    customers=Customer.query.all()

    return render_template('admin_home.html',services=services,profs=profs,reqs=reqs,customers=customers)

@app.route('/admin/createService', methods=['GET','POST'])
def create_service():
    var=False
    
    if request.method=='POST':
        name=request.form['name']
        type=request.form['type']
        price=request.form['price']
        time=request.form['time']
        desc=request.form['desc']

        service=Service.query.filter_by(name=name).first()
        if(service):
            var=True
            return render_template('create_service.html',var=var)
        
        new_service=Service(id=2,name=name,type=type,price=price,time_reqd=time,description=desc)
        db.session.add(new_service)
        db.session.commit()
        
        return redirect('/admin/home')

    return render_template('create_service.html',var=var)

@app.route('/admin/deleteService/<int:id>')
def delete_service(id):
    service=Service.query.filter_by(id=id).first()
    db.session.delete(service)
    db.session.commit()
    return redirect('/admin/home')

@app.route('/admin/editService/<int:id>', methods=['GET','POST'])
def edit_service(id):
    service=Service.query.filter_by(id=id).first()

    if request.method=='POST':
        name=request.form['name']
        price=request.form['price']
        time=request.form['time']
        desc=request.form['desc']

        service.name=name
        service.price=price
        service.time_reqd=time
        service.description=desc

        db.session.add(service)
        db.session.commit()

        return redirect('/admin/home')

    return render_template('edit_service.html',service=service)

@app.route('/admin/approveProfessional/<int:id>')
def approve_prof(id):
    prof=Professional.query.filter_by(id=id).first()
    prof.status='Approved'

    db.session.add(prof)
    db.session.commit()

    return redirect('/admin/home')

@app.route('/admin/rejectProfessional/<int:id>')
def reject_prof(id):
    prof=Professional.query.filter_by(id=id).first()
    prof.status='Rejected'

    db.session.add(prof)
    db.session.commit()

    return redirect('/admin/home')

@app.route('/admin/blockProfessional/<int:id>')
def block_prof(id):
    prof=Professional.query.filter_by(id=id).first()
    prof.status='Blocked'

    db.session.add(prof)
    db.session.commit()

    return redirect('/admin/home')

@app.route('/admin/blockCustomer/<int:id>')
def block_cust(id):
    cust=Customer.query.filter_by(id=id).first()
    cust.status='Blocked'

    db.session.add(cust)
    db.session.commit()

    return redirect('/admin/home')


@app.route('/admin/search', methods=['GET','POST'])
def admin_search():
    if request.method=='POST':
        var=request.form.get('db')
        key=request.form['key']
        data=[]
        
        if(var=='service'):
            data=Service.query.filter(
                or_(
                    Service.name.ilike(f'%{key}%'),
                    Service.type.ilike(f'%{key}%'),
                    Service.price.ilike(f'%{key}%'),
                    Service.time_reqd.ilike(f'%{key}%'),
                    Service.description.ilike(f'%{key}%')
                )
            ).all()
        
            return render_template('admin_search.html',var=var, services=data)
        elif(var=='prof'):
            data=Professional.query.filter(
                or_(
                    Professional.name.ilike(f'%{key}%'),
                    Professional.email.ilike(f'%{key}%'),
                    Professional.service_name.ilike(f'%{key}%'),
                    Professional.experience.ilike(f'%{key}%'),
                    Professional.address.ilike(f'%{key}%'),
                    Professional.pincode.ilike(f'%{key}%'),
                    Professional.status.ilike(f'%{key}%')
                )
            ).all()

            return render_template('admin_search.html', var=var, profs=data)
        
        elif(var=='req'):
            data=Service_Request.query.filter(
                or_(
                    Service_Request.service_id.ilike(f'%{key}%'),
                    Service_Request.prof_id.ilike(f'%{key}%'),
                    Service_Request.cust_id.ilike(f'%{key}%'),
                    Service_Request.status.ilike(f'%{key}%')
                )
            ).all()

            return render_template('admin_search.html', var=var, reqs=data)
        
        else:
            data=Customer.query.filter(
                or_(
                    Customer.name.ilike(f'%{key}%'),
                    Customer.email.ilike(f'%{key}%'),
                    Customer.address.ilike(f'%{key}%'),
                    Customer.pincode.ilike(f'%{key}%'),
                    Customer.status.ilike(f'%{key}%'),
                )
            ).all()

            return render_template('admin_search.html', var=var, customers=data)

    return render_template('admin_search.html')

@app.route('/prof/<int:id>/home')
def prof_home(id):
    prof=Professional.query.filter_by(id=id).first()
    reqs=Service_Request.query.filter_by(status="requested", service_id=prof.service_id).all()
    preqs=Service_Request.query.filter_by(prof_id=id, status="pending").all()
    customers=Customer.query.all()
    creqs=Service_Request.query.filter_by(prof_id=id, status="completed").all()
    Oreqs=[]
    Creqs=[]
    
    for customer in customers:
        for req in reqs:
            if(req.cust_id==customer.id):
                Oreqs.append((req,customer))
        
        for req in creqs:
            if(req.cust_id==customer.id):
                Creqs.append((req,customer))
    
    for req in preqs:
        for customer in customers:
            if(req.cust_id==customer.id):
                Oreqs.append((req,customer))
    
    return render_template('prof_home.html', prof=prof,open_reqs=Oreqs,closed_reqs=Creqs)

@app.route('/prof/<int:prof_id>/acceptRequest/<int:req_id>')
def accept_req(prof_id,req_id):
    req=Service_Request.query.filter_by(id=req_id).first()
    req.prof_id=prof_id
    req.status='pending'

    db.session.add(req)
    db.session.commit()

    return redirect(url_for('prof_home',id=prof_id))

@app.route('/prof/<int:id>/search', methods=['GET','POST'])
def search_prof(id):
    prof=Professional.query.filter_by(id=id).first()
    
    if(request.method=='POST'):
        var=request.form.get('db')
        key=request.form['key']

        if(var=='status'):
            stat_reqs=Service_Request.query.filter(Service_Request.status.ilike(f'%{key}%')).all()
            custs=Customer.query.all()
            preqs=[]
            reqs=[]
            
            for req in stat_reqs:
                if(req.prof_id==id):
                    preqs.append(req)

            for req in preqs:
                for cust in custs:
                    if(req.cust_id==cust.id):
                        reqs.append((req,cust))
            
            return render_template('prof_search.html',prof=prof,var=var,reqs=reqs)
        
        else:
            customers=Customer.query.filter(
                or_(
                    Customer.name.ilike(f'%{key}%'),
                    Customer.email.ilike(f'%{key}%'),
                    Customer.address.ilike(f'%{key}%'),
                    Customer.pincode.ilike(f'%{key}%')
                )
            ).all()
            O_pen_reqs=Service_Request.query.filter_by(status='pending', prof_id=id).all()
            O_req_reqs=Service_Request.query.filter_by(status='requested', service_id=prof.service_id).all()
            Oreqs=O_req_reqs+O_pen_reqs
            Creqs=Service_Request.query.filter_by(status='completed', prof_id=id).all()

            open_reqs=[]
            closed_reqs=[]

            for customer in customers:
                for req in Oreqs:
                    if(customer.id==req.cust_id):
                        open_reqs.append((req,customer))

                for req in Creqs:
                    if(customer.id==req.cust_id):
                        closed_reqs.append((req, customer))

            return render_template('prof_search.html',prof=prof,var=var,open_reqs=open_reqs,closed_reqs=closed_reqs)

    
    return render_template('prof_search.html', prof=prof)

@app.route('/customer/<int:id>/home')
def customer_home(id):
    cust=Customer.query.filter_by(id=id).first()
    reqs=Service_Request.query.filter_by(cust_id=cust.id).all()
    profs=Professional.query.all()
    services=[]

    for req in reqs:
        flag=False
        service=Service.query.filter_by(id=req.service_id).first()
        for prof in profs:
            if(req.prof_id==prof.id):
                services.append((req,prof,service))
                flag=True
        if(not flag):
            services.append((req,'-',service))
    
    return render_template('customer_home.html', cust=cust, services=services)

@app.route('/<int:id>/service/<string:service>')
def customer_service(id,service):
    cust=Customer.query.filter_by(id=id).first()
    services_by_type=Service.query.filter_by(type=service).all()
    reqs=Service_Request.query.filter_by(cust_id=cust.id).all()
    profs=Professional.query.all()
    services=[]

    for req in reqs:
        flag=False
        ser=Service.query.filter_by(id=req.service_id).first()
        for prof in profs:
            if(req.prof_id==prof.id):
                services.append((req,prof,ser))
                flag=True
        if(not flag):
            services.append((req,'-',ser))

    return render_template('customer_home.html',cust=cust, services=services, packs=services_by_type, service=service.capitalize())

@app.route('/<int:cust_id>/close_service/<int:req_id>')
def close_service(cust_id,req_id):
    req=Service_Request.query.filter_by(id=req_id).first()
    req.status='completed'

    db.session.add(req)
    db.session.commit()

    return redirect(url_for('customer_home',id=cust_id))

@app.route('/<int:cust_id>/service/<int:service_id>')
def book_service(cust_id, service_id):
    req=Service_Request(id=2,service_id=service_id,cust_id=cust_id,status='requested')

    db.session.add(req)
    db.session.commit()

    return redirect(url_for('customer_home',id=cust_id))

@app.route('/customer/<int:cust_id>/search', methods=['GET','POST'])
def customer_search(cust_id):
    cust=Customer.query.filter_by(id=cust_id).first()

    if(request.method=='POST'):
        var=True
        key=request.form['key']

        services=Service.query.filter(
            or_(
                Service.name.ilike(f'%{key}%'),
                Service.type.ilike(f'%{key}%'),
                Service.price.ilike(f'%{key}%'),
                Service.time_reqd.ilike(f'%{key}%'),
                Service.description.ilike(f'%{key}%')
            )
        ).all()
        
        return render_template('customer_search.html', cust=cust, packs=services, var=var)

    return render_template('customer_search.html', cust=cust)

if __name__ == '__main__':
    app.run(debug=True)
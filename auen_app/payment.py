from flask import Blueprint, request, redirect, render_template, url_for
from flask_login import login_required, current_user
from .models import Subscriptions
from . import db
import stripe

payment = Blueprint('payment', __name__)

stripe.api_key = "sk_test_51IwAV3DCfpIT9YMsK88FDdE4Ib6IjMvhV7LhgzktmOeIDpO6qGjqkRzfwWa0Xml5g2S7MaD8CjTuHqQIwEg1dJDI00zb0egpxH"

@payment.route('/create_checkout_session', methods=["GET", "POST"])
@login_required
def create_checkout_session():
    checkout_session = stripe.checkout.Session.create(
        line_items =  [ 
            {
                'price': 'price_1NE7BWDCfpIT9YMswgYvapGz',
                'quantity': 1
            }
        ],
        mode="subscription",
        success_url = "http://127.0.0.1:5000/save_checkout",
        cancel_url = "http://127.0.0.1:5000/"
    )   
    return redirect(checkout_session.url, code=303)

@payment.route('/save_checkout', methods=["GET", "POST"])
@login_required
def save_checkout():
    subscription = Subscriptions(user_id = current_user.id)    
    db.session.add(subscription)
    db.session.commit()

    return redirect(url_for('main.profile'))

@payment.route('/delete_subscription', methods=["GET", "POSt"])
@login_required
def delete_subscription():
    unsubscribe = Subscriptions.query.filter_by(user_id=current_user.id).first()

    db.session.delete(unsubscribe)
    db.session.commit()

    return redirect(url_for('main.profile'))


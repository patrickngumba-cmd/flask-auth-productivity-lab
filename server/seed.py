#!/usr/bin/env python3

from config import app, db
from models import User, Note

with app.app_context():
    print("Clearing existing records...")
    Note.query.delete()
    User.query.delete()
    db.session.commit()

    print("Creating users...")
    user1 = User(username="patrick_n")
    user1.password_hash = "password123"

    user2 = User(username="amina_k")
    user2.password_hash = "securepass"

    db.session.add_all([user1, user2])
    db.session.commit()

    print("Creating starter notes...")
    notes = [
        Note(title="Q4 Marketing Activation", content="Finalize WhatsApp campaign list and showroom follow-ups.", user_id=user1.id),
        Note(title="Showroom Inventory Check", content="Verify quartz slab stock levels before Monday.", user_id=user1.id),
        Note(title="Flask API Study Plan", content="Review session authentication and pagination queries.", user_id=user1.id),
        Note(title="Supplier Call Notes", content="Confirm delivery schedule for new countertop samples.", user_id=user1.id),
        Note(title="Weekend Errands", content="Pick up groceries and renew gym membership.", user_id=user1.id),
        Note(title="Client Proposal Draft", content="Prepare cost breakdown for commercial fitting project.", user_id=user1.id),
        Note(title="Amina's Private Note", content="Personal project roadmap for November.", user_id=user2.id),
        Note(title="Team Sync Agenda", content="Discuss customer engagement metrics and feedback.", user_id=user2.id),
    ]

    db.session.add_all(notes)
    db.session.commit()
    print("Database seeded successfully!")

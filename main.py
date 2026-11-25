from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import SessionLocal
import models
from schemas import (
    UserCreate,
    EventCreate,
    RegistrationCreate,
    AttendanceCreate,
    LoginRequest,
    NotificationCreate
)

from qr_code import generate_qr


# ==================================================
# CREATE FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="AI Event Management System",
    description="AI-Assisted Smart Event Management & Collaboration Platform",
    version="1.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ==================================================
# QR CODE STATIC FILES
# ==================================================

app.mount(
    "/qr",
    StaticFiles(directory="generated_qr"),
    name="qr"
)


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message": "AI Event Management System is running!"
    }


# ==================================================
# DATABASE TEST
# ==================================================

@app.get("/db-test")
def database_test():

    db = SessionLocal()

    try:

        db.execute(
            models.User.__table__.select().limit(1)
        )

        return {
            "success": True,
            "message": "Database connection successful!"
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }

    finally:

        db.close()


# ==================================================
# CREATE USER
# ==================================================

@app.post("/users")
def create_user(
    user: UserCreate
):

    db = SessionLocal()


    # ----------------------------------------------
    # CHECK IF EMAIL ALREADY EXISTS
    # ----------------------------------------------

    existing_user = db.query(
        models.User
    ).filter(
        models.User.email == user.email
    ).first()


    if existing_user is not None:

        db.close()

        return {
            "success": False,
            "message": "Email already registered"
        }


    # ----------------------------------------------
    # CREATE USER
    # ----------------------------------------------

    new_user = models.User(

        name=user.name,

        email=user.email,

        password=user.password,

        role=user.role

    )


    db.add(new_user)

    db.commit()

    db.refresh(new_user)


    user_id = new_user.id

    db.close()


    return {

        "success": True,

        "message": "User created successfully!",

        "user_id": user_id

    }


# ==================================================
# GET ALL USERS
# ==================================================

@app.get("/users")
def get_users():

    db = SessionLocal()

    users = db.query(
        models.User
    ).all()


    result = []


    for user in users:

        result.append({

            "id": user.id,

            "name": user.name,

            "email": user.email,

            "role": user.role

        })


    db.close()


    return result


# ==================================================
# LOGIN
# ==================================================

@app.post("/login")
def login(
    login_data: LoginRequest
):

    db = SessionLocal()


    # ----------------------------------------------
    # FIND USER
    # ----------------------------------------------

    user = db.query(
        models.User
    ).filter(
        models.User.email == login_data.email
    ).first()


    # ----------------------------------------------
    # USER NOT FOUND
    # ----------------------------------------------

    if user is None:

        db.close()

        return {

            "success": False,

            "message": "Invalid email or password"

        }


    # ----------------------------------------------
    # CHECK PASSWORD
    # ----------------------------------------------

    if user.password != login_data.password:

        db.close()

        return {

            "success": False,

            "message": "Invalid email or password"

        }


    # ----------------------------------------------
    # LOGIN SUCCESS
    # ----------------------------------------------

    db.close()


    return {

        "success": True,

        "message": "Login successful!",

        "user_id": user.id,

        "name": user.name,

        "email": user.email,

        "role": user.role

    }


# ==================================================
# CREATE EVENT
# ==================================================

@app.post("/events")
def create_event(
    event: EventCreate
):

    db = SessionLocal()


    new_event = models.Event(

        title=event.title,

        description=event.description,

        date=event.date,

        time=event.time,

        location=event.location

    )


    db.add(new_event)

    db.commit()

    db.refresh(new_event)


    event_id = new_event.id

    db.close()


    return {

        "success": True,

        "message": "Event created successfully!",

        "event_id": event_id

    }


# ==================================================
# GET ALL EVENTS
# ==================================================

@app.get("/events")
def get_events():

    db = SessionLocal()


    events = db.query(
        models.Event
    ).all()


    result = []


    for event in events:

        result.append({

            "id": event.id,

            "title": event.title,

            "description": event.description,

            "date": event.date,

            "time": event.time,

            "location": event.location

        })


    db.close()


    return result


# ==================================================
# REGISTER FOR EVENT
# ==================================================

@app.post("/registrations")
def create_registration(
    registration: RegistrationCreate
):

    db = SessionLocal()


    # ----------------------------------------------
    # CHECK USER
    # ----------------------------------------------

    user = db.query(
        models.User
    ).filter(
        models.User.id == registration.user_id
    ).first()


    if user is None:

        db.close()

        return {

            "success": False,

            "message": "User not found"

        }


    # ----------------------------------------------
    # CHECK EVENT
    # ----------------------------------------------

    event = db.query(
        models.Event
    ).filter(
        models.Event.id == registration.event_id
    ).first()


    if event is None:

        db.close()

        return {

            "success": False,

            "message": "Event not found"

        }


    # ----------------------------------------------
    # CHECK DUPLICATE REGISTRATION
    # ----------------------------------------------

    existing_registration = db.query(
        models.Registration
    ).filter(

        models.Registration.user_id ==
        registration.user_id,

        models.Registration.event_id ==
        registration.event_id

    ).first()


    if existing_registration is not None:

        db.close()

        return {

            "success": False,

            "message": "User already registered for this event",

            "registration_id":
                existing_registration.id

        }


    # ----------------------------------------------
    # CREATE REGISTRATION
    # ----------------------------------------------

    new_registration = models.Registration(

        user_id=registration.user_id,

        event_id=registration.event_id

    )


    db.add(new_registration)

    db.commit()

    db.refresh(new_registration)


    registration_id = new_registration.id


    # ----------------------------------------------
    # GENERATE QR CODE
    # ----------------------------------------------

    qr_file = generate_qr(
        registration_id
    )


    db.close()


    return {

        "success": True,

        "message": "Registration successful!",

        "registration_id":
            registration_id,

        "qr_file":
            qr_file

    }


# ==================================================
# GET ALL REGISTRATIONS
# ==================================================

@app.get("/registrations")
def get_registrations():

    db = SessionLocal()


    registrations = db.query(
        models.Registration
    ).all()


    result = []


    for registration in registrations:

        result.append({

            "id":
                registration.id,

            "user_id":
                registration.user_id,

            "event_id":
                registration.event_id

        })


    db.close()


    return result


# ==================================================
# MARK ATTENDANCE
# ==================================================

@app.post("/attendance")
def mark_attendance(
    attendance: AttendanceCreate
):

    db = SessionLocal()


    # ----------------------------------------------
    # CHECK REGISTRATION
    # ----------------------------------------------

    registration = db.query(
        models.Registration
    ).filter(
        models.Registration.id ==
        attendance.registration_id
    ).first()


    if registration is None:

        db.close()

        return {

            "success": False,

            "message":
                "Registration not found"

        }


    # ----------------------------------------------
    # CHECK DUPLICATE ATTENDANCE
    # ----------------------------------------------

    existing_attendance = db.query(
        models.Attendance
    ).filter(
        models.Attendance.registration_id ==
        attendance.registration_id
    ).first()


    if existing_attendance is not None:

        db.close()

        return {

            "success": False,

            "message":
                "Attendance already marked for this registration"

        }


    # ----------------------------------------------
    # CREATE ATTENDANCE
    # ----------------------------------------------

    new_attendance = models.Attendance(

        registration_id=
            attendance.registration_id,

        status=
            attendance.status

    )


    db.add(new_attendance)

    db.commit()

    db.refresh(new_attendance)


    attendance_id = new_attendance.id


    db.close()


    return {

        "success": True,

        "message":
            "Attendance marked successfully!",

        "attendance_id":
            attendance_id

    }


# ==================================================
# GET ALL ATTENDANCE
# ==================================================

@app.get("/attendance")
def get_attendance():

    db = SessionLocal()


    attendance_records = db.query(
        models.Attendance
    ).all()


    result = []


    for attendance in attendance_records:

        result.append({

            "id":
                attendance.id,

            "registration_id":
                attendance.registration_id,

            "status":
                attendance.status

        })


    db.close()


    return result


# ==================================================
# DASHBOARD
# ==================================================

@app.get("/dashboard")
def get_dashboard():

    db = SessionLocal()


    # ----------------------------------------------
    # OVERALL STATISTICS
    # ----------------------------------------------

    total_events = db.query(
        models.Event
    ).count()


    total_registrations = db.query(
        models.Registration
    ).count()


    total_attendance = db.query(
        models.Attendance
    ).filter(
        models.Attendance.status == "PRESENT"
    ).count()


    # ----------------------------------------------
    # OVERALL ATTENDANCE PERCENTAGE
    # ----------------------------------------------

    if total_registrations > 0:

        attendance_percentage = (

            total_attendance /
            total_registrations

        ) * 100

    else:

        attendance_percentage = 0


    # ----------------------------------------------
    # EVENT STATISTICS
    # ----------------------------------------------

    event_statistics = []


    all_events = db.query(
        models.Event
    ).all()


    for event in all_events:


        # ------------------------------------------
        # EVENT REGISTRATIONS
        # ------------------------------------------

        event_registrations = db.query(
            models.Registration
        ).filter(
            models.Registration.event_id ==
            event.id
        ).count()


        # ------------------------------------------
        # EVENT ATTENDANCE
        # ------------------------------------------

        event_attendance = db.query(
            models.Attendance
        ).join(
            models.Registration,

            models.Attendance.registration_id ==
            models.Registration.id

        ).filter(

            models.Registration.event_id ==
            event.id,

            models.Attendance.status ==
            "PRESENT"

        ).count()


        # ------------------------------------------
        # EVENT ATTENDANCE PERCENTAGE
        # ------------------------------------------

        if event_registrations > 0:

            event_attendance_percentage = (

                event_attendance /
                event_registrations

            ) * 100

        else:

            event_attendance_percentage = 0


        # ------------------------------------------
        # ADD EVENT STATISTICS
        # ------------------------------------------

        event_statistics.append({

            "event_id":
                event.id,

            "title":
                event.title,

            "date":
                event.date,

            "location":
                event.location,

            "registrations":
                event_registrations,

            "attendance":
                event_attendance,

            "attendance_percentage":
                round(
                    event_attendance_percentage,
                    2
                )

        })


    db.close()


    # ----------------------------------------------
    # DASHBOARD RESPONSE
    # ----------------------------------------------

    return {

        "total_events":
            total_events,

        "total_registrations":
            total_registrations,

        "total_attendance":
            total_attendance,

        "attendance_percentage":
            round(
                attendance_percentage,
                2
            ),

        "event_statistics":
            event_statistics

    }
# ==================================================
# AI EVENT ANALYSIS
# ==================================================

@app.get("/ai-analysis")
def ai_event_analysis():

    db = SessionLocal()

    # ----------------------------------------------
    # GET TOTAL DATA
    # ----------------------------------------------

    total_events = db.query(
        models.Event
    ).count()

    total_registrations = db.query(
        models.Registration
    ).count()

    total_attendance = db.query(
        models.Attendance
    ).filter(
        models.Attendance.status == "PRESENT"
    ).count()


    # ----------------------------------------------
    # CALCULATE ATTENDANCE PERCENTAGE
    # ----------------------------------------------

    if total_registrations > 0:

        attendance_percentage = (
            total_attendance /
            total_registrations
        ) * 100

    else:

        attendance_percentage = 0


    # ----------------------------------------------
    # AI-STYLE ANALYSIS
    # ----------------------------------------------

    if attendance_percentage >= 80:

        participation_level = "Excellent"

        suggestion = (
            "Event participation is very good. "
            "Continue using the current registration "
            "and attendance process."
        )

    elif attendance_percentage >= 60:

        participation_level = "Good"

        suggestion = (
            "Participation is good. "
            "Send reminder notifications before the event "
            "to improve attendance."
        )

    elif attendance_percentage >= 40:

        participation_level = "Average"

        suggestion = (
            "Attendance is moderate. "
            "Consider sending multiple reminders and "
            "improving event promotion."
        )

    else:

        participation_level = "Low"

        suggestion = (
            "Attendance is low. "
            "Consider stronger event promotion, "
            "reminder notifications, and easier registration."
        )


    # ----------------------------------------------
    # CLOSE DATABASE
    # ----------------------------------------------

    db.close()


    # ----------------------------------------------
    # RETURN AI ANALYSIS
    # ----------------------------------------------

    return {

        "total_events":
            total_events,

        "total_registrations":
            total_registrations,

        "total_attendance":
            total_attendance,

        "attendance_percentage":
            round(
                attendance_percentage,
                2
            ),

        "participation_level":
            participation_level,

        "suggestion":
            suggestion

    }
# ==================================================
# AI ANALYSIS FOR INDIVIDUAL EVENT
# ==================================================

@app.get("/ai-analysis/{event_id}")
def ai_analysis_for_event(event_id: int):

    db = SessionLocal()

    # ----------------------------------------------
    # FIND EVENT
    # ----------------------------------------------

    event = db.query(
        models.Event
    ).filter(
        models.Event.id == event_id
    ).first()


    if event is None:

        db.close()

        return {
            "success": False,
            "message": "Event not found"
        }


    # ----------------------------------------------
    # COUNT REGISTRATIONS
    # ----------------------------------------------

    total_registrations = db.query(
        models.Registration
    ).filter(
        models.Registration.event_id == event_id
    ).count()


    # ----------------------------------------------
    # COUNT ATTENDANCE
    # ----------------------------------------------

    total_attendance = db.query(
        models.Attendance
    ).join(
        models.Registration,
        models.Attendance.registration_id ==
        models.Registration.id
    ).filter(
        models.Registration.event_id == event_id,
        models.Attendance.status == "PRESENT"
    ).count()


    # ----------------------------------------------
    # CALCULATE ATTENDANCE
    # ----------------------------------------------

    if total_registrations > 0:

        attendance_percentage = (
            total_attendance /
            total_registrations
        ) * 100

    else:

        attendance_percentage = 0


    # ----------------------------------------------
    # AI-ASSISTED ANALYSIS
    # ----------------------------------------------

    if total_registrations == 0:

        participation_level = "No Data"

        insight = (
            "No participants have registered for this "
            "event yet."
        )

        recommendation = (
            "Promote the event and encourage students "
            "to register."
        )


    elif attendance_percentage >= 80:

        participation_level = "Excellent"

        insight = (
            "This event has excellent participant "
            "attendance."
        )

        recommendation = (
            "Maintain the current registration and "
            "communication strategy."
        )


    elif attendance_percentage >= 60:

        participation_level = "Good"

        insight = (
            "This event has good participant attendance."
        )

        recommendation = (
            "Send reminder notifications before the event "
            "to improve attendance further."
        )


    elif attendance_percentage >= 40:

        participation_level = "Average"

        insight = (
            "This event has moderate participant "
            "attendance."
        )

        recommendation = (
            "Improve event promotion and send additional "
            "reminders to registered participants."
        )


    else:

        participation_level = "Low"

        insight = (
            "This event has low participant attendance."
        )

        recommendation = (
            "Increase event promotion and send reminder "
            "notifications to registered participants."
        )


    # ----------------------------------------------
    # CLOSE DATABASE
    # ----------------------------------------------

    db.close()


    # ----------------------------------------------
    # RETURN RESULT
    # ----------------------------------------------

    return {

        "success": True,

        "event_id":
            event.id,

        "event_title":
            event.title,

        "event_date":
            event.date,

        "event_location":
            event.location,

        "total_registrations":
            total_registrations,

        "total_attendance":
            total_attendance,

        "attendance_percentage":
            round(
                attendance_percentage,
                2
            ),

        "participation_level":
            participation_level,

        "insight":
            insight,

        "recommendation":
            recommendation

    }
# ==================================================
# CREATE NOTIFICATION
# ==================================================

@app.post("/notifications")
def create_notification(
    notification: NotificationCreate
):

    db = SessionLocal()

    # Check user

    user = db.query(
        models.User
    ).filter(
        models.User.id == notification.user_id
    ).first()

    if user is None:

        db.close()

        return {
            "success": False,
            "message": "User not found"
        }


    # Check event

    event = db.query(
        models.Event
    ).filter(
        models.Event.id == notification.event_id
    ).first()

    if event is None:

        db.close()

        return {
            "success": False,
            "message": "Event not found"
        }


    # Create notification

    new_notification = models.Notification(

        user_id=notification.user_id,

        event_id=notification.event_id,

        message=notification.message,

        status="UNREAD"

    )


    db.add(new_notification)

    db.commit()

    db.refresh(new_notification)


    notification_id = new_notification.id

    db.close()


    return {

        "success": True,

        "message": "Notification created successfully!",

        "notification_id": notification_id

    }


# ==================================================
# GET USER NOTIFICATIONS
# ==================================================

@app.get("/notifications/{user_id}")
def get_notifications(user_id: int):

    db = SessionLocal()

    notifications = db.query(
        models.Notification
    ).filter(
        models.Notification.user_id == user_id
    ).order_by(
        models.Notification.id.desc()
    ).all()


    result = []

    for notification in notifications:

        result.append({

            "id":
                notification.id,

            "user_id":
                notification.user_id,

            "event_id":
                notification.event_id,

            "message":
                notification.message,

            "status":
                notification.status

        })


    db.close()


    return result
# ==================================================
# SEND EVENT REMINDER TO ALL REGISTERED USERS
# ==================================================

@app.post("/notifications/remind/{event_id}")
def send_event_reminder(event_id: int):

    db = SessionLocal()

    # Check event

    event = db.query(
        models.Event
    ).filter(
        models.Event.id == event_id
    ).first()

    if event is None:

        db.close()

        return {
            "success": False,
            "message": "Event not found"
        }


    # Get all registrations for this event

    registrations = db.query(
        models.Registration
    ).filter(
        models.Registration.event_id == event_id
    ).all()


    if len(registrations) == 0:

        db.close()

        return {
            "success": False,
            "message": "No students are registered for this event"
        }


    notification_count = 0


    # Create notification for every registered student

    for registration in registrations:

        new_notification = models.Notification(

            user_id=registration.user_id,

            event_id=event_id,

            message=(
                f"Reminder: {event.title} "
                f"is scheduled on {event.date} "
                f"at {event.time} "
                f"at {event.location}."
            ),

            status="UNREAD"

        )

        db.add(new_notification)

        notification_count += 1


    db.commit()

    db.close()


    return {

        "success": True,

        "message": (
            f"Reminder sent to "
            f"{notification_count} registered students."
        ),

        "notification_count":
            notification_count

    }
# ==================================================
# EVENT REPORT
# ==================================================

@app.get("/reports/{event_id}")
def generate_event_report(event_id: int):

    db = SessionLocal()

    # --------------------------------------------------
    # FIND EVENT
    # --------------------------------------------------

    event = db.query(
        models.Event
    ).filter(
        models.Event.id == event_id
    ).first()

    if event is None:

        db.close()

        return {
            "success": False,
            "message": "Event not found"
        }


    # --------------------------------------------------
    # TOTAL REGISTRATIONS
    # --------------------------------------------------

    total_registrations = db.query(
        models.Registration
    ).filter(
        models.Registration.event_id == event_id
    ).count()


    # --------------------------------------------------
    # TOTAL PRESENT
    # --------------------------------------------------

    total_attendance = db.query(
        models.Attendance
    ).join(
        models.Registration,
        models.Attendance.registration_id ==
        models.Registration.id
    ).filter(
        models.Registration.event_id == event_id,
        models.Attendance.status == "PRESENT"
    ).count()


    # --------------------------------------------------
    # CALCULATE ABSENT / NOT ATTENDED
    # --------------------------------------------------

    total_absent = (
        total_registrations -
        total_attendance
    )


    # --------------------------------------------------
    # ATTENDANCE PERCENTAGE
    # --------------------------------------------------

    if total_registrations > 0:

        attendance_percentage = (
            total_attendance /
            total_registrations
        ) * 100

    else:

        attendance_percentage = 0


    # --------------------------------------------------
    # PARTICIPATION LEVEL
    # --------------------------------------------------

    if total_registrations == 0:

        participation_level = "No Data"

    elif attendance_percentage >= 80:

        participation_level = "Excellent"

    elif attendance_percentage >= 60:

        participation_level = "Good"

    elif attendance_percentage >= 40:

        participation_level = "Average"

    else:

        participation_level = "Low"


    # --------------------------------------------------
    # AI INSIGHT
    # --------------------------------------------------

    if total_registrations == 0:

        insight = (
            "No participants registered "
            "for this event."
        )

        recommendation = (
            "Promote the event and encourage "
            "participants to register."
        )

    elif attendance_percentage >= 80:

        insight = (
            "The event achieved a high "
            "attendance rate."
        )

        recommendation = (
            "Continue the current event "
            "communication strategy."
        )

    elif attendance_percentage >= 60:

        insight = (
            "The event achieved a good "
            "attendance rate."
        )

        recommendation = (
            "Send reminder notifications before "
            "future events to improve attendance."
        )

    elif attendance_percentage >= 40:

        insight = (
            "The event had moderate attendance."
        )

        recommendation = (
            "Improve event promotion and "
            "participant communication."
        )

    else:

        insight = (
            "The event had low attendance."
        )

        recommendation = (
            "Increase event promotion and "
            "send reminder notifications."
        )


    # --------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------

    db.close()


    # --------------------------------------------------
    # RETURN REPORT
    # --------------------------------------------------

    return {

        "success": True,

        "report": {

            "event_id":
                event.id,

            "event_title":
                event.title,

            "description":
                event.description,

            "date":
                event.date,

            "time":
                event.time,

            "location":
                event.location,

            "total_registrations":
                total_registrations,

            "total_attendance":
                total_attendance,

            "total_absent":
                total_absent,

            "attendance_percentage":
                round(
                    attendance_percentage,
                    2
                ),

            "participation_level":
                participation_level,

            "ai_insight":
                insight,

            "ai_recommendation":
                recommendation

        }

    }
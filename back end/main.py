# main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from datetime import datetime
import shutil
import os
from pydantic import BaseModel

# Config 
DATABASE_URL = "postgresql://postgres:8052@localhost/creative_hut_db"  # <-- Update this

app = FastAPI()

origins = [
    "http://localhost:5173"
]

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ContactCreate(BaseModel):
    name: str
    email: str
    message: str

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="buyer")  # buyer, freelancer, admin
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    rating = Column(Float, default=0.0)
    profile_pic = Column(String, nullable=True)

    gigs = relationship("Gig", back_populates="owner")
    applications = relationship("Application", back_populates="freelancer")

class Gig(Base):
    __tablename__ = "gigs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String)
    price = Column(Integer)
    revisions = Column(Integer)
    delivery = Column(Integer)
    image_path = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="gigs")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String)
    status = Column(String, default="Pending")
    freelancer = Column(String, nullable=True)
    budget_type = Column(String)
    deadline = Column(String)
    skills = Column(Text)
    buyer_id = Column(Integer, ForeignKey("users.id"))


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    freelancer_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)

    freelancer = relationship("User", back_populates="applications")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    instructor = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    thumbnail = Column(String, nullable=True)


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)



# Create Tables
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Routes

@app.get("/")
def root():
    return {"message": "Creative Hut API is running."}

# User Routes

@app.post("/users/")
def create_user(name: str = Form(...), email: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    user = User(name=name, email=email, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/users/{user_id}/upload-pic")
def upload_profile_pic(user_id: int, image: UploadFile = File(...), db: Session = Depends(get_db)):
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    image_path = f"{uploads_dir}/{image.filename}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.profile_pic = image_path
    db.commit()
    db.refresh(user)
    return {"detail": "Profile picture updated", "profile_pic": image_path}

@app.get("/users/")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, name: str = Form(None), bio: str = Form(None), skills: str = Form(None), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if name:
        user.name = name
    if bio:
        user.bio = bio
    if skills:
        user.skills = skills
    db.commit()
    return user

@app.get("/users/by-email/{email}")
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}")
def update_user(
    user_id: int,
    name: str = Form(...),
    bio: str = Form(...),
    skills: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = name
    user.bio = bio
    user.skills = skills
    db.commit()
    db.refresh(user)
    return user

# Gig Routes

@app.post("/gigs/")
def create_gig(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: int = Form(...),
    revisions: int = Form(...),
    delivery: int = Form(...),
    user_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    image_path = f"{uploads_dir}/{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    gig = Gig(
        title=title,
        description=description,
        category=category,
        price=price,
        revisions=revisions,
        delivery=delivery,
        user_id=user_id,
        image_path=image_path
    )
    db.add(gig)
    db.commit()
    db.refresh(gig)
    return gig


@app.get("/gigs/")
def get_all_gigs(db: Session = Depends(get_db)):
    return db.query(Gig).all()

@app.get("/gigs/freelancer/{freelancer_id}")
def get_gigs_by_freelancer(freelancer_id: int, db: Session = Depends(get_db)):
    return db.query(Gig).filter(Gig.user_id == freelancer_id).all()

@app.get("/gigs/image/{filename}")
def get_image(filename: str):
    path = f"uploads/{filename}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)

@app.put("/gigs/{gig_id}")
def update_gig(
    gig_id: int,
    title: str = Form(...),
    category: str = Form(...),
    price: int = Form(...),
    db: Session = Depends(get_db)
):
    gig = db.query(Gig).filter(Gig.id == gig_id).first()
    if not gig:
        raise HTTPException(status_code=404, detail="Gig not found")
    gig.title = title
    gig.category = category
    gig.price = price
    db.commit()
    db.refresh(gig)
    return gig

@app.delete("/gigs/{gig_id}")
def delete_gig(gig_id: int, db: Session = Depends(get_db)):
    gig = db.query(Gig).filter(Gig.id == gig_id).first()
    if not gig:
        raise HTTPException(status_code=404, detail="Gig not found")
    db.delete(gig)
    db.commit()
    return {"detail": "Gig deleted"}

# Job Routes

@app.post("/jobs/")
def post_job(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    budget_type: str = Form(...),
    deadline: str = Form(...),
    skills: str = Form(...),
    buyer_id: int = Form(...),
    db: Session = Depends(get_db)
):
    job = Job(
        title=title,
        description=description,
        category=category,
        budget_type=budget_type,
        deadline=deadline,
        skills=skills,
        buyer_id=buyer_id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@app.get("/jobs/")
def get_all_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@app.get("/jobs/buyer/{buyer_id}")
def get_jobs_by_buyer(buyer_id: int, db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.buyer_id == buyer_id).all()

@app.post("/jobs/apply/")
def apply_to_job(
    job_id: int = Form(...),
    freelancer_id: int = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    appn = Application(job_id=job_id, freelancer_id=freelancer_id, message=message)
    db.add(appn)
    db.commit()
    db.refresh(appn)
    return appn

@app.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    title: str = Form(...),
    category: str = Form(...),
    deadline: str = Form(...),
    status: str = Form(...),
    freelancer: str = Form(None),  # Optional
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.title = title
    job.category = category
    job.deadline = deadline
    job.status = status
    job.freelancer = freelancer

    db.commit()
    db.refresh(job)
    return job

from fastapi import Query

# Courses Routes

@app.post("/courses/")
def create_course(
    title: str = Form(...),
    instructor: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    price: int = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    image_path = None

    if image:
        image_path = f"{uploads_dir}/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    course = Course(
        title=title,
        instructor=instructor,
        description=description,
        category=category,
        price=price,
        thumbnail=image_path
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@app.get("/courses/")
def get_all_courses(
    category: str = Query(None),
    is_free: bool = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Course)

    if category:
        query = query.filter(Course.category == category)

    if is_free is not None:
        if is_free:
            query = query.filter(Course.price == 0)
        else:
            query = query.filter(Course.price > 0)

    return query.all()


@app.get("/courses/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# Enrollment Routes

@app.post("/enrollments/")
def enroll_in_course(
    user_id: int = Form(...),
    course_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Optional: prevent duplicate enrollments
    existing = db.query(Enrollment).filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")

    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return {"message": "Enrollment successful", "enrollment_id": enrollment.id}

@app.get("/enrollments/{user_id}")
def get_user_enrollments(user_id: int, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter_by(user_id=user_id).all()
    return enrollments


# Top Freelancers

@app.get("/top-freelancers/")
def get_top_freelancers(db: Session = Depends(get_db)):
    top_users = db.query(User).filter(User.role == "freelancer").limit(6).all()
    result = []

    for user in top_users:
        gigs = db.query(Gig).filter(Gig.user_id == user.id).limit(1).all()
        gig_data = [
            {
                "title": gig.title,
                "price": gig.price,
                "delivery": gig.delivery
            }
            for gig in gigs
        ]
        result.append({
            "id": user.id,
            "name": user.name,
            "skill": user.bio or "Freelancer",  # reuse `bio` or add separate `skill`
            "rating": 4.8,  # static or avg rating if you add ratings later
            "reviews": 120,  # static for now
            "profile_pic": user.profile_pic,
            "gigs": gig_data
        })

    return result


@app.post("/contact")
def submit_contact(form: ContactCreate, db: Session = Depends(get_db)):
    contact = Contact(
        name=form.name,
        email=form.email,
        message=form.message,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return {"message": "Message received", "id": contact.id}



# Dashboard Summary

@app.get("/dashboard-summary/")
def get_dashboard_summary(db: Session = Depends(get_db)):
    user_count = db.query(User).count()
    gig_count = db.query(Gig).count()
    job_count = db.query(Job).count()
    return {
        "total_users": user_count,
        "total_gigs": gig_count,
        "total_jobs": job_count
    }

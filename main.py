from fastapi import (
    FastAPI,
    Response,
    status,
    HTTPException,
    Depends
)
import psycopg2 as pg2
from psycopg2.extras import RealDictCursor
import time
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import engine,get_db
from . import models

# create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# post model
class Post(BaseModel):
    """Post Model"""
    title: str
    description: str

# manage database connection
while True:
    try:
        conn = pg2.connect(
            host='localhost',
            database='fastapidb', 
            user='postgres',
            password='rootuser',
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("Database connection established.")
        break
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        cursor = None
        time.sleep(2)


@app.get("/")
def index():
    return {"message": "Hello World from FastAPI!"}


# @app.get("/posts")
# def get_posts():
#     cursor.execute("""select * from posts""") # way to get data from database using sql query
#     posts_list = cursor.fetchall()
#     return {"data": posts_list}


@app.get("/posts", status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all() # get all posts from database using sqlalchemy orm
    return {"data": posts}


# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_post(post: Post):
#     # cursor.execute("""insert into posts(title,description) values(%s,%s) returning * """,(post.title, post.description))
#     # new_post = cursor.fetchone()
#     # conn.commit()
#     return {"data": new_post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post:Post, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


# get post by id
@app.get("/posts/{id}", status_code=status.HTTP_200_OK)
def get_post(id: int):
    cursor.execute(""" select * from posts where id = %s """, (str(id),))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")

    return {"data": post}


# delte post by id
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(""" delete from posts where id = %s returning * """, (str(id),))
    post = cursor.fetchone()
    conn.commit()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update post
@app.put('/posts/{id}')
def update_post(id: int, post: Post):
    cursor.execute(""" update posts set title = %s, description = %s where id = %s returning * """, (post.title, post.description, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return {"data": updated_post}

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def commit_or_409(db: Session, message: str = "This action conflicts with existing related data"):
    """
    Commit the current transaction. If the database rejects it because of a
    foreign key or unique constraint violation, roll back and turn it into a
    clean 409 response instead of letting a raw 500 (IntegrityError) escape.

    Typical case: trying to DELETE a row that other rows still reference
    (e.g. deleting a `role` that a `user` still points to).
    """
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)

        
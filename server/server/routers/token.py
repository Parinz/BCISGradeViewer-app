from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from ..security import get_current_user, OauthUser, create_access_token
from ..scraper.parent import Parent
from ..scraper.student import Student
from ..exceptions import NotAuthenticated
from ..dependencies import get_db
from ..sql import crud, schemas
from sqlalchemy.orm import Session

router = APIRouter(tags=["Token"], prefix="/token")

# Gets the current user at /token/me
@router.get("/me/")
async def get_curr_user(current_user: OauthUser = Depends(get_current_user)):
    return current_user


# Login at /token/
@router.post("/")
def login(
    student: bool,
    backgroundTask: BackgroundTasks,
    formData: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Check if user already exists in db
    user = crud.get_user(db, formData.username, student)
    if user == None:
        # If they don't then perform validation
        try:
            # TODO: Queue a background task to add the user to the database
            if student:
                Student(formData.username, formData.password)
                # Bottom code will only run if password is correct, otherwise it will be caught by the except below.
                backgroundTask.add_task(
                    crud.create_student,
                    db,
                    schemas.StudentCreate(
                        username=formData.username, password=formData.password
                    ),
                )
            else:
                # TODO: Refactor to using schemas
                Parent(formData.username, formData.password)
                backgroundTask.add_task(
                    crud.create_parent,
                    db,
                    schemas.ParentCreate(
                        username=formData.username, password=formData.password
                    ),
                )
        except NotAuthenticated:
            raise HTTPException(
                status_code=401, detail="Incorrect username or password"
            )

    # Give user the access token
    access_token = create_access_token({"sub": formData.username, "student": student})

    return {"access_token": access_token, "token_type": "bearer"}



from database.db import Database

from database.repositories.login_repo import LoginRepository
from database.repositories.mouse_repo import MouseRepository
from database.repositories.session_repo import SessionRepository

from services.rspace_service import RSpaceService
from services.mouse_service import MouseService
from services.session_service import SessionService

from gui.main_window import MainWindow


def main():
    # Only one DB-Instance
    db = Database()

    # Repositories
    login_repo = LoginRepository(db)
    mouse_repo = MouseRepository(db)
    session_repo = SessionRepository(db)

    # Services
    rspace_service = RSpaceService(login_repo, mouse_repo, session_repo)
    mouse_service = MouseService(mouse_repo)
    session_service = SessionService(session_repo)

    # GUI
    app = MainWindow(
        mouse_service=mouse_service,
        session_service=session_service,
        rspace_service=rspace_service,
        db=db
    )
    app.mainloop()


if __name__ == "__main__":
    main()

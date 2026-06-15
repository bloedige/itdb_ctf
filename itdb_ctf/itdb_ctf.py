from itdb_ctf.api import app
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.pages.login import login_page
from itdb_ctf.pages.retos import retos_page
from itdb_ctf.pages.admin import admin_page
app.add_page(login_page, route="/login")
app.add_page(retos_page, route="/retos", on_load=AuthState.requiere_login)
app.add_page(admin_page, route="/admin", on_load=AuthState.require_staff)
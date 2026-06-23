from itdb_ctf.api import app
from itdb_ctf.auth.auth_state import AuthState

from itdb_ctf.states.reto_states import CrearRetosState
from itdb_ctf.states.catalogo_states import CatalogoState

from itdb_ctf.pages.login import login_page
from itdb_ctf.pages.catalogo import catalogo_page
from itdb_ctf.pages.retos import retos_page
from itdb_ctf.pages.admin import admin_page
from itdb_ctf.pages.admin_retos import admin_retos_page

app.add_page(login_page, route="/login")
app.add_page(catalogo_page, route="/retos", on_load=CatalogoState.cargar_retos)
#app.add_page(retos_page, route="/retos", on_load=AuthState.requiere_login)
app.add_page(admin_page, route="/admin", on_load=AuthState.requiere_staff)
app.add_page(admin_retos_page, route="/admin/retos", on_load=CrearRetosState.cargar_catalogos)
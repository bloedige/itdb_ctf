from itdb_ctf.api import app
from itdb_ctf.auth.auth_state import AuthState

from itdb_ctf.states.evento_states import CreaEventoState, ListarEventoState
from itdb_ctf.states.reto_states import CrearRetosState, ListarRetosState
from itdb_ctf.states.catalogo_states import CatalogoState
from itdb_ctf.states.asociar_state import AsociarState
from itdb_ctf.states.usuario_states import CrearUsuarioState, ListarUsuarioState


from itdb_ctf.pages.login import login_page
from itdb_ctf.pages.catalogo import catalogo_page
from itdb_ctf.pages.retos import retos_page
from itdb_ctf.pages.admin import admin_page
from itdb_ctf.pages.admin_reto import admin_retos_page
from itdb_ctf.pages.admin_evento import admin_eventos_page
from itdb_ctf.pages.admin_asociar import admin_asociar_page
from itdb_ctf.pages.admin_usuario import admin_usuario_page

app.add_page(login_page, route="/login")
app.add_page(catalogo_page, route="/retos", on_load=CatalogoState.cargar_retos)
#app.add_page(retos_page, route="/retos", on_load=AuthState.requiere_login)
app.add_page(admin_page, route="/admin", on_load=AuthState.requiere_staff)
app.add_page(admin_retos_page, route="/admin/retos", on_load=[CrearRetosState.cargar_catalogos, ListarRetosState.cargar_lista])
app.add_page(admin_eventos_page, route="/admin/eventos", on_load=[CreaEventoState.cargar_catalogos, ListarEventoState.cargar_lista])
app.add_page(admin_asociar_page, route="/admin/asociar", on_load=[AsociarState.cargar_todo])
app.add_page(admin_usuario_page, route="/admin/usuarios", on_load=[CrearUsuarioState.cargar_catoalogos, ListarUsuarioState.cargar_lista, ListarUsuarioState.cargar_catalogos])
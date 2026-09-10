from itdb_ctf.api import app
from itdb_ctf.auth.auth_state import AuthState

#states abierto

from itdb_ctf.informacion.informacion_state import InformacionState
from itdb_ctf.catalogo.catalogo_states import CatalogoState
from itdb_ctf.scoreboard.scoreboard_state import ScoreboardState
from itdb_ctf.auto_inscripcion.auto_inscripcion_evento_state import AutoInscripcionState

#states cerrado

from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState
from itdb_ctf.evento_cerrado.evento_cerrado_reto_state import EventoCerradoRetoState
from itdb_ctf.perfil.perfil_state import PerfilGeneralState, PerfilEventoCerradoState
from itdb_ctf.perfil.gestion_state import PerfilGestionState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_state import EventoCerradoAccesoState

#states staff

from itdb_ctf.evento.evento_states import CreaEventoState, ListarEventoState
from itdb_ctf.reto.reto_states import CrearRetosState, ListarRetosState
from itdb_ctf.asociar.asociar_state import AsociarRetoState, GestionarRetoState
from itdb_ctf.usuario.usuario_states import CrearUsuarioState, ListarUsuarioState
from itdb_ctf.inscripcion.inscripcion_state import InscribirState, GestionarInscripcionState
from itdb_ctf.dashboards.evento_abierto_dashboard_states import EventoAbiertoDashboardState
from itdb_ctf.dashboards.eventos_cerrados_dashboard_states import EventosCerradosDashboardState
from itdb_ctf.dashboards.retos_dashboard_states import RetosDashboardState
from itdb_ctf.dashboards.usuarios_dashboard_states import UsuariosDashboardState

#pages abierto

from itdb_ctf.pages.login import login_page
from itdb_ctf.pages.informacion import informacion_page
from itdb_ctf.pages.catalogo import catalogo_page
from itdb_ctf.pages.scoreboard import scoreboard_page
from itdb_ctf.pages.eventos import eventos_page

#pages cerrado

from itdb_ctf.pages.evento_cerrado_informacion import evento_cerrado_informacion_page
from itdb_ctf.pages.evento_cerrado_reto import evento_cerrado_reto_page
from itdb_ctf.pages.evento_cerrado_scoreboard import evento_cerrado_scoreboard_page
from itdb_ctf.pages.evento_cerrado_perfil import evento_cerrado_perfil_page
from itdb_ctf.pages.perfil import perfil_page

#pages staff

from itdb_ctf.pages.admin_reto import admin_retos_page
from itdb_ctf.pages.admin_evento import admin_eventos_page
from itdb_ctf.pages.admin_asociar import admin_asociar_page
from itdb_ctf.pages.admin_asociar_gestionar import admin_asociar_gestionar_page
from itdb_ctf.pages.admin_usuario import admin_usuario_page
from itdb_ctf.pages.admin_inscripcion import admin_inscripcion_page
from itdb_ctf.pages.admin_inscripcion_gestionar import admin_inscripcion_gestionar_page
from itdb_ctf.pages.evento_abierto_dashboard import evento_abierto_dashboard_page
from itdb_ctf.pages.eventos_cerrados_dashboard import eventos_cerrados_dashboard_page
from itdb_ctf.pages.retos_dashboard import retos_dashboard_page
from itdb_ctf.pages.usuarios_dashboard import usuarios_dashboard_page

app.add_page(login_page, route="/login")
app.add_page(informacion_page, route="/informacion", on_load=InformacionState.cargar_info)
app.add_page(catalogo_page, route="/retos", on_load=CatalogoState.cargar_retos)
app.add_page(scoreboard_page, route="/scoreboard", on_load=ScoreboardState.cargar_ranking)
app.add_page(eventos_page, route="/eventos", on_load=AutoInscripcionState.cargar_eventos)
app.add_page(perfil_page, route="/perfil", on_load=PerfilGeneralState.cargar_perfil)

app.add_page(evento_cerrado_informacion_page, route="/evento/[id_evento_cerrado]/informacion", on_load=[EventoCerradoInfromacionState.cargar_info, EventoCerradoAccesoState.verificar])
app.add_page(evento_cerrado_reto_page, route="/evento/[id_evento_cerrado]/retos", on_load=[EventoCerradoRetoState.cargar_retos, EventoCerradoAccesoState.verificar])
app.add_page(evento_cerrado_scoreboard_page, route="/evento/[id_evento_cerrado]/scoreboard", on_load=[ScoreboardState.cargar_ranking, EventoCerradoAccesoState.verificar])
app.add_page(evento_cerrado_perfil_page, route="/evento/[id_evento_cerrado]/perfil", on_load=[PerfilEventoCerradoState.cargar_perfil, EventoCerradoAccesoState.verificar])

app.add_page(admin_eventos_page, route="/admin/eventos", on_load=[CreaEventoState.cargar_catalogos, ListarEventoState.cargar_lista])
app.add_page(admin_retos_page, route="/admin/retos", on_load=[CrearRetosState.cargar_catalogos, ListarRetosState.cargar_lista])
app.add_page(admin_usuario_page, route="/admin/usuarios", on_load=[CrearUsuarioState.cargar_catoalogos, ListarUsuarioState.cargar_lista, ListarUsuarioState.cargar_catalogos])
app.add_page(admin_asociar_page, route="/admin/asociar", on_load=[AsociarRetoState.cargar_todo])
app.add_page(admin_asociar_gestionar_page, route="/admin/asociar/gestionar", on_load=[GestionarRetoState.cargar_todo])
app.add_page(admin_inscripcion_page, route="/admin/inscribir", on_load=[InscribirState.cargar_todo])
app.add_page(admin_inscripcion_gestionar_page, route="/admin/inscribir/gestionar", on_load=[GestionarInscripcionState.cargar_todo])
app.add_page(evento_abierto_dashboard_page, route="/admin/dashboard", on_load=EventoAbiertoDashboardState.cargar_dashboard)
app.add_page(eventos_cerrados_dashboard_page, route="/admin/dashboard/eventos-cerrados", on_load=EventosCerradosDashboardState.cargar_todo)
app.add_page(retos_dashboard_page, route="/admin/dashboard/retos", on_load=RetosDashboardState.cargar_dashboard)
app.add_page(usuarios_dashboard_page, route="/admin/dashboard/usuarios", on_load=UsuariosDashboardState.cargar_dashboard)
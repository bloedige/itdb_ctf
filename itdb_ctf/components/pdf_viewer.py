"""Visor de PDF para previsualizar el reporte de un evento (react-pdf / pdf.js).

Reflex no trae visor de PDF. En PyPI hay dos paquetes que lo resuelven —`reflex-pdf`
y `reflex-pdf-viewer`, ambos 0.0.3— pero su código es idéntico y son apenas estas
cuarenta líneas, así que el wrapper vive acá en vez de sumar una dependencia beta.
Es el mismo patrón de `evolucion_chart.py`.

Se eligió `react-pdf` y no un `<iframe>` porque pdf.js dibuja el documento en un
`<canvas>`: acepta un data URI y así el PDF viaja desde el State, sin necesidad de
publicarlo en un endpoint. Un `<iframe src="data:application/pdf;...">` no sirve —
Chrome y Edge lo bloquean y dejan el marco en blanco.

A cambio, `Pagina` renderiza **una página a la vez**: la navegación la pone quien
use el componente (ver `eventos_cerrados_dashboard_view.dialog_reporte`).
"""

from typing import Any

import reflex as rx

# El worker de pdf.js se sirve desde `assets/`, no desde unpkg: durante una
# competencia sin internet un CDN externo dejaría el visor colgado en "Cargando".
# `assets/pdf.worker.min.mjs` se copia de `.web/node_modules/pdfjs-dist/build/`
# para que la versión coincida exactamente con la que trae react-pdf.
_CUSTOM_JS = r"""
import { pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';
"""


class _ReactPDF(rx.NoSSRComponent):
    library = "react-pdf@9.1.1"


def _firma_carga(pdf_document_proxy: rx.vars.ObjectVar) -> tuple[rx.Var[dict]]:
    """`on_load_success` recibe el proxy del documento; solo interesa `_pdfInfo`,
    que trae `numPages`."""
    return (pdf_document_proxy["_pdfInfo"].to(dict),)


class Documento(_ReactPDF):
    """`file` acepta un data URI (`data:application/pdf;base64,...`) o una URL."""

    tag = "Document"

    file: rx.Var[str]
    loading: rx.Var[Any] = "Cargando PDF..."
    error: rx.Var[Any] = "No se pudo cargar el PDF."

    on_load_success: rx.EventHandler[_firma_carga]
    on_load_error: rx.EventHandler[lambda error: [error]]

    def add_custom_code(self) -> list[str]:
        return [_CUSTOM_JS]

    def add_imports(self) -> rx.ImportDict:
        return {
            "": [
                "react-pdf/dist/Page/AnnotationLayer.css",
                "react-pdf/dist/Page/TextLayer.css",
            ],
        }


class Pagina(_ReactPDF):
    tag = "Page"

    page_number: rx.Var[int]
    width: rx.Var[int]
    height: rx.Var[int]
    scale: rx.Var[float] = 1.0

    render_text_layer: rx.Var[bool] = True
    render_annotation_layer: rx.Var[bool] = True


documento = Documento.create
pagina = Pagina.create

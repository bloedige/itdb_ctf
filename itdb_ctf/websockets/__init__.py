"""Tiempo real de la plataforma: bus pub/sub sobre Redis + cache del scoreboard
+ estado de freeze.

Toda la funcionalidad degrada de forma transparente si Redis no está disponible
(la app vuelve al polling clásico). Ver `reddis.md` en la raíz del repo.
"""

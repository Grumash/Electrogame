# Web de ElectroGame Fuengirola

```
Landing_Page/
├── build.py      genera la web
├── src/          AQUÍ SE EDITA
│   ├── pages/    contenido de cada página (inicio.html, zona-gaming.html…)
│   ├── partials/ iconos compartidos (sprite.svg)
│   └── assets/   css/, js/, img/
└── docs/         AQUÍ ESTÁ LA WEB TERMINADA (se genera, no editar a mano)
```

## Editar
1. Cambia el texto en `src/pages/<página>.html` (o estilos en `src/assets/css/styles.css`).
2. Genera la web:
   - `python build.py --preview` → copia de prueba para GitHub Pages (Google no la indexa).
   - `python build.py` → versión final para el hosting real de electrogame.es.

   Cada vez se borra y se vuelve a crear `docs/` entera.
   Si falta `src/`, el script se detiene y no toca `docs/`.

La cabecera, el menú y el pie de página están en `build.py` y son iguales en todas las páginas.

## Ver en local
Abre `docs/index.html` con doble clic.

## Publicar en GitHub Pages (enlace para compartir)
1. Crea un repositorio **público** en GitHub (por ejemplo `electrogame`) y sube esta carpeta.
2. En el repositorio: **Settings → Pages → Build and deployment**
   - Source: *Deploy from a branch*
   - Branch: `main` · carpeta `/docs` → **Save**
3. En 1–2 minutos la web estará en `https://TU-USUARIO.github.io/electrogame/`.

Después de cada cambio: `python build.py --preview`, y sube los cambios (commit + push).

## Publicar en el hosting real
Ejecuta `python build.py` (sin `--preview`) y sube **el contenido de `docs/`** a la raíz del hosting.

No borres `src/` ni `build.py`: son los que generan `docs/`.

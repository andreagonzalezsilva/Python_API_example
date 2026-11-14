# Plan 001 – Aplicación web de educación personalizada

## 1. Objetivo
Aplicación web de escritorio que explica material académico adaptándose al método de aprendizaje del usuario, usando IA (Google Gemini) con verificación de información en fuentes veraces.

> Nota: se descarta la idea de "Método 1 / Método 2" de `lluvia_de_ideas.txt`. La personalización se define únicamente con la encuesta (`Encuesta001.md`).

## 2. Stack
- **Backend:** Django (auth, ORM, subida de archivos, settings por entorno)
- **Frontend:** HTML + CSS + JavaScript básico
- **BD:** SQLite
- **IA:** Google Gemini (SDK `google-genai`, plan gratuito)
- **Almacenamiento:** disco local del servidor (`media/`), sin servicios en la nube

## 3. Estructura de carpetas
```text
curso_API_python/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── plan001.md
├── config/
│   ├── urls.py
│   ├── wsgi.py
│   └── settings/
│       ├── base.py            # configuración común
│       ├── local.py           # Versión 1: desarrollo
│       └── pythonanywhere.py  # Versión 2: producción
├── accounts/                  # registro, login, ajustes de UI
├── onboarding/                # bienvenida + encuesta
│   ├── survey_config.py       # preguntas y mapeo (de Encuesta001.md)
│   └── presets.py             # perfiles predeterminados
├── learning/                  # módulo de aprendizaje + IA
│   ├── models.py              # Conversation, Message, MessageImage
│   └── services/
│       ├── prompt_builder.py
│       └── gemini_client.py
├── templates/
│   ├── base.html
│   ├── accounts/  (register, login, settings)
│   ├── onboarding/ (welcome, survey)
│   └── learning/  (home)
├── static/ (css/, js/)
└── media/
    ├── backgrounds/<user_id>/
    └── queries/<user_id>/
```

## 4. Modelos de base de datos
- **User** (Django): username, password, email (opcional).
- **UserProfile** (1–1 con User):
  - `onboarding_completed` (bool)
  - `preset_slug` (perfil predeterminado elegido, nullable)
  - `custom_config` (JSON con las respuestas de la encuesta)
  - `theme` (claro / oscuro / otros), `accent_color`
  - `background_image` (ImageField, opcional)
- **Conversation**: user, título, fecha.
- **Message**: conversation, rol (user/assistant), texto, fuentes (JSON), fecha.
- **MessageImage**: message, imagen (ImageField).

## 5. Flujo de la aplicación
1. Registro (usuario, contraseña, email opcional) → login.
2. Primera vez: pantalla de bienvenida → encuesta.
3. Resultado de la encuesta: elegir un **perfil predeterminado** o **crear perfil personalizado** con las respuestas.
4. Vista principal de aprendizaje: el usuario escribe un tema, adjunta imágenes, y recibe la explicación adaptada.
5. Ajustes: tema de colores, fondo (subir imagen propia), cambiar perfil de enseñanza.

## 6. Encuesta (basada en `Encuesta001.md`)
| # | Pregunta | Clave | Opciones |
|---|---|---|---|
| 1 | ¿Cómo prefieres que te explique un tema nuevo? | explicacion | A directa / B ejemplos primero / C socrático / D visual y analogías |
| 2 | ¿A qué ritmo quieres aprender? | ritmo | A rápido / B moderado / C lento / D adaptativo |
| 3 | ¿Cómo quieres practicar? | practica | A ejercicios repetitivos / B casos prácticos |
| 4 | ¿Cómo quieres recibir retroalimentación? | feedback | A corrección inmediata / B pistas / C motivacional / D análisis del error |
| 5 | ¿Qué estilo de comunicación prefieres? | tono | A formal / B amigable / C divertido / D minimalista |

Cada respuesta se convierte en una instrucción del *system prompt*.

## 7. Perfiles predeterminados (basados en las respuestas de la encuesta)
| Perfil | explicacion | ritmo | practica | feedback | tono |
|---|---|---|---|---|---|
| Directo y eficiente | directa | rápido | ejercicios repetitivos | corrección inmediata | minimalista |
| Práctico con ejemplos | ejemplos primero | moderado | casos prácticos | pistas | amigable |
| Explorador socrático | socrático | adaptativo | casos prácticos | pistas | amigable |
| Visual y relajado | visual y analogías | lento | casos prácticos | motivacional | divertido |


## 8. Integración con IA (Gemini)
- Cliente: `google-genai`, modelo Flash (por ejemplo `gemini-2.5-flash`; confirmar el modelo disponible en el plan gratuito).
- `prompt_builder.py` une: reglas base de verificación + instrucciones del perfil del usuario.
- **Verificación de datos:** activar la herramienta *Grounding with Google Search* y exigir en el system prompt:
  - basarse solo en fuentes confiables (académicas, institucionales, enciclopédicas);
  - no inventar datos, citas ni referencias;
  - decir "no estoy seguro" si no hay evidencia suficiente;
  - listar las fuentes al final (se extraen de `grounding_metadata`).
- Imágenes: se envían como `Part.from_bytes` junto al texto.
- La clave `GEMINI_API_KEY` va en variables de entorno (`.env`), nunca en el repositorio.

## 9. Archivos subidos y seguridad
- Rutas por usuario: `media/backgrounds/<id>/` y `media/queries/<id>/`.
- Validar tipo (jpg, png, webp), tamaño máximo (~5 MB) y verificar con Pillow.
- Renombrar con UUID para evitar colisiones y nombres maliciosos.
- Las imágenes de consultas son privadas: servirlas con una vista que compruebe el dueño. Si PythonAnywhere las sirve como estáticas quedan públicas por URL, así que los UUID son la mitigación mínima.
- Protección CSRF, hash de contraseñas y límite de peticiones por usuario para cuidar la cuota gratuita de Gemini.

## 10. Entornos
| Aspecto | Local (V1) | PythonAnywhere (V2) |
|---|---|---|
| Settings | `config.settings.local` | `config.settings.pythonanywhere` |
| DEBUG | True | False |
| ALLOWED_HOSTS | localhost, 127.0.0.1 | `<usuario>.pythonanywhere.com` |
| SECRET_KEY / API key | `.env` | variables en el WSGI o `.env` en el servidor |
| Archivos estáticos | servidos por Django | `collectstatic` + mapeo en la pestaña Web |
| Media | servida por Django | mapeo `/media/` en la pestaña Web |
| Servidor | `runserver` | WSGI de PythonAnywhere |

### Pasos de despliegue en PythonAnywhere
1. Subir el código (`git clone` desde la consola Bash).
2. Crear virtualenv e instalar: `pip install -r requirements.txt`.
3. Crear `.env` en el servidor con `SECRET_KEY` y `GEMINI_API_KEY`.
4. Web → Add new web app → Manual configuration (misma versión de Python que el virtualenv).
5. Editar el archivo WSGI para usar `DJANGO_SETTINGS_MODULE=config.settings.pythonanywhere`.
6. Ejecutar `python manage.py migrate` y `python manage.py collectstatic`.
7. En la pestaña Web mapear `/static/` → `.../staticfiles` y `/media/` → `.../media`.
8. Reload.

### Riesgos del plan gratuito de PythonAnywhere (verificar antes de desplegar)
- Las cuentas gratuitas solo pueden hacer peticiones salientes a una lista blanca de dominios. Hay que confirmar que `generativelanguage.googleapis.com` esté permitido. Si no lo está, la IA no funcionará allí y habrá que usar otro host o plan.
- Límites de disco (~512 MB), un solo web app y renovación periódica.
- La cuota gratuita de Gemini tiene límite por minuto y por día.

## 11. Fases de implementación
1. Proyecto Django, settings por entorno, `.gitignore`, `requirements.txt`.
2. Autenticación (registro/login) y `UserProfile`.
3. Bienvenida + encuesta + perfiles predeterminados/personalizados.
4. Servicio Gemini (prompt builder + grounding) y módulo de aprendizaje con imágenes.
5. Personalización de UI (temas y fondo propio).
6. Configuración y guía de despliegue en PythonAnywhere.
7. Pruebas manuales y README.

## 12. Entregables
- Estructura de carpetas y código backend (modelos, vistas, rutas, conexión con Gemini).
- Plantillas HTML/CSS/JS: registro, encuesta, vista de aprendizaje, ajustes.
- Preguntas de la encuesta (sección 6).
- Instrucciones para pasar de local a PythonAnywhere (sección 10).

## 13. Preguntas abiertas
- ¿Se permite elegir el idioma de las respuestas (hoy se asume español)?
- ¿Se guarda el historial de conversaciones por usuario?
- ¿Se agrega una opción alternativa a Gemini si falla la cuota?


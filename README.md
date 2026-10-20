# Sixtos Radar 🔎

**Tu radar de novedades de IA y Web3, en tu propio Discord.**

Consulta feeds RSS/Atom de fuentes primarias y envía titulares recientes con enlaces a un canal de Discord. Funciona con Python y GitHub Actions, sin API de X, sin claves de modelos de IA y sin dejar tu computadora encendida.

**Open source · licencia MIT · cada persona usa su propia cuenta, servidor y webhook.**

## Qué hace

- Consulta fuentes aproximadamente cada 30 minutos.
- Envía hasta 3 alertas al día y un resumen de hasta 5 noticias a partir de las 09:00 en la zona horaria configurada.
- Filtra por fecha, evita repetir enlaces durante 7 días y permite incluir o excluir palabras en el titular.
- Incluye fuentes de IA, Ethereum y agentes que conectan IA con wallets.
- Si no hay anuncios recientes, lo dice; si falla una fuente, señala la cobertura parcial en el resumen.

Sirve para reunir ideas para contenido, seguir lanzamientos y leer anuncios originales. Los titulares conservan su idioma. **No genera tuits con IA, no mide tendencias en X ni garantiza que una noticia sea exclusiva.** Lee la fuente antes de publicar.

## Pruébalo en tu cuenta

### 1. Haz tu copia

Pulsa **Fork** arriba en este repositorio y elige tu cuenta de GitHub. Conserva el repositorio público si quieres usar los runners estándar gratuitos. Tu copia es independiente: puedes editarla sin cambiar la de otras personas.

### 2. Prepara tu Discord

1. En Discord, pulsa **Añadir un servidor → Crear mi propio modelo → Para mí y mis amigos**.
2. Elige un nombre, por ejemplo `Mi Radar`.
3. Crea un canal de texto, por ejemplo `radar-ai-web3`. Si será solo para ti, márcalo como privado y omite añadir miembros.
4. En **Editar canal → Integraciones → Webhooks**, crea un webhook y elige ese canal.
5. Ponle el nombre que quieras y pulsa **Copia la URL del webhook**.

No necesitas un bot de Discord con permisos de administrador. Se usa un webhook entrante: una dirección privada que permite enviar mensajes al canal elegido. **No la pegues en un issue, commit, captura o chat público.**

### 3. Guarda tu secreto en TU fork

En tu copia de GitHub:

**Settings → Secrets and variables → Actions → New repository secret**

- **Name:** `DISCORD_WEBHOOK_URL`
- **Secret:** la URL que copiaste de tu propio Discord.

Pulsa **Add secret**. Los secretos del proyecto original no se copian con el fork: debes configurar el tuyo. Tampoco necesitas una contraseña de Discord, token de X o token personal de GitHub.

### 4. Personaliza y activa

1. Edita [`config.json`](config.json) en tu copia y guarda el cambio en la rama predeterminada.
2. Abre **Actions**. Si GitHub lo solicita, habilita los workflows de tu fork.
3. Elige **Radar IA y Web3** y habilita el workflow si está desactivado.
4. Pulsa **Run workflow → main → Run workflow** (usa tu rama predeterminada si la renombraste).
5. Comprueba la marca verde en GitHub y el mensaje **Radar conectado** en tu canal.

Los horarios programados de forks están desactivados por defecto hasta que los habilites. El mensaje de prueba solo se envía cuando ejecutas manualmente; no cada 30 minutos.

## Tus fuentes y horarios

Edita `config.json`. No contiene credenciales y será visible si tu repositorio es público.

| Opción | Qué cambia | Ejemplo |
| --- | --- | --- |
| `timezone` | Zona IANA para el resumen y el límite diario; ajusta el horario de verano | `Europe/Madrid`, `America/Bogota`, `America/Argentina/Buenos_Aires` |
| `digest_time` | Hora local desde la cual se envía el resumen, formato de 24 horas | `08:30` |
| `max_alerts_per_day` | Máximo diario de avisos individuales; `0` deja solo el resumen | `3` |
| `digest_items` | Noticias por resumen, de 1 a 5 | `5` |
| `lookback_hours` | Antigüedad máxima, de 1 a 72 horas | `24` |
| `include_keywords` | Dejar vacío para todo; de lo contrario, exige al menos una coincidencia en el titular | `["agent", "wallet", "AI"]` |
| `exclude_keywords` | Excluye titulares con cualquiera de estas palabras | `["giveaway"]` |
| `feeds` | Nombre público y dirección HTTPS de cada feed, hasta 20 | ver abajo |

Por ejemplo, para sumar una fuente agrega una entrada dentro de `feeds`:

```json
"Nombre de la nueva fuente": "https://example.org/feed.xml"
```

Esa dirección es solo un ejemplo: reemplázala por un RSS/Atom real. No pegues la URL de una página normal ni feeds privados con claves. Conserva las comas entre entradas. Las palabras se buscan como texto dentro del titular, sin distinguir mayúsculas; no hay clasificación semántica con IA.

La zona horaria decide el día de los avisos y la hora del resumen. Si eliges `08:30`, llegará en la primera ejecución disponible después de esa hora (normalmente cerca de las 08:47 con el cron predeterminado), no necesariamente a las 08:30 exactas. Un cambio de zona puede reiniciar el límite de avisos si cambia la fecha local.

Para cambiar la **frecuencia de consulta**, edita `.github/workflows/radar.yml`:

```yaml
schedule:
  - cron: '17,47 * * * *' # aproximadamente cada 30 minutos
```

Una vez por hora: `'17 * * * *'`. El cron predeterminado usa UTC; para consultas durante todo el día eso no modifica la hora local del resumen. Mantén una frecuencia razonable para no saturar las fuentes. GitHub puede retrasar u omitir ejecuciones y suspender cron públicos tras 60 días sin actividad; revisa Actions si dejan de llegar mensajes.

## Privacidad y seguridad

- **Público:** código, fuentes, configuración, historial de commits y logs de Actions.
- **Privado:** la URL de tu webhook, guardada como secreto de Actions de tu repositorio.
- El código no necesita ni almacena contraseñas de X, GitHub o Discord.
- Cada fork usa su propio secreto. El historial de envíos se reinicia al detectar otra instancia mediante `GITHUB_REPOSITORY`.
- `state.json` solo guarda identificador público de la instancia, hashes de enlaces y fechas. No guarda mensajes privados, usuarios de Discord o el webhook. Su historial también es público.
- Los pull requests ejecutan únicamente pruebas de lectura, sin publicar a Discord. El monitor solo se activa manualmente o por horario en la rama predeterminada.
- Revisa las contribuciones antes de incorporarlas: el código que aceptes en tu rama podrá usar tu secreto. No otorgues escritura a desconocidos.
- Si expones tu webhook, elimínalo en Discord, crea otro y actualiza el secreto. Borrar el texto de un archivo no lo borra del historial de Git.

Consulta [SECURITY.md](SECURITY.md) para reportar una posible exposición sin publicar credenciales.

## Costos

Este proyecto usa un runner estándar de Linux en un repositorio público, sin artifacts, cachés ni APIs facturables. Eso entra en el uso gratuito de GitHub Actions conforme a sus [condiciones actuales](https://docs.github.com/en/billing/concepts/product-billing/github-actions). No exige comprar créditos de X, contratar un servidor ni conectar una tarjeta para el diseño descrito.

Si cambias a un repositorio privado, activas un runner grande o añades servicios externos, revisa sus cuotas y costos. No se promete gratuidad para modificaciones ajenas al diseño original ni si cambian las condiciones del proveedor.

## Ejecutar y probar localmente

Requiere Python 3.9+ y una base de zonas horarias IANA (incluida en el runner de Ubuntu). No se instalan dependencias de Python.

```sh
python3 -m unittest -v
python3 radar.py --dry-run
```

La prueba en seco consulta feeds sin enviar mensajes ni guardar estado. Para enviar localmente, configura `DISCORD_WEBHOOK_URL` como variable de entorno privada y ejecuta `python3 radar.py`; no pongas el secreto en el comando que compartas o en el código.

## Límites conocidos

Los feeds pueden llevar retraso, cambiar o no tener publicaciones recientes. El filtro usa la fecha de publicación que declara la fuente; no prueba la veracidad del anuncio. Solo se deduplican enlaces normalizados, por lo que dos sitios que cubran lo mismo pueden generar avisos separados. Un fallo después de enviar y antes de guardar/subir el estado puede causar duplicados. El resumen y los avisos individuales pueden incluir la misma noticia de forma intencional.

¿Quieres añadir fuentes, mejorar los filtros o aportar traducción? Lee [CONTRIBUTING.md](CONTRIBUTING.md). Puedes modificar tu fork libremente o proponer una mejora mediante pull request.

## Licencia

[MIT](LICENSE). Puedes usar, copiar, modificar y redistribuir el código, incluso comercialmente, conservando el aviso de licencia. Las fuentes externas y sus contenidos conservan sus propias condiciones.

Creado por [@0xSixtos](https://x.com/0xSixtos).

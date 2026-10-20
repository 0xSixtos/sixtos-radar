# Seguridad

El único secreto de la instalación estándar es `DISCORD_WEBHOOK_URL`. Se configura en GitHub Actions Secrets, nunca en `config.json`, el código o un archivo de ejemplo.

## Si encuentras una exposición

No abras un issue público con el secreto ni envíes tokens por mensaje. Si el secreto es tuyo, revoca el webhook en Discord y reemplázalo. Borrar un archivo no elimina el secreto del historial.

Para informar al mantenedor, usa **Security → Advisories → Report a vulnerability** si está disponible. Si no aparece, abre un issue que solo solicite un canal privado de contacto, sin incluir secretos ni detalles explotables.

## Alcance

Los forks no heredan los secretos del repositorio original. Sin embargo, quien tenga permisos para editar el código o los workflows de tu copia puede intentar extraer sus secretos. Revisa los pull requests antes de aceptarlos y limita los permisos de escritura.

El monitor solo se ejecuta con secretos por `schedule` o `workflow_dispatch`; CI de pull requests utiliza permisos de lectura y pruebas simuladas. No añadas `pull_request_target` para ejecutar código externo con secretos.

Este es un proyecto pequeño, sin auditoría de seguridad externa ni garantía de ausencia de vulnerabilidades. Consulta el README para ver qué estado y logs son públicos.

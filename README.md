# Sixtos Radar

Monitor de anuncios de IA y Web3 para Discord. Python 3.9+; sin dependencias ni APIs de pago.

Consulta cuatro feeds oficiales cada 30 minutos aproximadamente. Envía hasta tres avisos diarios y un resumen de hasta cinco noticias a partir de las 09:00 de Ciudad de México. Solo incluye anuncios fechados en las últimas 24 horas y evita repetir enlaces durante siete días.

Los titulares pueden estar en inglés. No traduce, no verifica el contenido completo, no mide tendencias en X ni asegura exclusivas. La redacción de tuits con IA queda pendiente: entrega fuentes para revisión editorial, no tuits listos.

## Activar

1. Crear el servidor personal «Sixtos Radar» y el canal de texto `radar-ai-web3`.
2. Crear un webhook del canal en Ajustes → Integraciones → Webhooks.
3. Guardar su URL en Settings → Secrets and variables → Actions como secreto `DISCORD_WEBHOOK_URL`. Nunca publicarla.
4. Actions → Radar IA y Web3 → Run workflow. Comprobar que llegó un mensaje antes de dar por activo el monitor.

El webhook permite escribir en un canal. No requiere un bot administrador. Crear esa credencial persistente requiere intervención o confirmación del titular.

## Gratuidad y límites

Usar un repositorio público con el runner estándar `ubuntu-latest`. No se usan runners grandes, artifacts, cachés ni servicios facturables. El estado público solo contiene hashes de enlaces y fechas; el webhook es un secreto. Un repositorio privado consume la cuota gratuita de la cuenta; no cambiar a privado sin revisar presupuesto y cuotas.

GitHub puede retrasar u omitir ejecuciones. Los workflows programados públicos pueden desactivarse tras 60 días sin actividad; revisar Actions. Los commits automáticos no garantizan evitarlo.

El monitor guarda estado tras confirmar cada envío. Un fallo entre envío y persistencia puede producir duplicados. Un fallo parcial se informa en el resumen; si fallan todas las fuentes, falla la ejecución sin anunciar ausencia de noticias.

## Probar sin enviar

```sh
python3 radar.py --dry-run
python3 -m unittest -v
```

Fuentes: Hugging Face Blog, Ethereum Blog, releases de ElizaOS y Coinbase AgentKit. Ajustarlas en `FEEDS`.

Costos: https://docs.github.com/en/billing/concepts/product-billing/github-actions

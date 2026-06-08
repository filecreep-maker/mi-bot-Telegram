import os
import random
import asyncio
import logging
from datetime import datetime, time
from telegram import Bot
from telegram.error import TelegramError

# ─────────────────────────────────────────
#  CONFIGURACIÓN  ← edita solo esta sección
# ─────────────────────────────────────────

# Token del bot (ponlo en Variables de Railway, no aquí en duro)
BOT_TOKEN = os.environ.get("TOKEN", "8561778753:AAH67ygxhEwsmxtrll9WkDaN2BX0sCD-lzo")

# IDs o @username de los canales donde publicar
# Ejemplo: ["-1001234567890", "@micanalpublico"]
CANALES = [
    "@tu_canal_aqui",
]

# Horario permitido para publicar (hora local UTC)
HORA_INICIO = time(8, 0)   # 08:00
HORA_FIN    = time(23, 0)  # 23:00

# Cantidad de publicaciones por día (se elige al azar entre estos valores)
MIN_POSTS = 8
MAX_POSTS = 15

# ── Fotos ──
# URLs raw de GitHub. Formato:
# https://raw.githubusercontent.com/USUARIO/REPO/main/CARPETA/archivo.jpg
FOTOS = [
    "https://raw.githubusercontent.com/TU_USUARIO/mi-bot-Telegram/main/images/foto1.jpg",
    "https://raw.githubusercontent.com/TU_USUARIO/mi-bot-Telegram/main/images/foto2.jpg",
    "https://raw.githubusercontent.com/TU_USUARIO/mi-bot-Telegram/main/images/foto3.jpg",
    "https://raw.githubusercontent.com/TU_USUARIO/mi-bot-Telegram/main/images/foto4.jpg",
    "https://raw.githubusercontent.com/TU_USUARIO/mi-bot-Telegram/main/images/foto5.jpg",
]

# ── Textos (caption de cada foto) ──
TEXTOS = [
    "✨ Texto de ejemplo 1 — edítalo a tu gusto.",
    "🔥 Texto de ejemplo 2 — ponle tu mensaje aquí.",
    "💡 Texto de ejemplo 3 — el que quieras.",
    "🚀 Texto de ejemplo 4 — personalízalo.",
    "🎯 Texto de ejemplo 5 — otro mensaje.",
    "🌟 Texto de ejemplo 6 — el que necesites.",
    "💎 Texto de ejemplo 7 — agrega los tuyos.",
    "📢 Texto de ejemplo 8 — sigue sumando.",
]

# ─────────────────────────────────────────
#  LÓGICA DEL BOT  (no necesitas editar)
# ─────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def segundos_hasta(t: time) -> float:
    """Segundos que faltan hasta la próxima ocurrencia de la hora t (UTC)."""
    ahora = datetime.utcnow()
    objetivo = ahora.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
    if objetivo <= ahora:
        # ya pasó hoy → mañana
        from datetime import timedelta
        objetivo += timedelta(days=1)
    return (objetivo - ahora).total_seconds()


def generar_horario() -> list[float]:
    """
    Genera N timestamps (segundos desde epoch UTC) dentro del
    horario permitido para HOY, distribuidos aleatoriamente.
    """
    n = random.randint(MIN_POSTS, MAX_POSTS)
    ahora = datetime.utcnow()

    inicio_dt = ahora.replace(
        hour=HORA_INICIO.hour, minute=HORA_INICIO.minute, second=0, microsecond=0
    )
    fin_dt = ahora.replace(
        hour=HORA_FIN.hour, minute=HORA_FIN.minute, second=0, microsecond=0
    )

    ventana = (fin_dt - inicio_dt).total_seconds()
    if ventana <= 0:
        logger.warning("Ventana horaria inválida, usando todo el día.")
        ventana = 86400

    offsets = sorted(random.uniform(0, ventana) for _ in range(n))
    return [inicio_dt.timestamp() + off for off in offsets]


async def publicar(bot: Bot, canal: str, foto_url: str, texto: str):
    """Envía una foto con caption a un canal."""
    try:
        await bot.send_photo(
            chat_id=canal,
            photo=foto_url,
            caption=texto,
            parse_mode="HTML",
        )
        logger.info(f"✅ Publicado en {canal}")
    except TelegramError as e:
        logger.error(f"❌ Error al publicar en {canal}: {e}")


async def ciclo_diario(bot: Bot):
    """Ejecuta el ciclo de un día completo."""
    horario = generar_horario()
    logger.info(f"📅 Hoy se publicarán {len(horario)} veces.")

    for ts in horario:
        espera = ts - datetime.utcnow().timestamp()
        if espera > 0:
            logger.info(f"⏳ Próxima publicación en {espera/60:.1f} minutos.")
            await asyncio.sleep(espera)

        foto  = random.choice(FOTOS)
        texto = random.choice(TEXTOS)

        for canal in CANALES:
            await publicar(bot, canal, foto, texto)
            await asyncio.sleep(1)  # pausa entre canales


async def main():
    bot = Bot(token=BOT_TOKEN)

    # Verificar conexión
    me = await bot.get_me()
    logger.info(f"🤖 Bot conectado: @{me.username}")

    while True:
        ahora = datetime.utcnow().time()

        # Si aún no llegó la hora de inicio, esperar
        if ahora < HORA_INICIO:
            espera = segundos_hasta(HORA_INICIO)
            logger.info(f"🕐 Esperando inicio del día en {espera/60:.1f} min.")
            await asyncio.sleep(espera)

        await ciclo_diario(bot)

        # Esperar hasta el inicio del día siguiente
        espera = segundos_hasta(HORA_INICIO)
        logger.info(f"🌙 Día completado. Próximo ciclo en {espera/3600:.1f} horas.")
        await asyncio.sleep(espera)


if __name__ == "__main__":
    asyncio.run(main())

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# Token oficial de tu bot (@relevo_la_joya_bot)
BOT_TOKEN = "8547680119:AAHqHFCFyWftzAtxsri9hnbW7UC_LmzJ4RQ"

# Estados de la conversación
SEDE, RESPONSABLE_ENTREGA, RESPONSABLE_RECIBE, BULTOS, AVANCE, CALIDAD, OBSERVACIONES, CONFIRMACION = range(8)

# Lista de sedes KMMP
SEDES = [
    "RELEVO KMMP – CALLAO",
    "RELEVO KMMP – PUCUSANA",
    "RELEVO KMMP – LOGOP Y TALLERES",
    "RELEVO KMMP – TOQUEPALA",
    "RELEVO KMMP – CUAJONE",
    "RELEVO KMMP – ILO",
    "RELEVO KMMP – SMCV (CERRO VERDE)",
    "RELEVO KMMP – ANTAPACCAY",
    "RELEVO KMMP – QUELLAVECO",
    "RELEVO KMMP – LAS BAMBAS",
    "RELEVO KMMP – ANTAMINA",
    "RELEVO KMMP – CHINALCO"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for i in range(0, len(SEDES), 2):
        row = [InlineKeyboardButton(SEDES[i], callback_data=f"sede_{i}")]
        if i + 1 < len(SEDES):
            row.append(InlineKeyboardButton(SEDES[i+1], callback_data=f"sede_{i+1}"))
        keyboard.append(row)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "?? **SISTEMA DE RELEVO DE TRANSPORTE Y ALMACÉN - KMMP** ??\n\n"
        "Selecciona la **Sede u Operación** correspondiente:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SEDE

async def seleccionar_sede(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    idx = int(query.data.split("_")[1])
    sede_elegida = SEDES[idx]
    context.user_data['sede'] = sede_elegida
    
    user = update.effective_user
    nombre_sugerido = user.first_name + (f" (@{user.username})" if user.username else "")
    context.user_data['user_telegram'] = nombre_sugerido

    keyboard = [[InlineKeyboardButton(f"?? Usar mi usuario ({nombre_sugerido})", callback_data="usar_mi_nombre")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        f"?? Sede: **{sede_elegida}**\n\n"
        "?? **1/6. Responsable que ENTREGA el turno:**\n"
        "Escribe el nombre del operador o presiona el botón para usar tu usuario actual:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return RESPONSABLE_ENTREGA

async def responsable_entrega_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        context.user_data['saliente'] = context.user_data['user_telegram']
        msg = query.message
    else:
        context.user_data['saliente'] = update.message.text
        msg = update.message

    await msg.reply_text(
        "?? **2/6. Responsable que RECIBE el turno:**\n"
        "Escribe el nombre completo del operador entrante:",
        parse_mode="Markdown"
    )
    return RESPONSABLE_RECIBE

async def responsable_recibe_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['entrante'] = update.message.text
    
    await update.message.reply_text(
        "?? **3/6. Cantidad de Bultos:**\n"
        "Ingresa el número total de bultos gestionados en el relevo:",
        parse_mode="Markdown"
    )
    return BULTOS

async def bultos_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bultos'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("25%", callback_data="av_25"), InlineKeyboardButton("50%", callback_data="av_50")],
        [InlineKeyboardButton("75%", callback_data="av_75"), InlineKeyboardButton("100% (Completado)", callback_data="av_100")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "?? **4/6. Porcentaje de Avance:**\n"
        "Selecciona el avance de las operaciones del turno:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return AVANCE

async def avance_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    avance_val = query.data.split("_")[1] + "%"
    context.user_data['avance'] = avance_val

    await query.message.edit_text(
        f"? Avance seleccionado: **{avance_val}**\n\n"
        "?? **5/6. Materiales en Calidad:**\n"
        "Indica cuántos materiales o bultos están retenidos o en revisión por calidad (Escribe '0' si no hay ninguno):",
        parse_mode="Markdown"
    )
    return CALIDAD

async def calidad_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['calidad'] = update.message.text

    await update.message.reply_text(
        "?? **6/6. Observaciones sobre los bultos / transporte:**\n"
        "Escribe detalles de incidencias, faltantes, estado de la carga o escribe **'Ninguna'**:",
        parse_mode="Markdown"
    )
    return OBSERVACIONES

async def observaciones_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['observaciones'] = update.message.text
    
    d = context.user_data
    resumen = (
        f"?? **RESUMEN DE RELEVO - POR CONFIRMAR** ??\n\n"
        f"?? **Sede:** {d['sede']}\n"
        f"?? **Entrega:** {d['saliente']}\n"
        f"?? **Recibe:** {d['entrante']}\n"
        f"?? **Bultos:** {d['bultos']}\n"
        f"?? **Avance:** {d['avance']}\n"
        f"?? **En Calidad:** {d['calidad']}\n"
        f"?? **Observaciones:** {d['observaciones']}\n\n"
        f"¿Deseas enviar este reporte?"
    )

    keyboard = [
        [InlineKeyboardButton("?? Confirmar y Enviar", callback_data="enviar_reporte")],
        [InlineKeyboardButton("? Cancelar / Reiniciar", callback_data="cancelar_reporte")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(resumen, reply_markup=reply_markup, parse_mode="Markdown")
    return CONFIRMACION

async def confirmar_envio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "enviar_reporte":
        d = context.user_data
        reporte_final = (
            f"?? **REPORTE DE RELEVO OFICIAL - KMMP** ??\n\n"
            f"?? **Sede:** {d['sede']}\n"
            f"?? **Saliente:** {d['saliente']}\n"
            f"?? **Entrante:** {d['entrante']}\n"
            f"?? **Total Bultos:** {d['bultos']}\n"
            f"?? **Avance:** {d['avance']}\n"
            f"?? **Materiales en Calidad:** {d['calidad']}\n"
            f"?? **Observaciones sobre bultos:** {d['observaciones']}\n"
        )
        
        await query.message.edit_text(
            "? **¡Relevo registrado y enviado con éxito!**\n\n" + reporte_final,
            parse_mode="Markdown"
        )
    else:
        await query.message.edit_text("? Registro cancelado. Escribe /start para comenzar de nuevo.")
        
    context.user_data.clear()
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada. Usa /start para iniciar de nuevo.")
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SEDE: [CallbackQueryHandler(seleccionar_sede, pattern="^sede_")],
            RESPONSABLE_ENTREGA: [
                CallbackQueryHandler(responsable_entrega_input, pattern="^usar_mi_nombre$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, responsable_entrega_input)
            ],
            RESPONSABLE_RECIBE: [MessageHandler(filters.TEXT & ~filters.COMMAND, responsable_recibe_input)],
            BULTOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bultos_input)],
            AVANCE: [CallbackQueryHandler(avance_input, pattern="^av_")],
            CALIDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, calidad_input)],
            OBSERVACIONES: [MessageHandler(filters.TEXT & ~filters.COMMAND, observaciones_input)],
            CONFIRMACION: [CallbackQueryHandler(confirmar_envio, pattern="^(enviar_reporte|cancelar_reporte)$")]
        },
        fallbacks=[CommandHandler("cancel", cancelar)]
    )
    
    app.add_handler(conv_handler)
    print("Bot de relevos KMMP (@relevo_la_joya_bot) en ejecución...")
    app.run_polling()
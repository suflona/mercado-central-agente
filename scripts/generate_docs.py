"""
Genera los documentos ficticios de 'Mercado Central 24h' (supermercado
colombiano ficticio, abierto 24 horas) para el proyecto Alura Agente.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Body", parent=styles["Normal"],
                           alignment=TA_JUSTIFY, spaceAfter=8, leading=14))
styles.add(ParagraphStyle(name="H1", parent=styles["Heading1"], spaceAfter=12))
styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], spaceAfter=8))


def build_pdf(filename, title, sections):
    path = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=letter,
                             topMargin=2 * cm, bottomMargin=2 * cm,
                             leftMargin=2 * cm, rightMargin=2 * cm)
    story = [Paragraph(title, styles["H1"]), Spacer(1, 6)]
    for heading, content in sections:
        story.append(Paragraph(heading, styles["H2"]))
        for item in content:
            if isinstance(item, tuple):
                bullets = [ListItem(Paragraph(b, styles["Body"])) for b in item[1]]
                story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=18))
                story.append(Spacer(1, 6))
            else:
                story.append(Paragraph(item, styles["Body"]))
        story.append(Spacer(1, 4))
    doc.build(story)
    print(f"OK -> {path}")


# ---------------------------------------------------------------------------
# 1. FAQ
# ---------------------------------------------------------------------------
build_pdf(
    "FAQ_Mercado_Central_24h.pdf",
    "Preguntas Frecuentes — Mercado Central 24h",
    [
        ("¿Cuál es el horario de atención?", [
            "Mercado Central 24h está abierto los 365 días del año, "
            "las 24 horas del día, en todas nuestras sedes. El servicio "
            "a domicilio opera de 6:00 a.m. a 11:00 p.m.",
        ]),
        ("¿Hacen domicilios?", [
            "Sí. Puedes pedir a domicilio desde la app o la página web. "
            "El tiempo estimado de entrega es de 45 a 90 minutos según la "
            "zona. El costo de envío es gratis en compras superiores a "
            "$80.000 COP; por debajo de ese monto, el domicilio tiene un "
            "costo de $6.000 COP.",
        ]),
        ("¿Qué métodos de pago aceptan?", [
            ("Aceptamos los siguientes métodos:", [
                "Efectivo (solo en tienda física).",
                "Tarjetas débito y crédito (Visa, Mastercard, American Express).",
                "PSE y Nequi/Daviplata para pedidos por app.",
                "Bonos de mercado propios de Mercado Central 24h.",
            ]),
        ]),
        ("¿Puedo usar cupones de descuento?", [
            "Sí, los cupones se aplican en el checkout de la app ingresando "
            "el código. Solo se puede usar un cupón por pedido, y no son "
            "acumulables con otras promociones vigentes.",
        ]),
        ("¿Tienen programa de fidelización?", [
            "Sí, el programa 'Puntos Central' acumula 1 punto por cada "
            "$1.000 COP de compra. Cada 500 puntos equivalen a $5.000 COP "
            "de descuento en tu próxima compra. Los puntos se consultan "
            "en la app en la sección 'Mis Puntos'.",
        ]),
        ("¿Venden productos a granel?", [
            "Sí, contamos con sección de granos, frutos secos y "
            "detergentes a granel en tiendas físicas. Esta opción no "
            "está disponible para pedidos a domicilio por el momento.",
        ]),
    ],
)

# ---------------------------------------------------------------------------
# 2. Política de Atención al Cliente y Devoluciones
# ---------------------------------------------------------------------------
build_pdf(
    "Politica_Atencion_Cliente_y_Devoluciones_Mercado_Central_24h.pdf",
    "Política de Atención al Cliente y Devoluciones — Mercado Central 24h",
    [
        ("1. Devoluciones de productos", [
            ("Aceptamos devoluciones bajo las siguientes condiciones:", [
                "Productos no perecederos: hasta 5 días calendario después de la compra, con factura y empaque original.",
                "Productos perecederos (frutas, verduras, lácteos, carnes): solo se aceptan devoluciones el mismo día de la compra, por defecto de calidad comprobado.",
                "Electrodomésticos y artículos para el hogar: hasta 30 días calendario, sin uso y con empaque original, conforme al derecho de retracto del Estatuto del Consumidor (Ley 1480 de 2011).",
            ]),
        ]),
        ("2. Procedimiento para devolver un producto", [
            "Puedes acercarte al punto de 'Servicio al Cliente' de cualquier "
            "sede con el producto y la factura (física o digital, enviada "
            "por correo o disponible en la app). El reembolso se realiza "
            "por el mismo medio de pago original, en un plazo máximo de 5 "
            "días hábiles para pagos electrónicos, o de forma inmediata si "
            "fue en efectivo.",
        ]),
        ("3. Productos con defecto de fábrica", [
            "Si el producto presenta un defecto de fábrica, Mercado "
            "Central 24h gestiona el cambio directo o la devolución del "
            "dinero sin necesidad de que conserves el empaque original, "
            "conforme a la garantía legal mínima de un año establecida "
            "por el Estatuto del Consumidor.",
        ]),
        ("4. Quejas y reclamos", [
            "Puedes radicar una queja o reclamo en el módulo de 'PQR' de "
            "la app, en el punto de servicio al cliente de cualquier "
            "tienda, o al correo servicioalcliente@mercadocentral24h.com.co. "
            "El tiempo de respuesta máximo es de 15 días hábiles, conforme "
            "a la normativa vigente de protección al consumidor.",
        ]),
        ("5. Atención prioritaria", [
            "Mujeres embarazadas, personas en situación de discapacidad y "
            "adultos mayores tienen atención prioritaria en las filas de "
            "todas nuestras cajas y puntos de servicio, conforme a la Ley "
            "1091 de 2006 y normativa relacionada.",
        ]),
    ],
)

# ---------------------------------------------------------------------------
# 3. Reglamento Interno y Procedimientos Operativos
# ---------------------------------------------------------------------------
build_pdf(
    "Reglamento_Interno_Mercado_Central_24h.pdf",
    "Reglamento Interno y Procedimientos Operativos — Mercado Central 24h",
    [
        ("1. Horarios y turnos del personal", [
            ("El personal opera en 3 turnos rotativos para cubrir el servicio 24 horas:", [
                "Turno mañana: 6:00 a.m. - 2:00 p.m.",
                "Turno tarde: 2:00 p.m. - 10:00 p.m.",
                "Turno noche: 10:00 p.m. - 6:00 a.m. (recargo nocturno según Código Sustantivo del Trabajo).",
            ]),
        ]),
        ("2. Manejo de inventario y control de vencimientos", [
            "Los productos perecederos se revisan diariamente en el turno "
            "de la mañana. Todo producto próximo a vencer (5 días o menos) "
            "debe marcarse con descuento del 30% y ubicarse en la góndola "
            "de 'Ofertas del Día'. Productos vencidos se retiran de "
            "inmediato y se registran en el sistema de mermas.",
        ]),
        ("3. Protocolo de caja", [
            ("Cada cajero debe:", [
                "Verificar el fondo de caja al inicio y cierre de turno.",
                "Solicitar identificación en compras de bebidas alcohólicas o cigarrillos.",
                "Reportar cualquier faltante o sobrante de caja superior a $10.000 COP al supervisor de turno.",
            ]),
        ]),
        ("4. Seguridad y prevención de pérdidas", [
            "Todas las sedes cuentan con circuito cerrado de cámaras y "
            "personal de seguridad en turno noche. Cualquier incidente de "
            "hurto debe reportarse de inmediato al supervisor y quedar "
            "registrado en el formato de incidentes, disponible en el "
            "sistema interno.",
        ]),
        ("5. Recepción de proveedores", [
            "Los proveedores solo pueden hacer entregas en la franja de "
            "5:00 a.m. a 12:00 p.m., previa cita coordinada con el área de "
            "compras. Toda mercancía debe verificarse contra la orden de "
            "compra antes de firmar el recibido.",
        ]),
    ],
)

print("Todos los PDFs generados correctamente.")

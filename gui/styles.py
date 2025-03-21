"""
Archivo que contiene los estilos CSS para la aplicación
"""

# Definición de colores principales
main_color = "#00788E"
secondary_color = "#2CD5C4"
third_color = "#FFA500"
fourth_color = "#FFD700"
fifth_color = "#FF6347"
text_color = "#333333"
background_light = "rgba(245, 245, 245, 200)"

# Estilos de ventanas
WINDOW_GRADIENT = f"""
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 {secondary_color}, stop: 1 {main_color}
    );
"""

# Estilos de contenedores
ROUNDED_FRAME = f"""
    background: {background_light};
    border-radius: 10px;
    padding: 20px;
"""

# Puedes añadir más estilos según vayas necesitando
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {main_color};
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {secondary_color};
    }}
    QPushButton:pressed {{
        background-color: #005D6E;
    }}
"""

BUTTON_STYLE_2 = f"""
        QToolButton {{
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 1,
                stop: 0 {secondary_color}, stop: 1 {main_color}
            );
            color: white;
            font-size: 20px;
            font-weight: bold;
            border-radius: 15px;
            padding: 15px;
        }}
        QToolButton::menu-indicator {{  /* Oculta el indicador de menú si no se usa */
            image: none;
        }}
    """
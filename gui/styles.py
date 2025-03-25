"""
Archivo que contiene los estilos CSS para la aplicación
"""

# Definición de colores principales
main_color = "#00788E"
secondary_color = "#2CD5C4"
third_color = "#F5F5F5"
fourth_color = "#666666"
fifth_color = "#999999"
text_color = "#333333"
background_light = "rgba(245, 245, 245, 200)"

# Estilos de ventanas
WINDOW_GRADIENT = f"""
    QDialog {{
        background: qlineargradient(
            x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {main_color}, stop: 1 {secondary_color}
        );
    }}
"""

# Gradiente para ventanas secundarias
SECONDARY_WINDOW_GRADIENT = f"""
    QDialog {{
        background: qlineargradient(
            x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {main_color}, stop: 1 {third_color}
        );
    }}
"""

# Estilos de contenedores
ROUNDED_FRAME = f"""
    background: {background_light};
    border-radius: 10px;
    padding: 20px;
"""

# Botones básicos
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

# Botones con gradiente
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

# GroupBox para formularios
GROUP_BOX_STYLE = f"""
    QGroupBox {{
        border: 2px solid rgba(255, 255, 255, 100);
        border-radius: 8px;
        margin-top: 5px;
        padding-top: 5px;
        background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 1,
            stop: 0 rgba(44, 213, 196, 150), stop: 1 rgba(0, 120, 142, 150)
        );
    }}
"""

# Estilo para etiquetas en formularios
LABEL_STYLE = """
    QLabel {
        font-size: 16px;
        font-weight: bold;
        color: white;
        background-color: transparent;
        margin-bottom: 0px;
        qproperty-alignment: AlignCenter;
    }
"""

# Estilo para campos de entrada
INPUT_STYLE = f"""
    QLineEdit, QComboBox, QDoubleSpinBox {{
        padding: 8px;
        border: 2px solid rgba(255, 255, 255, 150);
        border-radius: 6px;
        background-color: rgba(255, 255, 255, 200);
        min-height: 25px;
        font-size: 16px;
        margin-top: 0px;
    }}
    
    QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {{
        border: 2px solid {secondary_color};
        background-color: white;
    }}
    
    QComboBox::drop-down {{
        border: 0px;
        background: transparent;
    }}
    
    QComboBox::down-arrow {{
        image: url(assets/icons/down-arrow.png);
        width: 12px;
        height: 12px;
    }}
    
    QDoubleSpinBox {{
        padding-right: 15px;
    }}
    
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        width: 0px;
        height: 0px;
    }}
"""

# Estilo para tablas
TABLE_STYLE = f"""
    QTableView {{
        background-color: white;
        border: 1px solid #DDDDDD;
        gridline-color: #DDDDDD;
        border-radius: 5px;
    }}
    QHeaderView::section {{
        background-color: {main_color};
        color: white;
        padding: 10px;
        border: 1px solid #005D6E;
        font-weight: bold;
        font-size: 14px;
        min-height: 30px;
    }}
    QTableView::item:selected {{
        background-color: #BBDEFB;
    }}
"""

# Estilo para QMessageBox
MESSAGE_BOX_STYLE = """
    QMessageBox {
        background-color: #F5F5F5;
    }
"""

# Botón pequeño para formularios
FORM_BUTTON_STYLE = BUTTON_STYLE_2.replace("QToolButton", "QPushButton").replace("font-size: 20px", "font-size: 14px")
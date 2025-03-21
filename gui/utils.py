from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor

def recolor_icon(icon_path, color):
    """
    Función para recolorear íconos
    
    Args:
        icon_path (str): Ruta al archivo de ícono
        color (str): Color en formato hexadecimal
        
    Returns:
        QIcon: Ícono recoloreado
    """
    pixmap = QPixmap(icon_path)
    painter = QPainter(pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return QIcon(pixmap)

# Puedes añadir más funciones de utilidad relacionadas con la GUI aquí
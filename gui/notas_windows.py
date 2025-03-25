import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, 
    QPushButton, QSizePolicy, QApplication,
    QLabel, QLineEdit, QComboBox, QGridLayout, QGroupBox,
    QDoubleSpinBox, QMessageBox, QTableView, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QStandardItemModel, QStandardItem
# Importar los estilos
from styles import WINDOW_GRADIENT, ROUNDED_FRAME, BUTTON_STYLE_2

class NotasWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Notas")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # Dimensiones iniciales
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)  # Mostrar maximizada

        # Aplicar estilos
        self.apply_styles()
        
        # Crear la interfaz
        self.setup_ui()
    
    def apply_styles(self):
        """Método para aplicar los estilos importados del archivo styles.py"""
        self.setStyleSheet(WINDOW_GRADIENT)
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Layout principal directamente en el diálogo (sin frame contenedor)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Crear el contenedor para los datos de producto/servicio
        self.crear_grupo_producto_servicio(main_layout)
        
        # Crear tabla para mostrar los items agregados
        self.crear_tabla_items(main_layout)
        
        # Añadir espacio flexible para empujar los botones hacia abajo
        main_layout.addStretch(1)
        
        # Crear layout para los botones (fila horizontal)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)  # Espacio entre botones
        botones_layout.setContentsMargins(0, 0, 0, 0)  # Sin márgenes adicionales
        
        # Usamos el estilo BUTTON_STYLE_2 importado de styles.py
        # Modificamos para usar QPushButton en lugar de QToolButton
        estilo_boton = BUTTON_STYLE_2.replace("QToolButton", "QPushButton")
        
        # Textos de los botones
        textos_botones = ["Nuevo", "Guardar", "Cancelar", "Buscar", "Editar", "Limpiar", "Imprimir"]
        
        # Crear los botones y añadirlos al layout
        self.botones = []
        for texto in textos_botones:
            boton = QPushButton(texto)
            boton.setStyleSheet(estilo_boton)
            boton.setCursor(Qt.PointingHandCursor)
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Expandir horizontalmente
            botones_layout.addWidget(boton)
            self.botones.append(boton)
        
        # Añadir el layout de botones al layout principal
        main_layout.addLayout(botones_layout)

        # Asignar el layout al diálogo
        self.setLayout(main_layout)
        
        # Conectar señales
        self.conectar_senales()
    
    def crear_grupo_producto_servicio(self, parent_layout):
        """Crear grupo de campos para producto/servicio"""
        # Crear un groupbox para agrupar los elementos - sin título
        grupo = QGroupBox("")
        grupo.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(255, 255, 255, 100);
                border-radius: 8px;
                margin-top: 5px;
                padding-top: 5px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(44, 213, 196, 150), stop: 1 rgba(0, 120, 142, 150)
                );
            }
        """)
        
        # Crear un grid layout para organizar los campos (más compacto)
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Estilos para labels e inputs
        label_estilo = """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                margin-bottom: 0px;
                qproperty-alignment: AlignCenter;
            }
        """
        
        input_estilo = """
            QLineEdit, QComboBox, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid rgba(255, 255, 255, 150);
                border-radius: 6px;
                background-color: rgba(255, 255, 255, 200);
                min-height: 25px;
                font-size: 16px;
                margin-top: 0px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #2CD5C4;
                background-color: white;
            }
            
            QComboBox::drop-down {
                border: 0px;
                background: transparent;
            }
            
            QComboBox::down-arrow {
                image: url(assets/icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
            
            QDoubleSpinBox {
                padding-right: 15px;
            }
            
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0px;
                height: 0px;
            }
        """
        
        # Definir proporciones de columnas (stretch)
        # Producto(2), Cantidad(1), Descripción(6), Precio(2), Importe(2)
        grid_layout.setColumnStretch(0, 2)    # Producto
        grid_layout.setColumnStretch(1, 1)    # Cantidad (reducido)
        grid_layout.setColumnStretch(2, 6)    # Descripción (aumentado)
        grid_layout.setColumnStretch(3, 2)    # Precio (reducido)
        grid_layout.setColumnStretch(4, 2)    # Importe
        grid_layout.setColumnStretch(5, 1)    # Botón Agregar
        
        # ---- Fila 1: Labels ----
        lbl_producto = QLabel("Producto o Servicio")
        lbl_producto.setStyleSheet(label_estilo)
        grid_layout.addWidget(lbl_producto, 0, 0)
        
        lbl_cantidad = QLabel("Cantidad")
        lbl_cantidad.setStyleSheet(label_estilo)
        grid_layout.addWidget(lbl_cantidad, 0, 1)
        
        lbl_descripcion = QLabel("Descripción")
        lbl_descripcion.setStyleSheet(label_estilo)
        grid_layout.addWidget(lbl_descripcion, 0, 2)
        
        lbl_precio = QLabel("Precio Unitario")
        lbl_precio.setStyleSheet(label_estilo)
        grid_layout.addWidget(lbl_precio, 0, 3)
        
        lbl_importe = QLabel("Importe")
        lbl_importe.setStyleSheet(label_estilo)
        grid_layout.addWidget(lbl_importe, 0, 4)
        
        # ---- Fila 2: Campos ----
        self.cmb_producto = QComboBox()
        self.cmb_producto.addItems(["Seleccione...", "Producto", "Servicio"])
        self.cmb_producto.setStyleSheet(input_estilo)
        grid_layout.addWidget(self.cmb_producto, 1, 0)
        
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setStyleSheet(input_estilo)
        self.txt_cantidad.setPlaceholderText("Cantidad")
        # Validador para permitir solo números
        self.txt_cantidad.setValidator(QDoubleValidator())
        grid_layout.addWidget(self.txt_cantidad, 1, 1)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(input_estilo)
        self.txt_descripcion.setPlaceholderText("Ingrese descripción")
        grid_layout.addWidget(self.txt_descripcion, 1, 2)
        
        self.txt_precio = QLineEdit()
        self.txt_precio.setStyleSheet(input_estilo)
        self.txt_precio.setPlaceholderText("$0.00")
        # Validador para permitir solo números con decimales
        self.txt_precio.setValidator(QDoubleValidator(0.00, 9999999.99, 2))
        grid_layout.addWidget(self.txt_precio, 1, 3)
        
        self.txt_importe = QDoubleSpinBox()
        self.txt_importe.setReadOnly(True)
        self.txt_importe.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.txt_importe.setRange(0, 9999999.99)
        self.txt_importe.setDecimals(2)
        self.txt_importe.setPrefix("$ ")
        self.txt_importe.setStyleSheet(input_estilo)
        grid_layout.addWidget(self.txt_importe, 1, 4)
        
        # Botón para agregar a la tabla
        estilo_boton = BUTTON_STYLE_2.replace("QToolButton", "QPushButton")
        # Reducir tamaño de fuente para el botón
        estilo_boton = estilo_boton.replace("font-size: 20px", "font-size: 14px")
        
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setStyleSheet(estilo_boton)
        self.btn_agregar.setCursor(Qt.PointingHandCursor)
        grid_layout.addWidget(self.btn_agregar, 1, 5)
        
        # Establecer el layout del grupo
        grupo.setLayout(grid_layout)
        
        # Añadir el grupo al layout principal
        parent_layout.addWidget(grupo)
    
    def crear_tabla_items(self, parent_layout):
        """Crear tabla para mostrar los items agregados usando QTableView"""
        # Crear modelo de datos
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels(["Cantidad", "Descripción", "Precio Unitario", "Importe"])
        
        # Crear vista de tabla
        self.tabla_items = QTableView()
        self.tabla_items.setModel(self.tabla_model)
        self.tabla_items.horizontalHeader().setVisible(True)
        self.tabla_items.verticalHeader().setVisible(False)
        
        # Estilo para la tabla
        self.tabla_items.setStyleSheet("""
            QTableView {
                background-color: white;
                border: 1px solid #DDDDDD;
                gridline-color: #DDDDDD;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #00788E;
                color: white;
                padding: 10px;
                border: 1px solid #005D6E;
                font-weight: bold;
                font-size: 14px;
                min-height: 30px;
            }
            QTableView::item:selected {
                background-color: #BBDEFB;
            }
        """)
        
        # Configurar ancho de columnas
        header = self.tabla_items.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Cantidad
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Descripción se expande
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Precio Unitario
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Importe
        
        # Configurar comportamiento de selección
        self.tabla_items.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_items.setSelectionMode(QTableView.SingleSelection)
        
        # Establecer altura mínima y agregar al layout
        self.tabla_items.setMinimumHeight(200)
        parent_layout.addWidget(self.tabla_items)
    
    def conectar_senales(self):
        """Conectar las señales de los controles"""
        # Calcular importe cuando cambia cantidad o precio unitario
        self.txt_cantidad.textChanged.connect(self.calcular_importe)
        self.txt_precio.textChanged.connect(self.calcular_importe)
        
        # Manejar cambio en el combo de producto/servicio
        self.cmb_producto.currentIndexChanged.connect(self.manejar_cambio_tipo)
        
        # Conectar botón agregar
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
    
    def manejar_cambio_tipo(self):
        """Maneja el cambio en el combo de producto/servicio"""
        seleccion = self.cmb_producto.currentText()
        
        if seleccion == "Servicio":
            # Si es servicio, poner "-" en cantidad y deshabilitar el campo
            self.txt_cantidad.setText("-")
            self.txt_cantidad.setReadOnly(True)
        else:
            # Si no es servicio, habilitar el campo de cantidad y dejarlo vacío si tiene "-"
            if self.txt_cantidad.text() == "-":
                self.txt_cantidad.setText("")
            self.txt_cantidad.setReadOnly(False)
    
    def calcular_importe(self):
        """Calcular el importe basado en cantidad y precio unitario"""
        try:
            # Determinar cantidad según el tipo de producto/servicio
            if self.cmb_producto.currentText() == "Servicio" and self.txt_cantidad.text() == "-":
                cantidad = 1.0  # Si es servicio, considerar como 1 para el cálculo
            else:
                cantidad = float(self.txt_cantidad.text()) if self.txt_cantidad.text() else 0
            
            # Limpiar el texto del precio para manejar posibles formatos como "$1,234.56"
            precio_texto = self.txt_precio.text()
            precio_texto = precio_texto.replace("$", "").replace(",", "").strip()
            precio = float(precio_texto) if precio_texto else 0
            
            importe = cantidad * precio
            self.txt_importe.setValue(importe)
            
            # Formatear el precio con formato de moneda
            if precio > 0 and not self.txt_precio.hasFocus():
                self.txt_precio.setText(f"${precio:.2f}")
        except ValueError:
            # Si hay un error en la conversión, mostrar 0
            self.txt_importe.setValue(0)
    
    def agregar_a_tabla(self):
        """Agrega los datos del formulario a la tabla"""
        # Verificar datos obligatorios
        if not self.validar_datos():
            return
            
        # Obtener los datos
        if self.cmb_producto.currentText() == "Servicio":
            cantidad = "-"  # Para mostrar
            cantidad_calculo = 1  # Para el cálculo
        else:
            cantidad = self.txt_cantidad.text()
            cantidad_calculo = float(cantidad)
            
        descripcion = self.txt_descripcion.text()
        
        # Formatear precio unitario
        precio_texto = self.txt_precio.text()
        precio_texto = precio_texto.replace("$", "").replace(",", "").strip()
        precio = float(precio_texto)
        precio_formateado = f"${precio:.2f}"
        
        # Calcular importe
        importe = cantidad_calculo * precio
        importe_formateado = f"${importe:.2f}"
        
        # Crear items para añadir al modelo
        item_cantidad = QStandardItem(cantidad)
        item_cantidad.setTextAlignment(Qt.AlignCenter)
        
        item_descripcion = QStandardItem(descripcion)
        item_descripcion.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        item_precio = QStandardItem(precio_formateado)
        item_precio.setTextAlignment(Qt.AlignCenter)
        
        item_importe = QStandardItem(importe_formateado)
        item_importe.setTextAlignment(Qt.AlignCenter)
        
        # Añadir fila al modelo
        fila = self.tabla_model.rowCount()
        self.tabla_model.setItem(fila, 0, item_cantidad)
        self.tabla_model.setItem(fila, 1, item_descripcion)
        self.tabla_model.setItem(fila, 2, item_precio)
        self.tabla_model.setItem(fila, 3, item_importe)
        
        # Limpiar el formulario para un nuevo ingreso
        self.limpiar_formulario()
    
    def validar_datos(self):
        """Valida que los datos del formulario sean correctos"""
        tipo = self.cmb_producto.currentText()
        
        if tipo == "Seleccione...":
            QMessageBox.warning(self, "Advertencia", "Seleccione el tipo de ítem (Producto o Servicio).")
            return False
            
        if tipo == "Producto" and (not self.txt_cantidad.text() or self.txt_cantidad.text() == "0"):
            QMessageBox.warning(self, "Advertencia", "Ingrese una cantidad válida.")
            return False
            
        if not self.txt_descripcion.text():
            QMessageBox.warning(self, "Advertencia", "Ingrese una descripción.")
            return False
            
        precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
        if not precio_texto or float(precio_texto) <= 0:
            QMessageBox.warning(self, "Advertencia", "Ingrese un precio válido.")
            return False
            
        return True
    
    def limpiar_formulario(self):
        """Limpia el formulario para un nuevo ingreso"""
        self.cmb_producto.setCurrentIndex(0)  # Seleccione...
        self.txt_cantidad.setReadOnly(False)
        self.txt_cantidad.setText("")
        self.txt_descripcion.setText("")
        self.txt_precio.setText("")
        self.txt_importe.setValue(0)
        self.cmb_producto.setFocus()
    
    def closeEvent(self, event):
        """Evento que se dispara al cerrar la ventana"""
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotasWindow()
    window.show()
    sys.exit(app.exec_())
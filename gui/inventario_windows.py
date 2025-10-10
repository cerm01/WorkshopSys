import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QGridLayout, QGroupBox, QMessageBox, QTableView, 
    QHeaderView, QFrame, QWidget, QComboBox, QSpinBox, 
    QDoubleSpinBox, QTabWidget, QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor

from styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE,
    LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, MESSAGE_BOX_STYLE
)


class InventarioWindow(QDialog):
    """Sistema completo de gestión de inventario"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Gestión de Inventario")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        
        # Configuración
        self.setMinimumSize(1400, 800)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)
        
        # Variables de control
        self.producto_en_edicion = None
        self.modo_edicion = False
        self.productos_data = []
        self.movimientos_data = []
        self.proximo_id = 1
        
        # Configurar UI
        self.setup_ui()
        self.conectar_senales()
        self.cargar_datos_ejemplo()
    
    def setup_ui(self):
        """Configurar interfaz con pestañas"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Crear pestañas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 150);
                color: #333;
                padding: 10px 20px;
                margin-right: 2px;
                border-radius: 5px 5px 0 0;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2CD5C4, stop: 1 #00788E
                );
                color: white;
            }
        """)
        
        # Pestaña 1: Productos
        self.tab_productos = self.crear_tab_productos()
        self.tabs.addTab(self.tab_productos, "📦 Productos")
        
        # Pestaña 2: Movimientos
        self.tab_movimientos = self.crear_tab_movimientos()
        self.tabs.addTab(self.tab_movimientos, "📊 Movimientos")
        
        # Pestaña 3: Alertas
        self.tab_alertas = self.crear_tab_alertas()
        self.tabs.addTab(self.tab_alertas, "⚠️ Alertas de Stock")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
    
    # ==================== PESTAÑA DE PRODUCTOS ====================
    
    def crear_tab_productos(self):
        """Pestaña principal de productos"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Formulario de producto
        self.crear_formulario_producto(layout)
        
        # Layout horizontal: Tabla + Panel
        contenedor = QHBoxLayout()
        self.crear_tabla_productos(contenedor)
        self.crear_panel_detalle_producto(contenedor)
        layout.addLayout(contenedor, 1)
        
        # Botones
        self.crear_botones_productos(layout)
        
        widget.setLayout(layout)
        return widget
    
    def crear_formulario_producto(self, parent_layout):
        """Formulario compacto para productos"""
        grupo = QGroupBox()
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        grupo.setMaximumHeight(200)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(15, 15, 15, 15)
        
        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background: transparent;
                min-width: 80px;
                max-width: 80px;
            }
        """
        
        # FILA 1: Código | Nombre | Categoría | Ubicación
        row = 0
        labels_campos = [
            ("Código:", "txt_codigo", "SKU-001"),
            ("Nombre:", "txt_nombre_prod", "Nombre del producto"),
            ("Categoría:", "cmb_categoria", None),
            ("Ubicación:", "txt_ubicacion", "Estante A1")
        ]
        
        for i, (texto, attr, placeholder) in enumerate(labels_campos):
            col_label = i * 2
            col_campo = i * 2 + 1
            
            lbl = QLabel(texto)
            lbl.setStyleSheet(label_style)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid.addWidget(lbl, row, col_label)
            
            if attr == "cmb_categoria":
                campo = QComboBox()
                campo.setStyleSheet(INPUT_STYLE)
                campo.addItems([
                    "Refacciones", "Herramientas", "Consumibles",
                    "Accesorios", "Equipos", "Otros"
                ])
            else:
                campo = QLineEdit()
                campo.setStyleSheet(INPUT_STYLE)
                campo.setPlaceholderText(placeholder)
            
            setattr(self, attr, campo)
            grid.addWidget(campo, row, col_campo)
        
        # FILA 2: Proveedor | Precio Compra | Precio Venta | Stock Min
        row = 1
        labels_campos = [
            ("Proveedor:", "txt_proveedor", "Nombre proveedor"),
            ("P. Compra:", "spin_precio_compra", None),
            ("P. Venta:", "spin_precio_venta", None),
            ("Stock Mín:", "spin_stock_min", None)
        ]
        
        for i, (texto, attr, placeholder) in enumerate(labels_campos):
            col_label = i * 2
            col_campo = i * 2 + 1
            
            lbl = QLabel(texto)
            lbl.setStyleSheet(label_style)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            grid.addWidget(lbl, row, col_label)
            
            if "spin_precio" in attr:
                campo = QDoubleSpinBox()
                campo.setRange(0, 999999.99)
                campo.setDecimals(2)
                campo.setPrefix("$ ")
                campo.setStyleSheet(INPUT_STYLE)
            elif attr == "spin_stock_min":
                campo = QSpinBox()
                campo.setRange(0, 99999)
                campo.setStyleSheet(INPUT_STYLE)
            else:
                campo = QLineEdit()
                campo.setStyleSheet(INPUT_STYLE)
                campo.setPlaceholderText(placeholder)
            
            setattr(self, attr, campo)
            grid.addWidget(campo, row, col_campo)
        
        # FILA 3: Stock Actual | Descripción (ocupa 3 columnas) | ID
        row = 2
        
        # Stock Actual
        lbl = QLabel("Stock:")
        lbl.setStyleSheet(label_style)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl, row, 0)
        
        self.spin_stock_actual = QSpinBox()
        self.spin_stock_actual.setRange(0, 99999)
        self.spin_stock_actual.setStyleSheet(INPUT_STYLE)
        grid.addWidget(self.spin_stock_actual, row, 1)
        
        # Descripción
        lbl = QLabel("Descripción:")
        lbl.setStyleSheet(label_style)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl, row, 2)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(INPUT_STYLE)
        self.txt_descripcion.setPlaceholderText("Descripción breve del producto")
        grid.addWidget(self.txt_descripcion, row, 3, 1, 3)  # Ocupa 3 columnas
        
        # ID
        lbl = QLabel("ID:")
        lbl.setStyleSheet(label_style)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl, row, 6)
        
        self.txt_id_prod = QLineEdit()
        self.txt_id_prod.setReadOnly(True)
        self.txt_id_prod.setStyleSheet(INPUT_STYLE + "background-color: #E8E8E8; color: #666;")
        self.txt_id_prod.setPlaceholderText("Auto")
        grid.addWidget(self.txt_id_prod, row, 7)
        
        # Configurar columnas
        for col in range(0, 8, 2):
            grid.setColumnStretch(col, 0)
            grid.setColumnMinimumWidth(col, 80)
        for col in range(1, 8, 2):
            grid.setColumnStretch(col, 1)
        
        grupo.setLayout(grid)
        parent_layout.addWidget(grupo)
    
    def crear_tabla_productos(self, parent_layout):
        """Tabla de productos"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título y búsqueda
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel("📦 Lista de Productos")
        lbl_titulo.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #2CD5C4, stop: 1 #00788E
            );
            padding: 8px;
            border-radius: 5px;
        """)
        header_layout.addWidget(lbl_titulo)
        
        # Campo de búsqueda
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setStyleSheet(INPUT_STYLE)
        self.txt_buscar.setPlaceholderText("🔍 Buscar producto...")
        self.txt_buscar.setMaximumWidth(300)
        header_layout.addWidget(self.txt_buscar)
        
        layout.addLayout(header_layout)
        
        # Modelo de tabla
        self.tabla_productos_model = QStandardItemModel()
        self.tabla_productos_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Stock", "P. Venta", "Estado"
        ])
        
        self.tabla_productos = QTableView()
        self.tabla_productos.setModel(self.tabla_productos_model)
        self.tabla_productos.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_productos.setSelectionMode(QTableView.SingleSelection)
        self.tabla_productos.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_productos.setStyleSheet(TABLE_STYLE)
        self.tabla_productos.verticalHeader().setDefaultSectionSize(35)
        
        header = self.tabla_productos.horizontalHeader()
        header.setFixedHeight(40)
        
        layout.addWidget(self.tabla_productos)
        widget.setLayout(layout)
        parent_layout.addWidget(widget, 7)
    
    def crear_panel_detalle_producto(self, parent_layout):
        """Panel con detalles del producto"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 200);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        titulo = QLabel("📄 Detalles del Producto")
        titulo.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00788E;
            padding: 8px;
            background: rgba(44, 213, 196, 0.2);
            border-radius: 5px;
        """)
        layout.addWidget(titulo)
        
        # Contenedor scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        detalle_widget = QWidget()
        detalle_layout = QVBoxLayout()
        
        # Labels de detalle
        self.labels_detalle_prod = {}
        campos = [
            ('id', '🆔 ID:', '---'),
            ('codigo', '🏷️ Código:', '---'),
            ('nombre', '📦 Nombre:', '---'),
            ('categoria', '📂 Categoría:', '---'),
            ('stock', '📊 Stock Actual:', '---'),
            ('stock_min', '⚠️ Stock Mínimo:', '---'),
            ('ubicacion', '📍 Ubicación:', '---'),
            ('proveedor', '🏭 Proveedor:', '---'),
            ('precio_compra', '💵 Precio Compra:', '---'),
            ('precio_venta', '💰 Precio Venta:', '---'),
            ('descripcion', '📝 Descripción:', '---')
        ]
        
        for key, titulo_campo, valor in campos:
            frame = self.crear_label_detalle(titulo_campo, valor)
            self.labels_detalle_prod[key] = frame
            detalle_layout.addWidget(frame)
            
            if key == 'ubicacion':
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("background-color: rgba(0, 120, 142, 0.3); max-height: 2px;")
                detalle_layout.addWidget(sep)
        
        detalle_layout.addStretch()
        detalle_widget.setLayout(detalle_layout)
        scroll.setWidget(detalle_widget)
        
        layout.addWidget(scroll)
        panel.setLayout(layout)
        parent_layout.addWidget(panel, 3)
    
    def crear_botones_productos(self, parent_layout):
        """Botones de acción para productos"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        botones = [
            ("Nuevo", self.nuevo_producto),
            ("Guardar", self.guardar_producto),
            ("Editar", self.editar_producto),
            ("Eliminar", self.eliminar_producto),
            ("Entrada", self.registrar_entrada),
            ("Salida", self.registrar_salida),
            ("Limpiar", self.limpiar_formulario_producto)
        ]
        
        for texto, funcion in botones:
            btn = QPushButton(texto)
            btn.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(50)
            btn.clicked.connect(funcion)
            layout.addWidget(btn)
        
        parent_layout.addLayout(layout)
    
    # ==================== PESTAÑA DE MOVIMIENTOS ====================
    
    def crear_tab_movimientos(self):
        """Pestaña de historial de movimientos"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        lbl_titulo = QLabel("📊 Historial de Movimientos de Inventario")
        lbl_titulo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #2CD5C4, stop: 1 #00788E
            );
            padding: 12px;
            border-radius: 5px;
        """)
        layout.addWidget(lbl_titulo)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        
        lbl_filtro = QLabel("Filtrar por:")
        lbl_filtro.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        filtros_layout.addWidget(lbl_filtro)
        
        self.cmb_filtro_tipo = QComboBox()
        self.cmb_filtro_tipo.setStyleSheet(INPUT_STYLE)
        self.cmb_filtro_tipo.addItems(["Todos", "Entradas", "Salidas"])
        self.cmb_filtro_tipo.currentTextChanged.connect(self.filtrar_movimientos)
        filtros_layout.addWidget(self.cmb_filtro_tipo)
        
        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)
        
        # Tabla de movimientos
        self.tabla_movimientos_model = QStandardItemModel()
        self.tabla_movimientos_model.setHorizontalHeaderLabels([
            "ID", "Fecha", "Tipo", "Producto", "Cantidad", "Usuario", "Motivo"
        ])
        
        self.tabla_movimientos = QTableView()
        self.tabla_movimientos.setModel(self.tabla_movimientos_model)
        self.tabla_movimientos.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_movimientos.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_movimientos.setStyleSheet(TABLE_STYLE)
        self.tabla_movimientos.verticalHeader().setDefaultSectionSize(35)
        
        header = self.tabla_movimientos.horizontalHeader()
        header.setFixedHeight(40)
        header.setStretchLastSection(True)
        
        layout.addWidget(self.tabla_movimientos)
        
        widget.setLayout(layout)
        return widget
    
    # ==================== PESTAÑA DE ALERTAS ====================
    
    def crear_tab_alertas(self):
        """Pestaña de alertas de stock bajo"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título con contador
        self.lbl_titulo_alertas = QLabel("⚠️ Productos con Stock Bajo (0)")
        self.lbl_titulo_alertas.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #FF6B6B, stop: 1 #FF8E53
            );
            padding: 12px;
            border-radius: 5px;
        """)
        layout.addWidget(self.lbl_titulo_alertas)
        
        # Tabla de alertas
        self.tabla_alertas_model = QStandardItemModel()
        self.tabla_alertas_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Stock Actual", "Stock Mínimo", "Diferencia"
        ])
        
        self.tabla_alertas = QTableView()
        self.tabla_alertas.setModel(self.tabla_alertas_model)
        self.tabla_alertas.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_alertas.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_alertas.setStyleSheet(TABLE_STYLE)
        self.tabla_alertas.verticalHeader().setDefaultSectionSize(35)
        
        header = self.tabla_alertas.horizontalHeader()
        header.setFixedHeight(40)
        
        layout.addWidget(self.tabla_alertas)
        
        # Botón de acción rápida
        btn_pedido = QPushButton("📋 Generar Orden de Compra")
        btn_pedido.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        btn_pedido.setCursor(Qt.PointingHandCursor)
        btn_pedido.setFixedHeight(50)
        layout.addWidget(btn_pedido)
        
        widget.setLayout(layout)
        return widget
    
    # ==================== FUNCIONES AUXILIARES ====================
    
    def crear_label_detalle(self, titulo, valor):
        """Crear label para panel de detalles"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(2)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-weight: bold; color: #666; font-size: 14px;")
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("color: #333; font-size: 16px;")
        lbl_valor.setWordWrap(True)
        lbl_valor.setObjectName("valor")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        frame.setLayout(layout)
        return frame
    
    def actualizar_label_valor(self, frame, valor):
        """Actualizar valor en label de detalle"""
        for widget in frame.findChildren(QLabel):
            if widget.objectName() == "valor":
                widget.setText(valor if valor else "---")
                break
    
    def conectar_senales(self):
        """Conectar señales de controles"""
        self.tabla_productos.doubleClicked.connect(self.editar_producto)
        self.tabla_productos.selectionModel().currentChanged.connect(
            self.actualizar_panel_detalle_producto
        )
        self.txt_buscar.textChanged.connect(self.buscar_productos)
    
    # ==================== OPERACIONES CRUD ====================
    
    def nuevo_producto(self):
        """Preparar formulario para nuevo producto"""
        self.limpiar_formulario_producto()
        self.txt_codigo.setFocus()
    
    def guardar_producto(self):
        """Guardar producto (nuevo o actualización)"""
        if not self.validar_formulario_producto():
            return
        
        if self.modo_edicion:
            self.actualizar_producto()
        else:
            self.agregar_producto()
    
    def agregar_producto(self):
        """Agregar nuevo producto"""
        producto = {
            'id': self.proximo_id,
            'codigo': self.txt_codigo.text().strip(),
            'nombre': self.txt_nombre_prod.text().strip(),
            'categoria': self.cmb_categoria.currentText(),
            'ubicacion': self.txt_ubicacion.text().strip(),
            'proveedor': self.txt_proveedor.text().strip(),
            'precio_compra': self.spin_precio_compra.value(),
            'precio_venta': self.spin_precio_venta.value(),
            'stock_actual': self.spin_stock_actual.value(),
            'stock_min': self.spin_stock_min.value(),
            'descripcion': self.txt_descripcion.text().strip()
        }
        
        self.productos_data.append(producto)
        self.proximo_id += 1
        
        self.actualizar_tabla_productos()
        self.actualizar_alertas()
        self.limpiar_formulario_producto()
        self.mostrar_mensaje("Éxito", "Producto agregado correctamente.", QMessageBox.Information)
    
    def actualizar_producto(self):
        """Actualizar producto existente"""
        if not self.producto_en_edicion:
            return
        
        for i, prod in enumerate(self.productos_data):
            if prod['id'] == self.producto_en_edicion['id']:
                self.productos_data[i].update({
                    'codigo': self.txt_codigo.text().strip(),
                    'nombre': self.txt_nombre_prod.text().strip(),
                    'categoria': self.cmb_categoria.currentText(),
                    'ubicacion': self.txt_ubicacion.text().strip(),
                    'proveedor': self.txt_proveedor.text().strip(),
                    'precio_compra': self.spin_precio_compra.value(),
                    'precio_venta': self.spin_precio_venta.value(),
                    'stock_actual': self.spin_stock_actual.value(),
                    'stock_min': self.spin_stock_min.value(),
                    'descripcion': self.txt_descripcion.text().strip()
                })
                break
        
        self.actualizar_tabla_productos()
        self.actualizar_alertas()
        self.cancelar_edicion()
        self.mostrar_mensaje("Éxito", "Producto actualizado correctamente.", QMessageBox.Information)
    
    def editar_producto(self):
        """Cargar producto para edición"""
        fila = self.tabla_productos.currentIndex().row()
        if fila < 0:
            self.mostrar_mensaje("Advertencia", "Seleccione un producto.", QMessageBox.Warning)
            return
        
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        producto = self.obtener_producto_por_id(producto_id)
        
        if producto:
            self.cargar_datos_formulario_producto(producto)
            self.modo_edicion = True
            self.producto_en_edicion = producto
            self.txt_codigo.setFocus()
    
    def eliminar_producto(self):
        """Eliminar producto"""
        fila = self.tabla_productos.currentIndex().row()
        if fila < 0:
            self.mostrar_mensaje("Advertencia", "Seleccione un producto.", QMessageBox.Warning)
            return
        
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        producto = self.obtener_producto_por_id(producto_id)
        
        if producto:
            respuesta = QMessageBox.question(
                self, "Confirmar",
                f"¿Eliminar producto '{producto['nombre']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                self.productos_data.remove(producto)
                self.actualizar_tabla_productos()
                self.actualizar_alertas()
                self.limpiar_formulario_producto()
    
    def registrar_entrada(self):
        """Registrar entrada de stock"""
        from PyQt5.QtWidgets import QInputDialog
        
        fila = self.tabla_productos.currentIndex().row()
        if fila < 0:
            self.mostrar_mensaje("Advertencia", "Seleccione un producto.", QMessageBox.Warning)
            return
        
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        producto = self.obtener_producto_por_id(producto_id)
        
        if producto:
            cantidad, ok = QInputDialog.getInt(
                self, "Entrada de Stock",
                f"Producto: {producto['nombre']}\nStock actual: {producto['stock_actual']}\n\nCantidad a ingresar:",
                1, 1, 99999
            )
            
            if ok:
                motivo, ok2 = QInputDialog.getText(
                    self, "Motivo",
                    "Motivo de la entrada:"
                )
                
                if ok2:
                    producto['stock_actual'] += cantidad
                    self.registrar_movimiento("Entrada", producto, cantidad, motivo)
                    self.actualizar_tabla_productos()
                    self.actualizar_alertas()
                    self.mostrar_mensaje("Éxito", f"Se agregaron {cantidad} unidades.", QMessageBox.Information)
    
    def registrar_salida(self):
        """Registrar salida de stock"""
        from PyQt5.QtWidgets import QInputDialog
        
        fila = self.tabla_productos.currentIndex().row()
        if fila < 0:
            self.mostrar_mensaje("Advertencia", "Seleccione un producto.", QMessageBox.Warning)
            return
        
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        producto = self.obtener_producto_por_id(producto_id)
        
        if producto:
            if producto['stock_actual'] == 0:
                self.mostrar_mensaje("Error", "No hay stock disponible.", QMessageBox.Critical)
                return
            
            cantidad, ok = QInputDialog.getInt(
                self, "Salida de Stock",
                f"Producto: {producto['nombre']}\nStock actual: {producto['stock_actual']}\n\nCantidad a retirar:",
                1, 1, producto['stock_actual']
            )
            
            if ok:
                motivo, ok2 = QInputDialog.getText(
                    self, "Motivo",
                    "Motivo de la salida:"
                )
                
                if ok2:
                    producto['stock_actual'] -= cantidad
                    self.registrar_movimiento("Salida", producto, cantidad, motivo)
                    self.actualizar_tabla_productos()
                    self.actualizar_alertas()
                    self.mostrar_mensaje("Éxito", f"Se retiraron {cantidad} unidades.", QMessageBox.Information)
    
    def registrar_movimiento(self, tipo, producto, cantidad, motivo):
        """Registrar movimiento en el historial"""
        from datetime import datetime
        
        movimiento = {
            'id': len(self.movimientos_data) + 1,
            'fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'tipo': tipo,
            'producto': producto['nombre'],
            'cantidad': cantidad,
            'usuario': "Admin",  # Aquí puedes usar el usuario actual
            'motivo': motivo
        }
        
        self.movimientos_data.append(movimiento)
        self.actualizar_tabla_movimientos()
    
    # ==================== FUNCIONES DE ACTUALIZACIÓN ====================
    
    def actualizar_tabla_productos(self):
        """Actualizar tabla de productos"""
        self.tabla_productos_model.clear()
        self.tabla_productos_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Stock", "P. Venta", "Estado"
        ])
        
        for producto in self.productos_data:
            # Determinar estado
            if producto['stock_actual'] == 0:
                estado = "SIN STOCK"
                color_estado = QColor(255, 107, 107)
            elif producto['stock_actual'] <= producto['stock_min']:
                estado = "BAJO"
                color_estado = QColor(255, 177, 66)
            else:
                estado = "OK"
                color_estado = QColor(46, 213, 196)
            
            fila = [
                QStandardItem(str(producto['id'])),
                QStandardItem(producto['codigo']),
                QStandardItem(producto['nombre']),
                QStandardItem(producto['categoria']),
                QStandardItem(str(producto['stock_actual'])),
                QStandardItem(f"${producto['precio_venta']:.2f}"),
                QStandardItem(estado)
            ]
            
            # Alineación
            fila[0].setTextAlignment(Qt.AlignCenter)
            fila[1].setTextAlignment(Qt.AlignCenter)
            fila[3].setTextAlignment(Qt.AlignCenter)
            fila[4].setTextAlignment(Qt.AlignCenter)
            fila[5].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fila[6].setTextAlignment(Qt.AlignCenter)
            
            # Color del estado
            fila[6].setBackground(color_estado)
            fila[6].setForeground(QColor(255, 255, 255))
            
            self.tabla_productos_model.appendRow(fila)
    
    def actualizar_tabla_movimientos(self):
        """Actualizar tabla de movimientos"""
        self.tabla_movimientos_model.clear()
        self.tabla_movimientos_model.setHorizontalHeaderLabels([
            "ID", "Fecha", "Tipo", "Producto", "Cantidad", "Usuario", "Motivo"
        ])
        
        for mov in reversed(self.movimientos_data):  # Más recientes primero
            fila = [
                QStandardItem(str(mov['id'])),
                QStandardItem(mov['fecha']),
                QStandardItem(mov['tipo']),
                QStandardItem(mov['producto']),
                QStandardItem(str(mov['cantidad'])),
                QStandardItem(mov['usuario']),
                QStandardItem(mov['motivo'])
            ]
            
            # Alineación
            fila[0].setTextAlignment(Qt.AlignCenter)
            fila[1].setTextAlignment(Qt.AlignCenter)
            fila[2].setTextAlignment(Qt.AlignCenter)
            fila[4].setTextAlignment(Qt.AlignCenter)
            
            # Color según tipo
            if mov['tipo'] == "Entrada":
                fila[2].setBackground(QColor(46, 213, 196))
                fila[2].setForeground(QColor(255, 255, 255))
            else:
                fila[2].setBackground(QColor(255, 107, 107))
                fila[2].setForeground(QColor(255, 255, 255))
            
            self.tabla_movimientos_model.appendRow(fila)
    
    def actualizar_alertas(self):
        """Actualizar tabla de alertas"""
        self.tabla_alertas_model.clear()
        self.tabla_alertas_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Stock Actual", "Stock Mínimo", "Diferencia"
        ])
        
        productos_bajo_stock = [
            p for p in self.productos_data 
            if p['stock_actual'] <= p['stock_min']
        ]
        
        # Actualizar contador en título
        self.lbl_titulo_alertas.setText(
            f"⚠️ Productos con Stock Bajo ({len(productos_bajo_stock)})"
        )
        
        for producto in productos_bajo_stock:
            diferencia = producto['stock_min'] - producto['stock_actual']
            
            fila = [
                QStandardItem(str(producto['id'])),
                QStandardItem(producto['codigo']),
                QStandardItem(producto['nombre']),
                QStandardItem(str(producto['stock_actual'])),
                QStandardItem(str(producto['stock_min'])),
                QStandardItem(str(diferencia))
            ]
            
            # Alineación
            for i in [0, 1, 3, 4, 5]:
                fila[i].setTextAlignment(Qt.AlignCenter)
            
            # Color de fondo según criticidad
            if producto['stock_actual'] == 0:
                color_fondo = QColor(255, 107, 107, 100)
            else:
                color_fondo = QColor(255, 177, 66, 100)
            
            for item in fila:
                item.setBackground(color_fondo)
            
            self.tabla_alertas_model.appendRow(fila)
    
    def actualizar_panel_detalle_producto(self, current, previous):
        """Actualizar panel de detalles"""
        if not current.isValid():
            return
        
        fila = current.row()
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        producto = self.obtener_producto_por_id(producto_id)
        
        if producto:
            self.actualizar_label_valor(self.labels_detalle_prod['id'], str(producto['id']))
            self.actualizar_label_valor(self.labels_detalle_prod['codigo'], producto['codigo'])
            self.actualizar_label_valor(self.labels_detalle_prod['nombre'], producto['nombre'])
            self.actualizar_label_valor(self.labels_detalle_prod['categoria'], producto['categoria'])
            self.actualizar_label_valor(self.labels_detalle_prod['stock'], str(producto['stock_actual']))
            self.actualizar_label_valor(self.labels_detalle_prod['stock_min'], str(producto['stock_min']))
            self.actualizar_label_valor(self.labels_detalle_prod['ubicacion'], producto['ubicacion'])
            self.actualizar_label_valor(self.labels_detalle_prod['proveedor'], producto['proveedor'])
            self.actualizar_label_valor(self.labels_detalle_prod['precio_compra'], f"${producto['precio_compra']:.2f}")
            self.actualizar_label_valor(self.labels_detalle_prod['precio_venta'], f"${producto['precio_venta']:.2f}")
            self.actualizar_label_valor(self.labels_detalle_prod['descripcion'], producto['descripcion'])
    
    def buscar_productos(self, texto):
        """Buscar productos en tiempo real"""
        if not texto:
            self.actualizar_tabla_productos()
            return
        
        texto = texto.lower()
        self.tabla_productos_model.clear()
        self.tabla_productos_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Stock", "P. Venta", "Estado"
        ])
        
        for producto in self.productos_data:
            if (texto in producto['codigo'].lower() or 
                texto in producto['nombre'].lower() or
                texto in producto['categoria'].lower()):
                
                # Determinar estado
                if producto['stock_actual'] == 0:
                    estado = "SIN STOCK"
                    color_estado = QColor(255, 107, 107)
                elif producto['stock_actual'] <= producto['stock_min']:
                    estado = "BAJO"
                    color_estado = QColor(255, 177, 66)
                else:
                    estado = "OK"
                    color_estado = QColor(46, 213, 196)
                
                fila = [
                    QStandardItem(str(producto['id'])),
                    QStandardItem(producto['codigo']),
                    QStandardItem(producto['nombre']),
                    QStandardItem(producto['categoria']),
                    QStandardItem(str(producto['stock_actual'])),
                    QStandardItem(f"${producto['precio_venta']:.2f}"),
                    QStandardItem(estado)
                ]
                
                fila[0].setTextAlignment(Qt.AlignCenter)
                fila[1].setTextAlignment(Qt.AlignCenter)
                fila[3].setTextAlignment(Qt.AlignCenter)
                fila[4].setTextAlignment(Qt.AlignCenter)
                fila[5].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                fila[6].setTextAlignment(Qt.AlignCenter)
                fila[6].setBackground(color_estado)
                fila[6].setForeground(QColor(255, 255, 255))
                
                self.tabla_productos_model.appendRow(fila)
    
    def filtrar_movimientos(self, tipo):
        """Filtrar movimientos por tipo"""
        self.tabla_movimientos_model.clear()
        self.tabla_movimientos_model.setHorizontalHeaderLabels([
            "ID", "Fecha", "Tipo", "Producto", "Cantidad", "Usuario", "Motivo"
        ])
        
        movimientos_filtrados = self.movimientos_data
        if tipo != "Todos":
            movimientos_filtrados = [m for m in self.movimientos_data if m['tipo'] == tipo]
        
        for mov in reversed(movimientos_filtrados):
            fila = [
                QStandardItem(str(mov['id'])),
                QStandardItem(mov['fecha']),
                QStandardItem(mov['tipo']),
                QStandardItem(mov['producto']),
                QStandardItem(str(mov['cantidad'])),
                QStandardItem(mov['usuario']),
                QStandardItem(mov['motivo'])
            ]
            
            fila[0].setTextAlignment(Qt.AlignCenter)
            fila[1].setTextAlignment(Qt.AlignCenter)
            fila[2].setTextAlignment(Qt.AlignCenter)
            fila[4].setTextAlignment(Qt.AlignCenter)
            
            if mov['tipo'] == "Entrada":
                fila[2].setBackground(QColor(46, 213, 196))
                fila[2].setForeground(QColor(255, 255, 255))
            else:
                fila[2].setBackground(QColor(255, 107, 107))
                fila[2].setForeground(QColor(255, 255, 255))
            
            self.tabla_movimientos_model.appendRow(fila)
    
    # ==================== FUNCIONES DE SOPORTE ====================
    
    def obtener_producto_por_id(self, producto_id):
        """Buscar producto por ID"""
        return next((p for p in self.productos_data if p['id'] == producto_id), None)
    
    def cargar_datos_formulario_producto(self, producto):
        """Cargar datos en formulario"""
        self.txt_id_prod.setText(str(producto['id']))
        self.txt_codigo.setText(producto['codigo'])
        self.txt_nombre_prod.setText(producto['nombre'])
        self.cmb_categoria.setCurrentText(producto['categoria'])
        self.txt_ubicacion.setText(producto['ubicacion'])
        self.txt_proveedor.setText(producto['proveedor'])
        self.spin_precio_compra.setValue(producto['precio_compra'])
        self.spin_precio_venta.setValue(producto['precio_venta'])
        self.spin_stock_actual.setValue(producto['stock_actual'])
        self.spin_stock_min.setValue(producto['stock_min'])
        self.txt_descripcion.setText(producto['descripcion'])
    
    def validar_formulario_producto(self):
        """Validar formulario"""
        if not self.txt_codigo.text().strip():
            self.mostrar_mensaje("Error", "El código es obligatorio.", QMessageBox.Critical)
            self.txt_codigo.setFocus()
            return False
        
        if not self.txt_nombre_prod.text().strip():
            self.mostrar_mensaje("Error", "El nombre es obligatorio.", QMessageBox.Critical)
            self.txt_nombre_prod.setFocus()
            return False
        
        # Verificar código duplicado (solo al agregar)
        if not self.modo_edicion:
            if any(p['codigo'] == self.txt_codigo.text().strip() for p in self.productos_data):
                self.mostrar_mensaje("Error", "El código ya existe.", QMessageBox.Critical)
                self.txt_codigo.setFocus()
                return False
        
        return True
    
    def limpiar_formulario_producto(self):
        """Limpiar formulario"""
        self.txt_id_prod.clear()
        self.txt_codigo.clear()
        self.txt_nombre_prod.clear()
        self.cmb_categoria.setCurrentIndex(0)
        self.txt_ubicacion.clear()
        self.txt_proveedor.clear()
        self.spin_precio_compra.setValue(0)
        self.spin_precio_venta.setValue(0)
        self.spin_stock_actual.setValue(0)
        self.spin_stock_min.setValue(0)
        self.txt_descripcion.clear()
        self.cancelar_edicion()
    
    def cancelar_edicion(self):
        """Cancelar edición"""
        self.modo_edicion = False
        self.producto_en_edicion = None
    
    def mostrar_mensaje(self, titulo, mensaje, tipo):
        """Mostrar mensaje"""
        msg_box = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()
    
    def cargar_datos_ejemplo(self):
        """Cargar datos de ejemplo"""
        ejemplos = [
            {
                'id': 1, 'codigo': 'REF-001', 'nombre': 'Filtro de Aceite',
                'categoria': 'Refacciones', 'ubicacion': 'Estante A1',
                'proveedor': 'Autopartes SA', 'precio_compra': 45.00, 'precio_venta': 75.00,
                'stock_actual': 15, 'stock_min': 10, 'descripcion': 'Filtro de aceite universal'
            },
            {
                'id': 2, 'codigo': 'HER-001', 'nombre': 'Llave Inglesa 12"',
                'categoria': 'Herramientas', 'ubicacion': 'Caja B3',
                'proveedor': 'Ferretería Total', 'precio_compra': 120.00, 'precio_venta': 180.00,
                'stock_actual': 3, 'stock_min': 5, 'descripcion': 'Llave ajustable 12 pulgadas'
            },
            {
                'id': 3, 'codigo': 'CON-001', 'nombre': 'Aceite Motor 10W-40',
                'categoria': 'Consumibles', 'ubicacion': 'Bodega C1',
                'proveedor': 'Lubricantes MX', 'precio_compra': 85.00, 'precio_venta': 135.00,
                'stock_actual': 0, 'stock_min': 20, 'descripcion': 'Aceite sintético 1 litro'
            },
            {
                'id': 4, 'codigo': 'REF-002', 'nombre': 'Pastillas de Freno',
                'categoria': 'Refacciones', 'ubicacion': 'Estante A2',
                'proveedor': 'Autopartes SA', 'precio_compra': 250.00, 'precio_venta': 400.00,
                'stock_actual': 8, 'stock_min': 6, 'descripcion': 'Pastillas delanteras universales'
            },
            {
                'id': 5, 'codigo': 'ACC-001', 'nombre': 'Tapete Automotriz',
                'categoria': 'Accesorios', 'ubicacion': 'Estante D1',
                'proveedor': 'Accesorios Pro', 'precio_compra': 150.00, 'precio_venta': 280.00,
                'stock_actual': 12, 'stock_min': 8, 'descripcion': 'Tapete universal de hule'
            }
        ]
        
        self.productos_data.extend(ejemplos)
        self.proximo_id = 6
        
        # Crear movimientos de ejemplo
        from datetime import datetime, timedelta
        
        movimientos_ejemplo = [
            {
                'id': 1,
                'fecha': (datetime.now() - timedelta(days=5)).strftime("%d/%m/%Y %H:%M"),
                'tipo': 'Entrada',
                'producto': 'Filtro de Aceite',
                'cantidad': 20,
                'usuario': 'Admin',
                'motivo': 'Compra a proveedor'
            },
            {
                'id': 2,
                'fecha': (datetime.now() - timedelta(days=3)).strftime("%d/%m/%Y %H:%M"),
                'tipo': 'Salida',
                'producto': 'Filtro de Aceite',
                'cantidad': 5,
                'usuario': 'Admin',
                'motivo': 'Orden de trabajo #123'
            },
            {
                'id': 3,
                'fecha': (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y %H:%M"),
                'tipo': 'Salida',
                'producto': 'Aceite Motor 10W-40',
                'cantidad': 15,
                'usuario': 'Admin',
                'motivo': 'Servicio múltiple'
            }
        ]
        
        self.movimientos_data.extend(movimientos_ejemplo)
        
        # Actualizar todas las vistas
        self.actualizar_tabla_productos()
        self.actualizar_tabla_movimientos()
        self.actualizar_alertas()
    
    def showEvent(self, event):
        """Ajustar columnas al mostrar"""
        super().showEvent(event)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(50, self.ajustar_columnas)
    
    def ajustar_columnas(self):
        """Ajustar anchos de columnas"""
        # Tabla de productos
        header = self.tabla_productos.horizontalHeader()
        ancho = self.tabla_productos.viewport().width()
        header.resizeSection(0, int(ancho * 0.05))  # ID
        header.resizeSection(1, int(ancho * 0.12))  # Código
        header.resizeSection(2, int(ancho * 0.30))  # Nombre
        header.resizeSection(3, int(ancho * 0.15))  # Categoría
        header.resizeSection(4, int(ancho * 0.10))  # Stock
        header.resizeSection(5, int(ancho * 0.13))  # Precio
        header.resizeSection(6, int(ancho * 0.15))  # Estado
    
    def closeEvent(self, event):
        """Evento al cerrar"""
        event.accept()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = InventarioWindow()
    window.show()
    sys.exit(app.exec_())
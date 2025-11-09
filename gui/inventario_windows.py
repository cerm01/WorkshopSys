from datetime import datetime
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QGridLayout, QGroupBox, QMessageBox, QTableView, 
    QHeaderView, QFrame, QWidget, QComboBox, QSpinBox, 
    QDoubleSpinBox, QTabWidget, QTextEdit, QScrollArea, QInputDialog,
    QCompleter
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor

from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE,
    LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, MESSAGE_BOX_STYLE
)

try:
    from gui.api_client import api_client as db_helper
    from gui.websocket_client import ws_client
except ImportError:
    print("Error: No se pudo importar 'api_client' o 'ws_client'.")
    db_helper = None
    ws_client = None


class InventarioWindow(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Gestión de Inventario")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        
        self.setMinimumSize(1400, 800)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)
        
        self.producto_en_edicion_id = None
        self.modo_edicion = False
        self.proveedores_dict = {}
        self._datos_cargados = False
        
        self.setup_ui()
        self.conectar_senales()

        if ws_client:
            ws_client.producto_creado.connect(self.on_notificacion_producto)
            ws_client.producto_actualizado.connect(self.on_notificacion_producto)
            ws_client.stock_actualizado.connect(self.on_notificacion_producto)
            ws_client.proveedor_creado.connect(self.on_notificacion_proveedor)
            ws_client.proveedor_actualizado.connect(self.on_notificacion_proveedor)
        
        QTimer.singleShot(100, self._cargar_datos_inicial)
    
    def _cargar_datos_inicial(self):
        if not self._datos_cargados:
            self.cargar_proveedores_bd()
            self.cargar_productos_desde_bd()
            self._datos_cargados = True

    def on_notificacion_producto(self, data):
        self.cargar_productos_desde_bd()

    def on_notificacion_proveedor(self, data):
        self.cargar_proveedores_bd()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
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
        
        self.tab_productos = self.crear_tab_productos()
        self.tabs.addTab(self.tab_productos, "📦 Productos")
        
        self.tab_movimientos = self.crear_tab_movimientos()
        self.tabs.addTab(self.tab_movimientos, "📊 Movimientos")
        
        self.tab_alertas = self.crear_tab_alertas()
        self.tabs.addTab(self.tab_alertas, "⚠️ Alertas de Stock")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
    
    def crear_tab_productos(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.crear_formulario_producto(layout)
        
        contenedor = QHBoxLayout()
        self.crear_tabla_productos(contenedor)
        self.crear_panel_detalle_producto(contenedor)
        layout.addLayout(contenedor, 1)
        
        self.crear_botones_productos(layout)
        
        widget.setLayout(layout)
        return widget
    
    def crear_formulario_producto(self, parent_layout):
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
        
        input_style_inventario = INPUT_STYLE + """
            QSpinBox {
                padding: 8px;
                border: 2px solid #F5F5F5;
                border-radius: 6px;
                background-color: #F5F5F5;
                min-height: 25px;
                font-size: 16px;
                margin-top: 0px;
            }
            
            QSpinBox:focus {
                border: 2px solid #2CD5C4;
                background-color: white;
            }
            
            QSpinBox {
                padding-right: 15px;
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                height: 0px;
            }
        """
        
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
        
        row = 1
        labels_campos = [
            ("Proveedor:", "txt_proveedor", "Escriba para buscar proveedor..."),
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
                campo.setStyleSheet(input_style_inventario)
            else:
                campo = QLineEdit()
                campo.setStyleSheet(INPUT_STYLE)
                campo.setPlaceholderText(placeholder)
            
            setattr(self, attr, campo)
            grid.addWidget(campo, row, col_campo)
        
        row = 2
        
        lbl = QLabel("Stock:")
        lbl.setStyleSheet(label_style)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl, row, 0)
        
        self.spin_stock_actual = QSpinBox()
        self.spin_stock_actual.setRange(0, 99999)
        self.spin_stock_actual.setStyleSheet(input_style_inventario)
        self.spin_stock_actual.setReadOnly(True) # No editable por defecto
        grid.addWidget(self.spin_stock_actual, row, 1)
        
        lbl = QLabel("Descripción:")
        lbl.setStyleSheet(label_style)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl, row, 2)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(INPUT_STYLE)
        self.txt_descripcion.setPlaceholderText("Descripción breve del producto")
        grid.addWidget(self.txt_descripcion, row, 3, 1, 3)
        
        lbl = QLabel("ID:")
        lbl.setStyleSheet(label_style)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        grid.addWidget(lbl, row, 6)
        
        self.txt_id_prod = QLineEdit()
        self.txt_id_prod.setReadOnly(True)
        self.txt_id_prod.setStyleSheet(INPUT_STYLE + "background-color: #E8E8E8; color: #666;")
        self.txt_id_prod.setPlaceholderText("Auto")
        grid.addWidget(self.txt_id_prod, row, 7)
        
        grupo.setLayout(grid)
        parent_layout.addWidget(grupo)
    
    def crear_tabla_productos(self, parent_layout):
            widget = QWidget()
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            
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
            
            self.txt_buscar = QLineEdit()
            self.txt_buscar.setStyleSheet(INPUT_STYLE)
            self.txt_buscar.setPlaceholderText("🔍 Buscar producto...")
            self.txt_buscar.setMaximumWidth(300)
            header_layout.addWidget(self.txt_buscar)
            
            layout.addLayout(header_layout)
            
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
            header.setStretchLastSection(True)
            
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
            
            layout.addWidget(self.tabla_productos)
            widget.setLayout(layout)
            parent_layout.addWidget(widget, 7)
    
    def crear_panel_detalle_producto(self, parent_layout):
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
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        detalle_widget = QWidget()
        detalle_layout = QVBoxLayout()
        
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
    
    def crear_tab_movimientos(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
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
        
        filtros_layout = QHBoxLayout()
        
        lbl_filtro = QLabel("Filtrar por:")
        lbl_filtro.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        filtros_layout.addWidget(lbl_filtro)
        
        self.cmb_filtro_tipo = QComboBox()
        self.cmb_filtro_tipo.setStyleSheet(INPUT_STYLE)
        self.cmb_filtro_tipo.addItems(["Todos", "Entrada", "Salida"])
        self.cmb_filtro_tipo.currentTextChanged.connect(self.filtrar_movimientos)
        filtros_layout.addWidget(self.cmb_filtro_tipo)
        
        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)
        
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
    
    def crear_tab_alertas(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
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
        
        btn_pedido = QPushButton("📋 Generar Orden de Compra")
        btn_pedido.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        btn_pedido.setCursor(Qt.PointingHandCursor)
        btn_pedido.setFixedHeight(50)
        layout.addWidget(btn_pedido)
        
        widget.setLayout(layout)
        return widget
    
    def _crear_item(self, texto, alineacion):
        item = QStandardItem(str(texto))
        item.setTextAlignment(alineacion)
        return item

    def crear_label_detalle(self, titulo, valor):
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
        for widget in frame.findChildren(QLabel):
            if widget.objectName() == "valor":
                widget.setText(str(valor) if valor else "---") 
                break
    
    def _limpiar_panel_detalle_producto(self):
        if not hasattr(self, 'labels_detalle_prod'):
            return
        
        for key, frame in self.labels_detalle_prod.items():
            self.actualizar_label_valor(frame, "---")
    
    def conectar_senales(self):
        self.tabla_productos.doubleClicked.connect(self.editar_producto)
        self.tabla_productos.selectionModel().currentChanged.connect(
            self.actualizar_panel_detalle_producto
        )
        self.txt_buscar.textChanged.connect(self.buscar_productos)
    
    def cargar_productos_desde_bd(self):
        try:
            self.actualizar_tabla_productos()
            self.actualizar_alertas()
            self.actualizar_tabla_movimientos()
        except Exception as e:
            self.mostrar_error(f"Error al cargar productos: {e}")
    
    def nuevo_producto(self):
        self.limpiar_formulario_producto()
        self.spin_stock_actual.setReadOnly(False)
        self.txt_codigo.setFocus()
    
    def guardar_producto(self):
        if not self.validar_formulario_producto():
            return
        
        if self.modo_edicion:
            self.actualizar_producto_bd()
        else:
            self.agregar_producto_bd()
    
    def agregar_producto_bd(self):
        datos = {
            'codigo': self.txt_codigo.text().strip(),
            'nombre': self.txt_nombre_prod.text().strip(),
            'categoria': self.cmb_categoria.currentText(),
            'ubicacion': self.txt_ubicacion.text().strip(),
            'precio_compra': self.spin_precio_compra.value(),
            'precio_venta': self.spin_precio_venta.value(),
            'stock_actual': self.spin_stock_actual.value(),
            'stock_min': self.spin_stock_min.value(),
            'descripcion': self.txt_descripcion.text().strip()
        }
        
        proveedor_nombre = self.txt_proveedor.text().strip()
        if proveedor_nombre:
            proveedor_id = self.proveedores_dict.get(proveedor_nombre, None)
            
            if proveedor_id:
                datos['proveedor_id'] = proveedor_id
            else:
                self.mostrar_advertencia(f"Proveedor '{proveedor_nombre}' no es válido. Seleccione uno de la lista.")
                datos['proveedor_id'] = None
        else:
            datos['proveedor_id'] = None
        
        producto = db_helper.crear_producto(datos)
        
        if producto:
            self.cargar_productos_desde_bd()
            self.limpiar_formulario_producto()
            self.spin_stock_actual.setReadOnly(True)
            self.mostrar_exito("Producto agregado correctamente.")
        else:
            self.mostrar_error("No se pudo agregar el producto.")
    
    def actualizar_producto_bd(self):
        if not self.producto_en_edicion_id:
            return
        
        datos = {
            'codigo': self.txt_codigo.text().strip(),
            'nombre': self.txt_nombre_prod.text().strip(),
            'categoria': self.cmb_categoria.currentText(),
            'ubicacion': self.txt_ubicacion.text().strip(),
            'precio_compra': self.spin_precio_compra.value(),
            'precio_venta': self.spin_precio_venta.value(),
            'stock_min': self.spin_stock_min.value(),
            'descripcion': self.txt_descripcion.text().strip()
        }
        
        proveedor_nombre = self.txt_proveedor.text().strip()
        if proveedor_nombre:
            proveedor_id = self.proveedores_dict.get(proveedor_nombre, None)
            
            if proveedor_id:
                datos['proveedor_id'] = proveedor_id
            else:
                self.mostrar_advertencia(f"Proveedor '{proveedor_nombre}' no es válido. Seleccione uno de la lista.")
                datos['proveedor_id'] = None
        else:
            datos['proveedor_id'] = None
        
        producto = db_helper.actualizar_producto(self.producto_en_edicion_id, datos)
        
        if producto:
            self.cargar_productos_desde_bd() 
            self.limpiar_formulario_producto()
            self.spin_stock_actual.setReadOnly(True)
            self.mostrar_exito("Producto actualizado correctamente.")
        else:
            self.mostrar_error("No se pudo actualizar el producto.")
    
    def editar_producto(self):
        fila = self.tabla_productos.currentIndex().row()
        if fila < 0:
            self.mostrar_advertencia("Seleccione un producto.")
            return
        
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        productos = db_helper.get_productos()
        producto = next((p for p in productos if p['id'] == producto_id), None)
        
        if producto:
            self.cargar_datos_formulario_producto(producto)
            self.spin_stock_actual.setReadOnly(True)
            self.modo_edicion = True
            self.producto_en_edicion_id = producto_id
            self.txt_codigo.setFocus()
    
    def eliminar_producto(self):
        fila = self.tabla_productos.currentIndex().row()
        if fila < 0:
            self.mostrar_advertencia("Seleccione un producto.")
            return
        
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        productos = db_helper.get_productos()
        producto = next((p for p in productos if p['id'] == producto_id), None)
        nombre_producto = producto['nombre'] if producto else f"ID {producto_id}"
        
        if producto:
            respuesta = QMessageBox.question(
                self, "Confirmar",
                f"¿Eliminar producto '{nombre_producto}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.Yes:
                if db_helper.eliminar_producto(producto_id):
                    self.cargar_productos_desde_bd()
                    self.limpiar_formulario_producto()
                    self.mostrar_exito("Producto eliminado.")
                else:
                    self.mostrar_error("No se pudo eliminar el producto.")
    
    def registrar_entrada(self):
        fila = self.tabla_productos.currentIndex().row()
        if fila < 0:
            self.mostrar_advertencia("Seleccione un producto.")
            return
        
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        
        productos = db_helper.get_productos()
        producto = next((p for p in productos if p['id'] == producto_id), None)
        
        if producto:
            cantidad, ok = QInputDialog.getInt(
                self, "Entrada de Stock",
                f"Producto: {producto.get('nombre')}\nStock actual: {producto.get('stock_actual')}\n\nCantidad a ingresar:",
                1, 1, 99999
            )
            
            if ok:
                motivo, ok2 = QInputDialog.getText(
                    self, "Motivo",
                    "Motivo de la entrada:"
                )
                
                if ok2:
                    if db_helper.registrar_movimiento_inventario(producto_id, "Entrada", cantidad, motivo, "Admin"):
                        self.cargar_productos_desde_bd() 
                        self.mostrar_exito(f"Se agregaron {cantidad} unidades.")
                    else:
                        self.mostrar_error("No se pudo registrar la entrada.")

    def registrar_salida(self):
        fila = self.tabla_productos.currentIndex().row()
        if fila < 0:
            self.mostrar_advertencia("Seleccione un producto.")
            return
        
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())
        
        productos = db_helper.get_productos()
        producto = next((p for p in productos if p['id'] == producto_id), None)
        
        if producto:
            stock_actual = producto.get('stock_actual', 0)
            if stock_actual == 0:
                self.mostrar_error("No hay stock disponible.")
                return
            
            cantidad, ok = QInputDialog.getInt(
                self, "Salida de Stock",
                f"Producto: {producto.get('nombre')}\nStock actual: {stock_actual}\n\nCantidad a retirar:",
                1, 1, stock_actual
            )
            
            if ok:
                motivo, ok2 = QInputDialog.getText(
                    self, "Motivo",
                    "Motivo de la salida:"
                )
                
                if ok2:
                    if db_helper.registrar_movimiento_inventario(producto_id, "Salida", cantidad, motivo, "Admin"):
                        self.cargar_productos_desde_bd() 
                        self.mostrar_exito(f"Se retiraron {cantidad} unidades.")
                    else:
                        self.mostrar_error("No se pudo registrar la salida.")
    
    def cargar_proveedores_bd(self):
        try:
            proveedores = db_helper.get_proveedores()
            self.proveedores_dict.clear()
            
            nombres_proveedores = []
            for prov in proveedores:
                nombre = prov.get('nombre', 'Sin Nombre')
                tipo = prov.get('tipo', 'Sin Tipo')
                nombre_completo = f"{nombre} - {tipo}"
                nombres_proveedores.append(nombre_completo)
                self.proveedores_dict[nombre_completo] = prov.get('id')
            
            completer = QCompleter(nombres_proveedores)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.setMaxVisibleItems(9)
            completer.popup().setStyleSheet("""
                QListView {
                    background-color: white;
                    border: 2px solid #2CD5C4;
                    border-radius: 4px;
                    padding: 5px;
                    font-size: 16px;
                    min-height: 60px;
                }
                QListView::item {
                    padding: 10px;
                    border-radius: 3px;
                    min-height: 30px;
                }
                QListView::item:hover {
                    background-color: #E0F7FA;
                }
                QListView::item:selected {
                    background-color: #2CD5C4;
                    color: white;
                }
            """)
            
            self.txt_proveedor.setCompleter(completer)
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar proveedores: {e}")
    
    def actualizar_tabla_productos(self, productos=None):
        if productos is None:
            try:
                productos = db_helper.get_productos()
            except Exception as e:
                self.mostrar_error(f"No se pudo leer productos: {e}")
                return

        self.tabla_productos_model.clear()
        self.tabla_productos_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Stock", "P. Venta", "Estado"
        ])
        
        for producto in productos:
            stock_actual = producto.get('stock_actual', 0)
            stock_min = producto.get('stock_min', 0)
            
            if stock_actual == 0:
                estado = "SIN STOCK"
                color_estado = QColor(255, 107, 107)
            elif stock_actual <= stock_min:
                estado = "BAJO"
                color_estado = QColor(255, 177, 66)
            else:
                estado = "OK"
                color_estado = QColor(46, 213, 196)
            
            fila = [
                self._crear_item(producto.get('id', 'N/A'), Qt.AlignCenter),
                self._crear_item(producto.get('codigo', 'N/A'), Qt.AlignCenter),
                self._crear_item(producto.get('nombre', 'N/A'), Qt.AlignLeft | Qt.AlignVCenter),
                self._crear_item(producto.get('categoria', 'N/A'), Qt.AlignCenter),
                self._crear_item(stock_actual, Qt.AlignCenter),
                self._crear_item(f"${producto.get('precio_venta', 0):.2f}", Qt.AlignRight | Qt.AlignVCenter),
                self._crear_item(estado, Qt.AlignCenter)
            ]
            
            fila[6].setBackground(color_estado)
            fila[6].setForeground(QColor(255, 255, 255))
            
            self.tabla_productos_model.appendRow(fila)
    
    def actualizar_tabla_movimientos(self):
        try:
            # CAMBIO 1: Usar el nombre correcto de la función
            if hasattr(db_helper, 'get_movimientos_inventario'):
                # CAMBIO 2: Usar el nombre correcto de la función
                movimientos = db_helper.get_movimientos_inventario()
            else:
                # CAMBIO 3: Actualizar el mensaje de advertencia
                print("ADVERTENCIA: 'db_helper.get_movimientos_inventario()' no existe. Mostrando tabla vacía.")
                movimientos = []
        except Exception as e:
            self.mostrar_error(f"No se pudo leer movimientos: {e}")
            return

        self.tabla_movimientos_model.clear()
        self.tabla_movimientos_model.setHorizontalHeaderLabels([
            "ID", "Fecha", "Tipo", "Producto", "Cantidad", "Usuario", "Motivo"
        ])
        
        for mov in reversed(movimientos):
            
            fecha_str = mov.get('fecha', 'N/A')
            if fecha_str != 'N/A' and fecha_str:
                try:
                    fecha_dt = datetime.fromisoformat(fecha_str)
                    fecha_str = fecha_dt.strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    pass 
            
            fila = [
                self._crear_item(mov.get('id', 'N/A'), Qt.AlignCenter),
                self._crear_item(fecha_str, Qt.AlignCenter), # <-- LÍNEA NUEVA
                self._crear_item(mov.get('tipo', 'N/A'), Qt.AlignCenter),
                self._crear_item(mov.get('producto', 'N/A'), Qt.AlignLeft | Qt.AlignVCenter),
                self._crear_item(mov.get('cantidad', 0), Qt.AlignCenter),
                self._crear_item(mov.get('usuario', 'N/A'), Qt.AlignCenter),
                self._crear_item(mov.get('motivo', ''), Qt.AlignLeft | Qt.AlignVCenter)
            ]
            
            tipo = mov.get('tipo')
            if tipo == "Entrada":
                fila[2].setBackground(QColor(46, 213, 196))
                fila[2].setForeground(QColor(255, 255, 255))
            else:
                fila[2].setBackground(QColor(255, 107, 107))
                fila[2].setForeground(QColor(255, 255, 255))
            
            self.tabla_movimientos_model.appendRow(fila)
    
    def actualizar_alertas(self):
        try:
            productos_bajo_stock = db_helper.get_productos_bajo_stock()
        except Exception as e:
            self.mostrar_error(f"No se pudo leer alertas: {e}")
            return
        
        self.tabla_alertas_model.clear()
        self.tabla_alertas_model.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Stock Actual", "Stock Mínimo", "Diferencia"
        ])
        
        self.lbl_titulo_alertas.setText(
            f"⚠️ Productos con Stock Bajo ({len(productos_bajo_stock)})"
        )
        
        for producto in productos_bajo_stock:
            stock_actual = producto.get('stock_actual', 0)
            stock_min = producto.get('stock_min', 0)
            diferencia = stock_min - stock_actual
            
            fila = [
                self._crear_item(producto.get('id', 'N/A'), Qt.AlignCenter),
                self._crear_item(producto.get('codigo', 'N/A'), Qt.AlignCenter),
                self._crear_item(producto.get('nombre', 'N/A'), Qt.AlignLeft | Qt.AlignVCenter),
                self._crear_item(stock_actual, Qt.AlignCenter),
                self._crear_item(stock_min, Qt.AlignCenter),
                self._crear_item(diferencia, Qt.AlignCenter)
            ]
            
            if stock_actual == 0:
                color_fondo = QColor(255, 107, 107, 100)
            else:
                color_fondo = QColor(255, 177, 66, 100)
            
            for item in fila:
                item.setBackground(color_fondo)
            
            self.tabla_alertas_model.appendRow(fila)
    
    def actualizar_panel_detalle_producto(self, current, previous):
        if not current.isValid():
            return
        
        fila = current.row()
        producto_id = int(self.tabla_productos_model.item(fila, 0).text())

        try:
            productos = db_helper.get_productos()
            producto = next((p for p in productos if p['id'] == producto_id), None)
        except Exception as e:
            print(f"Error al leer producto para panel: {e}")
            return
        
        if producto:
            self.actualizar_label_valor(self.labels_detalle_prod['id'], producto.get('id'))
            self.actualizar_label_valor(self.labels_detalle_prod['codigo'], producto.get('codigo'))
            self.actualizar_label_valor(self.labels_detalle_prod['nombre'], producto.get('nombre'))
            self.actualizar_label_valor(self.labels_detalle_prod['categoria'], producto.get('categoria'))
            self.actualizar_label_valor(self.labels_detalle_prod['stock'], producto.get('stock_actual'))
            self.actualizar_label_valor(self.labels_detalle_prod['stock_min'], producto.get('stock_min'))
            self.actualizar_label_valor(self.labels_detalle_prod['ubicacion'], producto.get('ubicacion'))
            
            proveedor_id_producto = producto.get('proveedor_id')
            proveedor_nombre_panel = "---"
            if proveedor_id_producto is not None:
                for nombre, id_prov in self.proveedores_dict.items():
                    if id_prov == proveedor_id_producto:
                        proveedor_nombre_panel = nombre
                        break
            self.actualizar_label_valor(self.labels_detalle_prod['proveedor'], proveedor_nombre_panel)
            self.actualizar_label_valor(self.labels_detalle_prod['precio_compra'], f"${producto.get('precio_compra', 0):.2f}")
            self.actualizar_label_valor(self.labels_detalle_prod['precio_venta'], f"${producto.get('precio_venta', 0):.2f}")
            self.actualizar_label_valor(self.labels_detalle_prod['descripcion'], producto.get('descripcion'))
    
    def buscar_productos(self, texto):
        if not texto:
            self.actualizar_tabla_productos()
            return
        
        try:
            productos = db_helper.buscar_productos(texto)
            self.actualizar_tabla_productos(productos) 
        except Exception as e:
            print(f"Error al buscar: {e}")
    
    def filtrar_movimientos(self, tipo):
        try:
            if hasattr(db_helper, 'get_movimientos_inventario'):
                todos_mov = db_helper.get_movimientos_inventario()
            else:
                print("ADVERTENCIA: 'db_helper.get_movimientos_inventario()' no existe. Mostrando tabla vacía.")
                todos_mov = []

            if tipo == "Todos":
                movimientos = todos_mov
            else:
                movimientos = [m for m in todos_mov if m.get('tipo') == tipo]
        except Exception as e:
            self.mostrar_error(f"No se pudo filtrar movimientos: {e}")
            return
        
        self.tabla_movimientos_model.clear()
        self.tabla_movimientos_model.setHorizontalHeaderLabels([
            "ID", "Fecha", "Tipo", "Producto", "Cantidad", "Usuario", "Motivo"
        ])
        
        for mov in reversed(movimientos):

            fecha_str = mov.get('fecha', 'N/A')
            if fecha_str != 'N/A' and fecha_str:
                try:
                    fecha_dt = datetime.fromisoformat(fecha_str)
                    fecha_str = fecha_dt.strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    pass
            
            fila = [
                self._crear_item(mov.get('id', 'N/A'), Qt.AlignCenter),
                self._crear_item(fecha_str, Qt.AlignCenter), # <-- LÍNEA NUEVA
                self._crear_item(mov.get('tipo', 'N/A'), Qt.AlignCenter),
                self._crear_item(mov.get('producto', 'N/A'), Qt.AlignLeft | Qt.AlignVCenter),
                self._crear_item(mov.get('cantidad', 0), Qt.AlignCenter),
                self._crear_item(mov.get('usuario', 'N/A'), Qt.AlignCenter),
                self._crear_item(mov.get('motivo', ''), Qt.AlignLeft | Qt.AlignVCenter)
            ]
            
            tipo = mov.get('tipo')
            if tipo == "Entrada":
                fila[2].setBackground(QColor(46, 213, 196))
                fila[2].setForeground(QColor(255, 255, 255))
            else:
                fila[2].setBackground(QColor(255, 107, 107))
                fila[2].setForeground(QColor(255, 255, 255))
            
            self.tabla_movimientos_model.appendRow(fila)
    
    def cargar_datos_formulario_producto(self, producto):
        self.txt_id_prod.setText(str(producto.get('id', '')))
        self.txt_codigo.setText(producto.get('codigo', ''))
        self.txt_nombre_prod.setText(producto.get('nombre', ''))
        self.cmb_categoria.setCurrentText(producto.get('categoria', 'Otros'))
        self.txt_ubicacion.setText(producto.get('ubicacion', ''))

        self.txt_proveedor.clear()
        proveedor_id_producto = producto.get('proveedor_id')
        
        if proveedor_id_producto is not None:
            for nombre, id_prov in self.proveedores_dict.items():
                if id_prov == proveedor_id_producto:
                    self.txt_proveedor.setText(nombre)
                    break
        
        self.spin_precio_compra.setValue(producto.get('precio_compra', 0))
        self.spin_precio_venta.setValue(producto.get('precio_venta', 0))
        self.spin_stock_actual.setValue(producto.get('stock_actual', 0))
        self.spin_stock_min.setValue(producto.get('stock_min', 0))
        self.txt_descripcion.setText(producto.get('descripcion', ''))
    
    def validar_formulario_producto(self):
        if not self.txt_codigo.text().strip():
            self.mostrar_error("El código es obligatorio.")
            self.txt_codigo.setFocus()
            return False
        
        if not self.txt_nombre_prod.text().strip():
            self.mostrar_error("El nombre es obligatorio.")
            self.txt_nombre_prod.setFocus()
            return False
        
        if not self.modo_edicion:
            try:
                productos = db_helper.get_productos()
                if any(p.get('codigo') == self.txt_codigo.text().strip() for p in productos):
                    self.mostrar_error("El código ya existe.")
                    self.txt_codigo.setFocus()
                    return False
            except Exception as e:
                self.mostrar_error(f"No se pudo validar código: {e}")
                return False
        
        return True
    
    def limpiar_formulario_producto(self):
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
        self.spin_stock_actual.setReadOnly(False)
        self._limpiar_panel_detalle_producto()        
        self.cancelar_edicion()
    
    def cancelar_edicion(self):
        self.modo_edicion = False
        self.producto_en_edicion_id = None
    
    def _mostrar_mensaje(self, icono, titulo, mensaje):
        msg_box = QMessageBox(icono, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()

    def mostrar_advertencia(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Warning, "Advertencia", mensaje)
    
    def mostrar_error(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Critical, "Error", mensaje)
    
    def mostrar_exito(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Information, "Éxito", mensaje)
        
    def mostrar_info(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Information, "Información", mensaje)
    
    def showEvent(self, event):
        super().showEvent(event)
        if not self._datos_cargados:
            self.cargar_proveedores_bd()
            self.cargar_productos_desde_bd()
            self._datos_cargados = True
    
    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    if not db_helper:
        QMessageBox.critical(None, "Error Crítico", "No se pudo importar 'api_client'. La aplicación no puede iniciar.")
    else:
        window = InventarioWindow()
        window.show()
        sys.exit(app.exec_())
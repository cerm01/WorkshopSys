import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QApplication,
    QLabel, QLineEdit, QGridLayout, QGroupBox, QDoubleSpinBox, QMessageBox,
    QTableView, QHeaderView, QMenu, QAction, QFrame, QWidget, QDateEdit, 
    QCompleter, QInputDialog
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem, QColor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.api_client import api_client as db_helper
from gui.websocket_client import ws_client
from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE, LABEL_STYLE,
    INPUT_STYLE, TABLE_STYLE, FORM_BUTTON_STYLE, MESSAGE_BOX_STYLE
)
from dialogs.buscar_notas_dialog import BuscarNotasDialog

try:
    from dialogs.buscar_ordenes_borrador_dialog import BuscarOrdenesBorradorDialog
except ImportError:
    BuscarOrdenesBorradorDialog = None

try:
    from gui.pagos_nota_dialog import PagosNotaDialog
except ImportError:
    PagosNotaDialog = None

class NotasWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Notas")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        # Variables de estado
        self.fila_en_edicion = -1
        self.iva_por_fila = {}
        self.tipo_por_fila = {}
        self.clientes_dict = {}
        self.nota_actual_id = None
        self.modo_edicion = False
        self._datos_cargados = False  # Flag para evitar recargas

        self.setup_ui()
        self.conectar_senales()
        
        # Cargar datos de forma asíncrona después de mostrar la UI
        QTimer.singleShot(100, self._cargar_datos_inicial)
        
        # WebSocket al final
        if ws_client:
            ws_client.cliente_creado.connect(self.on_notificacion_cliente)
            ws_client.cliente_actualizado.connect(self.on_notificacion_cliente)
            ws_client.nota_creada.connect(self.on_notificacion_nota)
    
    def _cargar_datos_inicial(self):
        """Carga datos después de mostrar la ventana"""
        if not self._datos_cargados:
            self.cargar_clientes_bd()
            self._datos_cargados = True

    def on_notificacion_cliente(self, data):
        self.cargar_clientes_bd()

    def on_notificacion_nota(self, data):
        if self.nota_actual_id and data.get('id') == self.nota_actual_id:
            try:
                nota_actualizada = db_helper.get_nota(self.nota_actual_id)
                if nota_actualizada:
                    self.cargar_nota_en_formulario(nota_actualizada)
            except Exception as e:
                print(f"Error recargando nota: {e}")
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.crear_grupo_cliente(main_layout)
        self.crear_grupo_producto_servicio(main_layout)
        self.crear_tabla_items(main_layout)
        self.crear_panel_totales(main_layout)
        main_layout.addStretch(1)
        
        # Botones principales
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        
        textos_botones = ["Nuevo", "Guardar", "Cancelar", "Buscar", "Editar", "Limpiar", "Imprimir"]
        self.botones = []
        
        for texto in textos_botones:
            boton = QPushButton(texto)
            boton.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            boton.setCursor(Qt.PointingHandCursor)
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            botones_layout.addWidget(boton)
            self.botones.append(boton)
        
        main_layout.addLayout(botones_layout)
        self.setLayout(main_layout)

    def crear_grupo_cliente(self, parent_layout):
        grupo_cliente = QGroupBox("")
        grupo_cliente.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        readonly_style = INPUT_STYLE + "QLineEdit { background-color: #E8E8E8; color: #666666; }"
        
        # Folio
        self.txt_folio = QLineEdit()
        self.txt_folio.setStyleSheet(readonly_style)
        self.txt_folio.setReadOnly(True)
        self.txt_folio.setPlaceholderText("NV-Auto")
        layout.addWidget(QLabel("Folio", styleSheet=LABEL_STYLE))
        layout.addWidget(self.txt_folio, 1)
        
        # Estado
        self.txt_estado = QLineEdit()
        self.txt_estado.setStyleSheet(readonly_style)
        self.txt_estado.setReadOnly(True)
        layout.addWidget(QLabel("Estado", styleSheet=LABEL_STYLE))
        layout.addWidget(self.txt_estado, 1)
        
        # Cliente
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setStyleSheet(INPUT_STYLE)
        self.txt_cliente.setPlaceholderText("Escriba para buscar cliente...")
        layout.addWidget(QLabel("Cliente", styleSheet=LABEL_STYLE))
        layout.addWidget(self.txt_cliente, 3)
        
        # Fecha
        self.date_fecha = QDateEdit()
        self.date_fecha.setCalendarPopup(True)
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setDisplayFormat("dd/MM/yyyy")
        self.date_fecha.setStyleSheet(self._obtener_estilo_calendario())
        layout.addWidget(QLabel("Fecha", styleSheet=LABEL_STYLE))
        layout.addWidget(self.date_fecha, 1)
        
        # Referencia
        self.txt_referencia = QLineEdit()
        self.txt_referencia.setStyleSheet(INPUT_STYLE)
        self.txt_referencia.setPlaceholderText("Placa/ID de vehículo/cliente")
        layout.addWidget(QLabel("Referencia", styleSheet=LABEL_STYLE))
        layout.addWidget(self.txt_referencia, 2)
        
        grupo_cliente.setLayout(layout)
        parent_layout.addWidget(grupo_cliente)
    
    def crear_grupo_producto_servicio(self, parent_layout):
        grupo = QGroupBox("")
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Columnas responsivas
        for i, stretch in enumerate([1, 6, 2, 2, 1, 1]):
            grid_layout.setColumnStretch(i, stretch)
        
        # Labels
        labels = ["Cantidad", "Descripción", "Precio Unitario", "Importe", "IVA %"]
        for i, texto in enumerate(labels):
            lbl = QLabel(texto)
            lbl.setStyleSheet(LABEL_STYLE)
            grid_layout.addWidget(lbl, 0, i)
        
        # Campos
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setStyleSheet(INPUT_STYLE)
        self.txt_cantidad.setPlaceholderText("Cant.")
        self.txt_cantidad.setValidator(QDoubleValidator())
        grid_layout.addWidget(self.txt_cantidad, 1, 0)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(INPUT_STYLE)
        self.txt_descripcion.setPlaceholderText("Ingrese descripción")
        grid_layout.addWidget(self.txt_descripcion, 1, 1)
        
        self.txt_precio = QLineEdit()
        self.txt_precio.setStyleSheet(INPUT_STYLE)
        self.txt_precio.setPlaceholderText("$0.00")
        self.txt_precio.setValidator(QDoubleValidator(0.00, 9999999.99, 2))
        grid_layout.addWidget(self.txt_precio, 1, 2)
        
        self.txt_importe = QDoubleSpinBox()
        self.txt_importe.setReadOnly(True)
        self.txt_importe.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.txt_importe.setRange(0, 9999999.99)
        self.txt_importe.setDecimals(2)
        self.txt_importe.setPrefix("$ ")
        self.txt_importe.setStyleSheet(INPUT_STYLE)
        grid_layout.addWidget(self.txt_importe, 1, 3)
        
        self.txt_impuestos = QDoubleSpinBox()
        self.txt_impuestos.setRange(0, 100)
        self.txt_impuestos.setDecimals(2)
        self.txt_impuestos.setSuffix(" %")
        self.txt_impuestos.setValue(16.00)
        self.txt_impuestos.setStyleSheet(INPUT_STYLE)
        grid_layout.addWidget(self.txt_impuestos, 1, 4)
        
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setStyleSheet(FORM_BUTTON_STYLE)
        self.btn_agregar.setCursor(Qt.PointingHandCursor)
        grid_layout.addWidget(self.btn_agregar, 1, 5)
        
        grupo.setLayout(grid_layout)
        parent_layout.addWidget(grupo)
    
    def crear_tabla_items(self, parent_layout):
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels(["Cantidad", "Descripción", "Precio Unitario", "IVA", "Importe"])
        
        self.tabla_items = QTableView()
        self.tabla_items.setModel(self.tabla_model)
        self.tabla_items.horizontalHeader().setVisible(True)
        self.tabla_items.verticalHeader().setVisible(False)
        self.tabla_items.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_items.setStyleSheet(TABLE_STYLE)
        self.tabla_items.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_items.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_items.setSelectionMode(QTableView.SingleSelection)
        self.tabla_items.setMinimumHeight(450)
        
        # Header responsivo
        header = self.tabla_items.horizontalHeader()
        for i, mode in enumerate([QHeaderView.ResizeToContents, QHeaderView.Stretch, 
                                   QHeaderView.ResizeToContents, QHeaderView.ResizeToContents, 
                                   QHeaderView.ResizeToContents]):
            header.setSectionResizeMode(i, mode)
        
        header.setFixedHeight(40)
        self.tabla_items.verticalHeader().setDefaultSectionSize(30)
        
        parent_layout.addWidget(self.tabla_items)
    
    def crear_panel_totales(self, parent_layout):
        contenedor = QWidget()
        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)

        # Botones intermedios
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)

        self.btn_ver_ordenes = QPushButton("Ordenes")
        self.btn_ver_ordenes.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        self.btn_ver_ordenes.setCursor(Qt.PointingHandCursor)
        botones_layout.addWidget(self.btn_ver_ordenes, 1)
        
        self.btn_ver_notas = QPushButton("Notas Emitidas")
        self.btn_ver_notas.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        self.btn_ver_notas.setCursor(Qt.PointingHandCursor)
        botones_layout.addWidget(self.btn_ver_notas, 1)
        
        self.btn_pagos_abonos = QPushButton("Pagos y Abonos")
        self.btn_pagos_abonos.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        self.btn_pagos_abonos.setCursor(Qt.PointingHandCursor)
        botones_layout.addWidget(self.btn_pagos_abonos, 1)
        botones_layout.addStretch(1)

        botones_container = QWidget()
        botones_container.setLayout(botones_layout)
        layout_principal.addWidget(botones_container, 6)
        
        # Panel de totales
        totales_frame = QFrame()
        totales_frame.setFrameStyle(QFrame.StyledPanel)
        totales_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255,255,255,250), stop:1 rgba(245,245,245,250));
                border: 1px solid rgba(0,120,142,0.2);
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
            }
        """)
        
        totales_grid = QGridLayout()
        totales_grid.setSpacing(5)
        
        label_style = "QLabel { font-size: 18px; color: #333; background: transparent; padding: 2px; }"
        
        self.lbl_subtotal_valor = QLabel("$ 0.00")
        self.lbl_subtotal_valor.setStyleSheet(label_style + "font-weight: bold;")
        self.lbl_subtotal_valor.setAlignment(Qt.AlignRight)
        
        self.lbl_impuestos_valor = QLabel("$ 0.00")
        self.lbl_impuestos_valor.setStyleSheet(label_style + "font-weight: bold;")
        self.lbl_impuestos_valor.setAlignment(Qt.AlignRight)
        
        self.lbl_total_valor = QLabel("$ 0.00")
        self.lbl_total_valor.setStyleSheet("QLabel { font-size: 18px; font-weight: bold; color: #00788E; }")
        self.lbl_total_valor.setAlignment(Qt.AlignRight)
        
        totales_grid.addWidget(QLabel("Subtotal:", styleSheet=label_style), 0, 0)
        totales_grid.addWidget(self.lbl_subtotal_valor, 0, 1)
        totales_grid.addWidget(QLabel("Impuestos:", styleSheet=label_style), 1, 0)
        totales_grid.addWidget(self.lbl_impuestos_valor, 1, 1)
        
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: rgba(0,120,142,0.3); max-height: 1px;")
        totales_grid.addWidget(linea, 2, 0, 1, 2)
        
        totales_grid.addWidget(QLabel("Total:", styleSheet=label_style + "font-weight: bold;"), 3, 0)
        totales_grid.addWidget(self.lbl_total_valor, 3, 1)
        
        totales_container = QWidget()
        totales_container.setLayout(totales_grid)
        totales_container.setFixedWidth(220)
        
        totales_layout = QHBoxLayout()
        totales_layout.addStretch()
        totales_layout.addWidget(totales_container)
        totales_frame.setLayout(totales_layout)
        
        layout_principal.addWidget(totales_frame, 1)
        contenedor.setLayout(layout_principal)
        parent_layout.addWidget(contenedor)
    
    def conectar_senales(self):
        self.txt_cantidad.textChanged.connect(self.calcular_importe)
        self.txt_precio.textChanged.connect(self.calcular_importe)
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        self.tabla_items.doubleClicked.connect(self.cargar_item_para_editar)
        self.tabla_items.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        
        self.botones[0].clicked.connect(self.nueva_nota)
        self.botones[1].clicked.connect(self.guardar_nota)
        self.botones[2].clicked.connect(self.cancelar_nota)
        self.botones[3].clicked.connect(self.buscar_nota)
        self.botones[4].clicked.connect(self.editar_nota)
        self.botones[5].clicked.connect(self.nueva_nota)
        
        self.btn_ver_ordenes.clicked.connect(self.abrir_ventana_ordenes_borrador)
        self.btn_ver_notas.clicked.connect(self.abrir_ventana_notas)
        self.btn_pagos_abonos.clicked.connect(self.abrir_ventana_pagos)
    
    def cargar_clientes_bd(self):
        try:
            clientes = db_helper.get_clientes()
            self.clientes_dict.clear()
            
            nombres_clientes = [f"{c['nombre']} - {c['tipo']}" for c in clientes]
            for nombre, cliente in zip(nombres_clientes, clientes):
                self.clientes_dict[nombre] = cliente['id']
            
            completer = QCompleter(nombres_clientes)
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
                }
                QListView::item { padding: 10px; min-height: 30px; }
                QListView::item:hover { background-color: #E0F7FA; }
                QListView::item:selected { background-color: #2CD5C4; color: white; }
            """)
            
            self.txt_cliente.setCompleter(completer)
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar clientes: {e}")
    
    def guardar_nota(self):
        cliente_id = self.clientes_dict.get(self.txt_cliente.text())
        
        if not cliente_id:
            self.mostrar_advertencia("Seleccione un cliente válido")
            return
        
        if self.tabla_model.rowCount() == 0:
            self.mostrar_advertencia("Agregue al menos un item")
            return
        
        try:
            nota_data = {
                'cliente_id': cliente_id,
                'metodo_pago': None,
                'fecha': self.date_fecha.date().toPyDate().isoformat(),
                'observaciones': self.txt_referencia.text()
            }
            
            items = []
            for fila in range(self.tabla_model.rowCount()):
                if self.tipo_por_fila.get(fila, 'normal') != 'normal':
                    continue
                
                cantidad = int(self.tabla_model.item(fila, 0).text())
                descripcion = self.tabla_model.item(fila, 1).text()
                precio_unitario = float(self.tabla_model.item(fila, 2).text().replace('$', '').replace(',', ''))
                
                items.append({
                    'cantidad': cantidad,
                    'descripcion': descripcion,
                    'precio_unitario': precio_unitario,
                    'importe': cantidad * precio_unitario,
                    'impuesto': self.iva_por_fila.get(fila, 16.0)
                })
            
            if self.modo_edicion and self.nota_actual_id:
                nota = db_helper.actualizar_nota(self.nota_actual_id, nota_data, items)
                mensaje = "Nota actualizada"
            else:
                nota = db_helper.crear_nota(nota_data, items)
                mensaje = "Nota guardada"
            
            if nota:
                self.mostrar_exito(f"{mensaje}: {nota['folio']}")
                self.nueva_nota()
            else:
                self.mostrar_error("No se pudo guardar la nota")
            
        except Exception as e:
            self.mostrar_error(f"Error al guardar: {e}")
    
    def nueva_nota(self):
        self.nota_actual_id = None
        self.modo_edicion = False
        self.txt_folio.clear()
        self.txt_folio.setPlaceholderText("NV-Auto")
        self.txt_estado.clear()
        self.date_fecha.setDate(QDate.currentDate())
        self.txt_cliente.clear()
        self.txt_referencia.clear()
        
        self.tabla_model.setRowCount(0)
        self.iva_por_fila.clear()
        self.tipo_por_fila.clear()
        self._limpiar_campos_item()
        self.calcular_totales()
        self.controlar_estado_campos(True)
        
        if self.botones:
            self.botones[1].setText("Guardar")

    def buscar_nota(self):
        folio, ok = QInputDialog.getText(self, "Buscar Nota", "Ingrese el folio:")
        
        if ok and folio:
            try:
                notas = db_helper.buscar_notas(folio=folio)
                if notas:
                    self.cargar_nota_en_formulario(notas[0])
                else:
                    self.mostrar_advertencia("No se encontró la nota")
            except Exception as e:
                self.mostrar_error(f"Error al buscar: {e}")

    def abrir_ventana_notas(self):
        dialog = BuscarNotasDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.nota_seleccionada:
            self.cargar_nota_en_formulario(dialog.nota_seleccionada)
    
    def abrir_ventana_ordenes_borrador(self):
        if not BuscarOrdenesBorradorDialog:
            self.mostrar_error("Módulo de órdenes no disponible")
            return
        
        dialog = BuscarOrdenesBorradorDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.nota_seleccionada:
            self.cargar_nota_en_formulario(dialog.nota_seleccionada)
    
    def cargar_nota_en_formulario(self, nota):
        self.nota_actual_id = nota['id']
        self.modo_edicion = False
        
        self.txt_folio.setText(nota['folio'])
        self.date_fecha.setDate(QDate.fromString(nota['fecha'], "dd/MM/yyyy"))
        self.txt_referencia.setText(nota['observaciones'])
        self.txt_estado.setText(nota.get('estado', 'Registrado'))
        
        # Buscar cliente
        for nombre, id_cliente in self.clientes_dict.items():
            if id_cliente == nota['cliente_id']:
                self.txt_cliente.setText(nombre)
                break
        
        self.tabla_model.setRowCount(0)
        self.iva_por_fila.clear()
        self.tipo_por_fila.clear()
        
        if 'items' in nota:
            for item in nota['items']:
                fila = self.tabla_model.rowCount()
                self.tabla_model.insertRow(fila)
                
                self.tabla_model.setItem(fila, 0, self._crear_item(str(item['cantidad']), Qt.AlignCenter))
                self.tabla_model.setItem(fila, 1, self._crear_item(item['descripcion'], Qt.AlignLeft | Qt.AlignVCenter))
                self.tabla_model.setItem(fila, 2, self._crear_item(f"${item['precio_unitario']:.2f}", Qt.AlignCenter))
                self.tabla_model.setItem(fila, 3, self._crear_item(f"{item['impuesto']:.1f} %", Qt.AlignCenter))
                self.tabla_model.setItem(fila, 4, self._crear_item(f"${item['cantidad'] * item['precio_unitario']:.2f}", Qt.AlignCenter))
                
                self.iva_por_fila[fila] = item['impuesto']
                self.tipo_por_fila[fila] = 'normal'
        
        self.calcular_totales()
        if self.botones:
            self.botones[1].setText("Guardar")
        self.controlar_estado_campos(False)

    def _crear_item(self, texto, alineacion):
        """Helper para crear items de tabla"""
        item = QStandardItem(texto)
        item.setTextAlignment(alineacion)
        return item

    def cancelar_nota(self):
        if not self.nota_actual_id:
            self.mostrar_advertencia("No hay nota para cancelar")
            return
        
        respuesta = QMessageBox.question(
            self, "Confirmar", f"¿Cancelar la nota {self.txt_folio.text()}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                if db_helper.cancelar_nota(self.nota_actual_id):
                    self.mostrar_exito("Nota cancelada")
                    nota_actualizada = db_helper.get_nota(self.nota_actual_id)
                    if nota_actualizada:
                        self.cargar_nota_en_formulario(nota_actualizada)
                    else:
                        self.nueva_nota()
                else:
                    self.mostrar_error("No se pudo cancelar (ya está cancelada o pagada)")
            except Exception as e:
                self.mostrar_error(f"Error: {e}")
    
    def calcular_importe(self):
        try:
            cantidad_texto = self.txt_cantidad.text().strip()
            precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
            
            if cantidad_texto and precio_texto:
                self.txt_importe.setValue(float(cantidad_texto) * float(precio_texto))
            else:
                self.txt_importe.setValue(0)
        except ValueError:
            self.txt_importe.setValue(0)
    
    def agregar_a_tabla(self):
        if not self.validar_datos():
            return
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        precio = float(self.txt_precio.text().replace("$", "").replace(",", "").strip())
        iva = self.txt_impuestos.value()
        importe = float(cantidad) * precio
        
        fila = self.tabla_model.rowCount()
        self.tabla_model.insertRow(fila)
        
        self.tabla_model.setItem(fila, 0, self._crear_item(cantidad, Qt.AlignCenter))
        self.tabla_model.setItem(fila, 1, self._crear_item(descripcion, Qt.AlignLeft | Qt.AlignVCenter))
        self.tabla_model.setItem(fila, 2, self._crear_item(f"${precio:.2f}", Qt.AlignCenter))
        self.tabla_model.setItem(fila, 3, self._crear_item(f"{iva:.1f} %", Qt.AlignCenter))
        self.tabla_model.setItem(fila, 4, self._crear_item(f"${importe:.2f}", Qt.AlignCenter))
        
        self.iva_por_fila[fila] = iva
        self.tipo_por_fila[fila] = 'normal'
        
        self.calcular_totales()
        self._limpiar_campos_item()
        self.tabla_items.selectRow(fila)
    
    def cargar_item_para_editar(self, index):
        fila = index.row()
        
        if self.tipo_por_fila.get(fila, 'normal') in ['nota', 'seccion']:
            self.editar_nota_o_seccion(fila)
            return
        
        self.txt_cantidad.setText(self.tabla_model.index(fila, 0).data())
        self.txt_descripcion.setText(self.tabla_model.index(fila, 1).data())
        self.txt_precio.setText(self.tabla_model.index(fila, 2).data().replace("$", "").replace(",", "").strip())
        self.txt_impuestos.setValue(self.iva_por_fila.get(fila, 16.0))
        
        self.fila_en_edicion = fila
        self.btn_agregar.setText("Actualizar")
        
        try:
            self.btn_agregar.clicked.disconnect()
        except TypeError:
            pass
        self.btn_agregar.clicked.connect(self.actualizar_item)
    
    def actualizar_item(self):
        if self.fila_en_edicion == -1 or not self.validar_datos():
            return
        
        fila = self.fila_en_edicion
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        precio = float(self.txt_precio.text().replace("$", "").replace(",", "").strip())
        iva = self.txt_impuestos.value()
        importe = float(cantidad) * precio
        
        self.tabla_model.item(fila, 0).setText(cantidad)
        self.tabla_model.item(fila, 1).setText(descripcion)
        self.tabla_model.item(fila, 2).setText(f"${precio:.2f}")
        self.tabla_model.item(fila, 3).setText(f"{iva:.1f} %")
        self.tabla_model.item(fila, 4).setText(f"${importe:.2f}")
        
        self.iva_por_fila[fila] = iva
        self.calcular_totales()
        self._limpiar_campos_item()
    
    def calcular_totales(self):
        subtotal = total_impuestos = 0
        
        for fila in range(self.tabla_model.rowCount()):
            if self.tipo_por_fila.get(fila, 'normal') != 'normal':
                continue
            
            importe = float(self.tabla_model.item(fila, 4).text().replace("$", "").replace(",", ""))
            iva_porcentaje = self.iva_por_fila.get(fila, 16.0)
            
            subtotal += importe
            total_impuestos += importe * (iva_porcentaje / 100)
        
        self.lbl_subtotal_valor.setText(f"$ {subtotal:,.2f}")
        self.lbl_impuestos_valor.setText(f"$ {total_impuestos:,.2f}")
        self.lbl_total_valor.setText(f"$ {subtotal + total_impuestos:,.2f}")
    
    def mostrar_menu_contextual(self, position):
        menu = QMenu(self)
        menu.addSection("Insertar")
        
        menu.addAction("➕ Agregar Nota", self.insertar_nota)
        menu.addAction("📁 Agregar Sección", self.insertar_seccion)
        menu.addSeparator()
        
        indexes = self.tabla_items.selectedIndexes()
        if indexes:
            fila = indexes[0].row()
            menu.addSection("Acciones")
            
            if self.tipo_por_fila.get(fila, 'normal') in ['nota', 'seccion']:
                menu.addAction("✏️ Editar", lambda: self.editar_nota_o_seccion(fila))
                menu.addSeparator()
            
            menu.addAction("Mover Arriba", lambda: self.mover_fila_arriba(fila)).setEnabled(fila > 0)
            menu.addAction("Mover Abajo", lambda: self.mover_fila_abajo(fila)).setEnabled(fila < self.tabla_model.rowCount() - 1)
            menu.addSeparator()
            menu.addAction("Eliminar", lambda: self.eliminar_fila(fila))
        
        menu.exec_(self.tabla_items.viewport().mapToGlobal(position))
    
    def insertar_nota(self):
        texto, ok = QInputDialog.getText(self, "Agregar Nota", "Texto de la nota:")
        if ok and texto:
            self._insertar_fila_especial(f"📝 {texto}", 'nota', QColor(245, 245, 245), QColor(100, 100, 100))

    def insertar_seccion(self):
        texto, ok = QInputDialog.getText(self, "Agregar Sección", "Nombre de la sección:")
        if ok and texto:
            self._insertar_fila_especial(texto.upper(), 'seccion', QColor(0, 120, 142, 30), QColor(0, 120, 142), bold=True)

    def _insertar_fila_especial(self, texto, tipo, bg_color, fg_color, bold=False):
        """Helper para insertar notas y secciones"""
        fila = self.tabla_model.rowCount()
        self.tabla_model.insertRow(fila)
        
        item = QStandardItem(texto)
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        item.setBackground(bg_color)
        item.setForeground(fg_color)
        
        if bold:
            font = item.font()
            font.setBold(True)
            font.setPointSize(10)
            item.setFont(font)
        
        self.tabla_model.setItem(fila, 0, item)
        self.tabla_items.setSpan(fila, 0, 1, 5)
        self.tipo_por_fila[fila] = tipo

    def editar_nota_o_seccion(self, fila):
        tipo = self.tipo_por_fila.get(fila, 'normal')
        if tipo == 'normal':
            return
        
        item = self.tabla_model.item(fila, 0)
        texto_actual = item.text().replace("📝 ", "") if tipo == 'nota' else item.text()
        
        titulo = "Editar Nota" if tipo == 'nota' else "Editar Sección"
        texto_nuevo, ok = QInputDialog.getText(self, titulo, "Modificar:", QLineEdit.Normal, texto_actual)
        
        if ok and texto_nuevo:
            if tipo == 'nota':
                self._insertar_fila_especial(f"📝 {texto_nuevo}", 'nota', QColor(245, 245, 245), QColor(100, 100, 100))
            else:
                self._insertar_fila_especial(texto_nuevo.upper(), 'seccion', QColor(0, 120, 142, 30), QColor(0, 120, 142), bold=True)
            self.tabla_model.removeRow(fila)
    
    def mover_fila_arriba(self, fila):
        if fila > 0:
            self.intercambiar_filas(fila, fila - 1)
            self.tabla_items.selectRow(fila - 1)
    
    def mover_fila_abajo(self, fila):
        if fila < self.tabla_model.rowCount() - 1:
            self.intercambiar_filas(fila, fila + 1)
            self.tabla_items.selectRow(fila + 1)
    
    def intercambiar_filas(self, fila1, fila2):
        # Usar takeItem para tomar posesión de los items y evitar que se eliminen
        items_fila1 = []
        items_fila2 = []
        
        for col in range(self.tabla_model.columnCount()):
            items_fila1.append(self.tabla_model.takeItem(fila1, col))
            items_fila2.append(self.tabla_model.takeItem(fila2, col))

        # Colocar los items en sus nuevas filas
        for col, item in enumerate(items_fila2):
            self.tabla_model.setItem(fila1, col, item if item else QStandardItem(""))
        
        for col, item in enumerate(items_fila1):
            self.tabla_model.setItem(fila2, col, item if item else QStandardItem(""))

        # Intercambiar metadatos
        tipo1 = self.tipo_por_fila.get(fila1, 'normal')
        tipo2 = self.tipo_por_fila.get(fila2, 'normal')
        self.tipo_por_fila[fila1] = tipo2
        self.tipo_por_fila[fila2] = tipo1
        
        iva1 = self.iva_por_fila.get(fila1, 16.0)
        iva2 = self.iva_por_fila.get(fila2, 16.0)
        self.iva_por_fila[fila1] = iva2
        self.iva_por_fila[fila2] = iva1
        
        # Restaurar spans para ambas filas (AQUÍ ESTÁ LA CORRECCIÓN)
        for f in [fila1, fila2]:
            tipo = self.tipo_por_fila.get(f, 'normal')
            if tipo in ['nota', 'seccion']:
                # Asignar span de 5 columnas para notas/secciones
                self.tabla_items.setSpan(f, 0, 1, 5)
            else:
                # Restaurar span normal (1 por columna)
                self.tabla_items.setSpan(f, 0, 1, 1)
    
    def eliminar_fila(self, fila):
        if QMessageBox.question(self, 'Confirmar', '¿Eliminar este item?',
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.tabla_model.removeRow(fila)
            
            # Reindexar metadatos
            self.iva_por_fila = {i if i < fila else i: self.iva_por_fila.get(i+1 if i >= fila else i, 16.0)
                                 for i in range(self.tabla_model.rowCount())}
            self.tipo_por_fila = {i if i < fila else i: self.tipo_por_fila.get(i+1 if i >= fila else i, 'normal')
                                  for i in range(self.tabla_model.rowCount())}
            
            self.calcular_totales()

    def editar_nota(self):
        if not self.nota_actual_id:
            self.mostrar_advertencia("No hay nota cargada")
            return
        if self.txt_estado.text() == 'Cancelada':
            self.mostrar_advertencia("No se puede editar una nota cancelada")
            return
        
        self.modo_edicion = True
        self.controlar_estado_campos(True)
        if self.botones:
            self.botones[1].setText("Actualizar")
        self.mostrar_exito("Modo edición activado")
    
    def controlar_estado_campos(self, habilitar):
        self.txt_cliente.setReadOnly(not habilitar)
        self.date_fecha.setEnabled(habilitar)
        self.txt_referencia.setReadOnly(not habilitar)
        self.txt_cantidad.setReadOnly(not habilitar)
        self.txt_descripcion.setReadOnly(not habilitar)
        self.txt_precio.setReadOnly(not habilitar)
        self.btn_agregar.setEnabled(habilitar)
        
        self.tabla_items.setEditTriggers(QTableView.DoubleClicked if habilitar else QTableView.NoEditTriggers)
    
    def abrir_ventana_pagos(self):
        if not PagosNotaDialog:
            self.mostrar_error("Módulo de pagos no disponible")
            return
        
        dialog = PagosNotaDialog(self)
        if self.nota_actual_id:
            try:
                nota = db_helper.get_nota(self.nota_actual_id)
                if nota:
                    dialog.cargar_nota(nota)
            except Exception as e:
                self.mostrar_error(f"Error al cargar nota: {e}")
        
        dialog.exec_()
        
        if self.nota_actual_id:
            try:
                nota_actualizada = db_helper.get_nota(self.nota_actual_id)
                if nota_actualizada:
                    self.cargar_nota_en_formulario(nota_actualizada)
            except Exception as e:
                self.mostrar_error(f"Error al recargar: {e}")
    
    def validar_datos(self):
        try:
            cantidad = self.txt_cantidad.text().strip()
            if not cantidad or float(cantidad) <= 0:
                self.mostrar_advertencia("Cantidad inválida")
                return False
        except ValueError:
            self.mostrar_advertencia("Cantidad debe ser numérica")
            return False
        
        if not self.txt_descripcion.text():
            self.mostrar_advertencia("Ingrese descripción")
            return False
        
        try:
            precio = float(self.txt_precio.text().replace("$", "").replace(",", "").strip())
            if precio < 0:
                self.mostrar_advertencia("Precio no puede ser negativo")
                return False
            if precio == 0 and self.txt_estado.text() != "Borrador":
                self.mostrar_advertencia("Precio 0.00 solo en Borrador")
                return False
        except ValueError:
            self.mostrar_advertencia("Precio inválido")
            return False
        
        return True
    
    def _limpiar_campos_item(self):
        self.txt_cantidad.clear()
        self.txt_descripcion.clear()
        self.txt_precio.clear()
        self.txt_importe.setValue(0)
        self.txt_impuestos.setValue(16.00)
        self.txt_cantidad.setFocus()
        
        self.btn_agregar.setText("Agregar")
        try:
            self.btn_agregar.clicked.disconnect()
        except TypeError:
            pass
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        self.fila_en_edicion = -1
    
    def mostrar_advertencia(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Warning, "Advertencia", mensaje)
    
    def mostrar_error(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Critical, "Error", mensaje)
    
    def mostrar_exito(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Information, "Éxito", mensaje)
    
    def _mostrar_mensaje(self, icono, titulo, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(icono)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(MESSAGE_BOX_STYLE)
        msg.exec_()
    
    def _obtener_estilo_calendario(self):
        return """
            QDateEdit {
                padding: 8px; border: 2px solid #F5F5F5; border-radius: 6px;
                background-color: #F5F5F5; min-height: 25px; font-size: 16px;
            }
            QDateEdit:focus { border: 2px solid #2CD5C4; background-color: white; }
            QDateEdit::drop-down { border: 0px; background: transparent; width: 30px; }
            QDateEdit::down-arrow { width: 16px; height: 16px; }
            QCalendarWidget { background-color: white; border: 2px solid #00788E; border-radius: 8px; }
            QCalendarWidget QToolButton { 
                color: white; background-color: #00788E; border: none; 
                border-radius: 4px; margin: 2px; padding: 4px; 
            }
            QCalendarWidget QToolButton:hover { background-color: #2CD5C4; }
            QCalendarWidget QAbstractItemView { 
                selection-background-color: #2CD5C4; selection-color: white; 
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #00788E; }
        """

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        from gui.api_client import api_client as db_helper
    except ImportError:
        print("Error: Servidor no disponible")
        sys.exit(1)
    window = NotasWindow()
    window.show()
    sys.exit(app.exec_())
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
from PyQt5.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem, QColor, QFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.api_client import api_client as db_helper
from gui.websocket_client import ws_client

from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE, LABEL_STYLE,
    INPUT_STYLE, TABLE_STYLE, FORM_BUTTON_STYLE, MESSAGE_BOX_STYLE
)

try:
    from dialogs.buscar_notas_proveedor_dialog import BuscarNotasProveedorDialog
except ImportError:
    print("Advertencia: No se pudo importar BuscarNotasProveedorDialog. Se usará QInputDialog.")
    BuscarNotasProveedorDialog = None

try:
    from dialogs.pagos_nota_proveedor_dialog import PagosNotaProveedorDialog
except ImportError:
    print("Advertencia: No se pudo importar PagosNotaProveedorDialog.")
    PagosNotaProveedorDialog = None

class NotasProveedoresWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Notas de Proveedores")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        self.fila_en_edicion = -1
        self.iva_por_fila = {}
        self.tipo_por_fila = {}  
        
        self.proveedores_dict = {}
        self.nota_actual_id = None
        self.modo_edicion = False
        self._datos_cargados = False

        self.setup_ui()
        self.conectar_senales()
        
        if ws_client:
            ws_client.proveedor_creado.connect(self.on_notificacion_proveedor)

        self.nueva_nota() 
        QTimer.singleShot(100, self._cargar_datos_inicial)

    def _cargar_datos_inicial(self):
        if not self._datos_cargados:
            self.cargar_proveedores_bd()
            self._datos_cargados = True

    def on_notificacion_proveedor(self, data):
        self.cargar_proveedores_bd()
    
    def on_notificacion_nota(self, data):
        if self.nota_actual_id and data.get('id') == self.nota_actual_id:
            print(f"Recargando nota proveedor {self.nota_actual_id} por notificación.")
            try:
                nota_actualizada = db_helper.get_nota_proveedor(self.nota_actual_id)
                if nota_actualizada:
                    self.cargar_nota_en_formulario(nota_actualizada)
            except Exception as e:
                print(f"Error recargando nota proveedor: {e}")

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.crear_grupo_proveedor(main_layout)
        self.crear_grupo_producto_servicio(main_layout)
        self.crear_tabla_items(main_layout)
        self.crear_panel_totales(main_layout)
        
        main_layout.addStretch(1)
        
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        botones_layout.setContentsMargins(0, 0, 0, 0)
        
        textos_botones = ["Nueva", "Guardar", "Cancelar", "Buscar", "Editar", "Limpiar", "Imprimir"]
        
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

    def crear_grupo_proveedor(self, parent_layout):
        grupo_proveedor = QGroupBox("")
        grupo_proveedor.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        readonly_style = INPUT_STYLE + """
            QLineEdit {
                background-color: #E8E8E8;
                color: #666666;
            }
        """
        
        lbl_folio = QLabel("Folio")
        lbl_folio.setStyleSheet(LABEL_STYLE)
        self.txt_folio = QLineEdit()
        self.txt_folio.setStyleSheet(readonly_style)
        self.txt_folio.setReadOnly(True)
        self.txt_folio.setPlaceholderText("NP-Auto")
        
        lbl_estado = QLabel("Estado")
        lbl_estado.setStyleSheet(LABEL_STYLE)
        self.txt_estado = QLineEdit()
        self.txt_estado.setStyleSheet(readonly_style)
        self.txt_estado.setReadOnly(True)
        self.txt_estado.setPlaceholderText("Estado")
        
        lbl_proveedor = QLabel("Proveedor")
        lbl_proveedor.setStyleSheet(LABEL_STYLE)
        self.txt_proveedor = QLineEdit()
        self.txt_proveedor.setStyleSheet(INPUT_STYLE)
        self.txt_proveedor.setPlaceholderText("Escriba para buscar proveedor...")
        
        lbl_fecha = QLabel("Fecha")
        lbl_fecha.setStyleSheet(LABEL_STYLE)
        self.date_fecha = QDateEdit()
        self.date_fecha.setCalendarPopup(True)
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setDisplayFormat("dd/MM/yyyy")
        self.date_fecha.setStyleSheet(self._obtener_estilo_calendario())
        
        lbl_referencia = QLabel("Referencia")
        lbl_referencia.setStyleSheet(LABEL_STYLE)
        self.txt_referencia = QLineEdit()
        self.txt_referencia.setStyleSheet(INPUT_STYLE)
        self.txt_referencia.setPlaceholderText("Factura / N° Pedido Proveedor")
        
        layout.addWidget(lbl_folio)
        layout.addWidget(self.txt_folio, 1)
        
        layout.addWidget(lbl_estado)
        layout.addWidget(self.txt_estado, 1)
        
        layout.addWidget(lbl_proveedor)
        layout.addWidget(self.txt_proveedor, 3)
        
        layout.addWidget(lbl_fecha)
        layout.addWidget(self.date_fecha, 1)
        
        layout.addWidget(lbl_referencia)
        layout.addWidget(self.txt_referencia, 2)
        
        grupo_proveedor.setLayout(layout)
        parent_layout.addWidget(grupo_proveedor)

    def obtener_datos_proveedor(self):
        nombre_proveedor = self.txt_proveedor.text()
        proveedor_id = self.proveedores_dict.get(nombre_proveedor, None)
        
        return {
            'proveedor_id': proveedor_id,
            'fecha': self.date_fecha.date().toPyDate(),
            'referencia': self.txt_referencia.text()
        }
    
    def crear_grupo_producto_servicio(self, parent_layout):
        grupo = QGroupBox("")
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        grid_layout.setColumnStretch(0, 1)    
        grid_layout.setColumnStretch(1, 6)    
        grid_layout.setColumnStretch(2, 2)    
        grid_layout.setColumnStretch(3, 2)    
        grid_layout.setColumnStretch(4, 1)    
        grid_layout.setColumnStretch(5, 1)    
        
        lbl_cantidad = QLabel("Cantidad")
        lbl_cantidad.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_cantidad, 0, 0)
        
        lbl_descripcion = QLabel("Descripción")
        lbl_descripcion.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_descripcion, 0, 1)
        
        lbl_precio = QLabel("Precio Unitario")
        lbl_precio.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_precio, 0, 2)
        
        lbl_importe = QLabel("Importe")
        lbl_importe.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_importe, 0, 3)
        
        lbl_impuestos = QLabel("IVA %")
        lbl_impuestos.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_impuestos, 0, 4)
        
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setStyleSheet(INPUT_STYLE)
        self.txt_cantidad.setPlaceholderText("Cant.")
        self.txt_cantidad.setValidator(QDoubleValidator())
        grid_layout.addWidget(self.txt_cantidad, 1, 0)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(INPUT_STYLE)
        self.txt_descripcion.setPlaceholderText("Ingrese descripción del producto o servicio")
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
        self.tabla_model.setHorizontalHeaderLabels([
            "Cantidad", 
            "Descripción", 
            "Precio Unitario", 
            "IVA", 
            "Importe"
        ])
        
        self.tabla_items = QTableView()
        self.tabla_items.setModel(self.tabla_model)
        self.tabla_items.horizontalHeader().setVisible(True)
        self.tabla_items.verticalHeader().setVisible(False)
        self.tabla_items.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_items.setStyleSheet(TABLE_STYLE)
        
        header = self.tabla_items.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        header.setFixedHeight(40)
        self.tabla_items.verticalHeader().setDefaultSectionSize(30)
        
        self.tabla_items.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_items.setSelectionMode(QTableView.SingleSelection)
        
        self.tabla_items.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_items.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        
        self.tabla_items.setMinimumHeight(15 * 30 + 40)
        parent_layout.addWidget(self.tabla_items)
    
    def crear_panel_totales(self, parent_layout):
        contenedor_principal = QWidget()
        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(0, 0, 0, 0)

        self.botones_intermedios_layout = QHBoxLayout()
        self.botones_intermedios_layout.setContentsMargins(0, 10, 0, 0)
        self.botones_intermedios_layout.setSpacing(10)
        
        self.btn_ver_notas = QPushButton("Notas de Proveedor")
        self.btn_ver_notas.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        self.btn_ver_notas.setCursor(Qt.PointingHandCursor)
        self.btn_ver_notas.clicked.connect(self.abrir_ventana_notas)
        self.btn_ver_notas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.botones_intermedios_layout.addWidget(self.btn_ver_notas, 1)
        
        self.btn_pagos_abonos = QPushButton("Pagos y Abonos")
        self.btn_pagos_abonos.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        self.btn_pagos_abonos.setCursor(Qt.PointingHandCursor)
        self.btn_pagos_abonos.clicked.connect(self.abrir_ventana_pagos)
        self.btn_pagos_abonos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.botones_intermedios_layout.addWidget(self.btn_pagos_abonos, 1)
        
        self.botones_intermedios_layout.addStretch(1)         
        botones_intermedios_container = QWidget()
        botones_intermedios_container.setLayout(self.botones_intermedios_layout)
        layout_principal.addWidget(botones_intermedios_container, 6)
        
        contenedor_frame = QWidget()
        contenedor_frame.setMaximumWidth(9999)
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        
        totales_frame = QFrame()
        totales_frame.setFrameStyle(QFrame.StyledPanel)
        totales_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 250),
                    stop: 1 rgba(245, 245, 245, 250)
                );
                border: 1px solid rgba(0, 120, 142, 0.2);
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
            }
        """)
        
        main_totales_layout = QHBoxLayout()
        main_totales_layout.addStretch()
        
        totales_grid = QGridLayout()
        totales_grid.setSpacing(5)
        totales_grid.setContentsMargins(0, 0, 0, 0)
        
        label_style = """
            QLabel {
                font-size: 18px;
                color: #333333;
                background: transparent;
                padding: 2px;
            }
        """
        label_bold_style = label_style + "font-weight: bold;"
        
        lbl_subtotal_text = QLabel("Subtotal:")
        lbl_subtotal_text.setStyleSheet(label_style)
        lbl_subtotal_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.lbl_subtotal_valor = QLabel("$ 0.00")
        self.lbl_subtotal_valor.setStyleSheet(label_bold_style)
        self.lbl_subtotal_valor.setAlignment(Qt.AlignRight)
        
        lbl_impuestos_text = QLabel("Impuestos:")
        lbl_impuestos_text.setStyleSheet(label_style)
        lbl_impuestos_text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.lbl_impuestos_valor = QLabel("$ 0.00")
        self.lbl_impuestos_valor.setStyleSheet(label_bold_style)
        self.lbl_impuestos_valor.setAlignment(Qt.AlignRight)
        
        linea = QFrame()
        linea.setFrameShape(QFrame.HLine)
        linea.setStyleSheet("background-color: rgba(0, 120, 142, 0.3); max-height: 1px;")
        
        lbl_total_text = QLabel("Total:")
        lbl_total_text.setStyleSheet(label_style + "font-size: 18px; font-weight: bold;")
        lbl_total_text.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        
        self.lbl_total_valor = QLabel("$ 0.00")
        self.lbl_total_valor.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #00788E;
                background: transparent;
                padding: 2px;
            }
        """)
        self.lbl_total_valor.setAlignment(Qt.AlignRight)
        
        totales_grid.addWidget(lbl_subtotal_text, 0, 0)
        totales_grid.addWidget(self.lbl_subtotal_valor, 0, 1)
        totales_grid.addWidget(lbl_impuestos_text, 1, 0)
        totales_grid.addWidget(self.lbl_impuestos_valor, 1, 1)
        totales_grid.addWidget(linea, 2, 0, 1, 2)
        totales_grid.addWidget(lbl_total_text, 3, 0)
        totales_grid.addWidget(self.lbl_total_valor, 3, 1)
        
        totales_grid.setColumnMinimumWidth(0, 80)
        totales_grid.setColumnMinimumWidth(1, 120)
        
        totales_container = QWidget()
        totales_container.setLayout(totales_grid)
        totales_container.setFixedWidth(220)
        
        main_totales_layout.addWidget(totales_container)
        totales_frame.setLayout(main_totales_layout)
        
        frame_layout.addWidget(totales_frame)
        contenedor_frame.setLayout(frame_layout)
        
        layout_principal.addWidget(contenedor_frame, 1)
        contenedor_principal.setLayout(layout_principal)
        parent_layout.addWidget(contenedor_principal)

    def conectar_senales(self):
        self.txt_cantidad.textChanged.connect(self.calcular_importe)
        self.txt_precio.textChanged.connect(self.calcular_importe)
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        
        self.tabla_items.doubleClicked.connect(self.cargar_item_para_editar)
        
        self.botones[0].clicked.connect(self.nueva_nota)
        self.botones[1].clicked.connect(self.guardar_nota)
        self.botones[2].clicked.connect(self.cancelar_nota)
        self.botones[3].clicked.connect(self.buscar_nota)
        self.botones[4].clicked.connect(self.editar_nota)
        self.botones[5].clicked.connect(self.nueva_nota)
    
    def cargar_proveedores_bd(self):
        try:
            proveedores = db_helper.get_proveedores() 
            self.proveedores_dict.clear() 
            
            nombres_proveedores = [] 
            for proveedor in proveedores:
                nombre = proveedor.get('nombre', 'Proveedor Desconocido')
                tipo = proveedor.get('tipo', 'Sin Tipo')
                
                nombre_completo = f"{nombre} - {tipo}"
                nombres_proveedores.append(nombre_completo)
                self.proveedores_dict[nombre_completo] = proveedor['id']
            
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
    
    def guardar_nota(self):
        nombre_proveedor = self.txt_proveedor.text()
        proveedor_id = self.proveedores_dict.get(nombre_proveedor, None) 
        
        if not proveedor_id:
            self.mostrar_advertencia("Seleccione un proveedor válido de la lista")
            return
        
        if self.tabla_model.rowCount() == 0:
            self.mostrar_advertencia("Agregue al menos un item")
            return
        
        try:
            nota_data = {
                'proveedor_id': proveedor_id,
                'metodo_pago': None, 
                'fecha': self.date_fecha.date().toPyDate(),
                'observaciones': self.txt_referencia.text()
            }
            
            items = []
            for fila in range(self.tabla_model.rowCount()):
                tipo = self.tipo_por_fila.get(fila, 'normal')
                if tipo != 'normal':
                    continue
                
                cantidad_texto = self.tabla_model.item(fila, 0).text()
                descripcion = self.tabla_model.item(fila, 1).text()
                precio_texto = self.tabla_model.item(fila, 2).text().replace('$', '').replace(',', '')
                
                try:
                    cantidad = float(cantidad_texto)
                    precio_unitario = float(precio_texto)
                except ValueError:
                    self.mostrar_error(f"Error en fila {fila+1}: Cantidad o precio no son numéricos.")
                    return

                importe = cantidad * precio_unitario
                iva_porcentaje = self.iva_por_fila.get(fila, 16.0)
                
                item_data = {
                    'cantidad': cantidad,
                    'descripcion': descripcion,
                    'precio_unitario': precio_unitario,
                    'importe': importe,
                    'impuesto': iva_porcentaje
                }
                items.append(item_data)
            
            if self.modo_edicion and self.nota_actual_id:
                nota = db_helper.actualizar_nota_proveedor(self.nota_actual_id, nota_data, items)
                mensaje = "Nota actualizada correctamente"
            else:
                nota = db_helper.crear_nota_proveedor(nota_data, items)
                mensaje = "Nota guardada correctamente"

            if nota:
                self.txt_folio.setText(nota['folio'])
                self.nota_actual_id = nota['id']
                self.txt_estado.setText(nota.get('estado', 'Registrado'))
                self.modo_edicion = False
                self.controlar_estado_campos(False)
                self.mostrar_exito(f"{mensaje}: {nota['folio']}")
            else:
                self.mostrar_error("No se pudo guardar la nota.")
            
        except Exception as e:
            self.mostrar_error(f"Error al guardar: {e}")
            import traceback
            traceback.print_exc()

    def nueva_nota(self):
            self.nota_actual_id = None
            self.modo_edicion = False
            self.txt_folio.clear()
            self.txt_folio.setPlaceholderText("NP-Auto")
            self.txt_estado.clear()
            self.txt_estado.setPlaceholderText("Estado")
            
            self.date_fecha.setDate(QDate.currentDate())
            self.txt_proveedor.clear()
            self.txt_referencia.clear()
            
            self.tabla_model.setRowCount(0)
            self.iva_por_fila.clear()
            self.tipo_por_fila.clear()
            
            self._limpiar_campos_item()
            self.calcular_totales()
            self.controlar_estado_campos(True)

            if hasattr(self, 'botones') and len(self.botones) > 1:
                self.botones[1].setText("Guardar")

    def buscar_nota(self):
        folio, ok = QInputDialog.getText(self, "Buscar Nota Proveedor", "Ingrese el folio:")
        
        if ok and folio:
            try:
                notas = db_helper.buscar_notas_proveedor(folio=folio)
                
                if notas:
                    self.cargar_nota_en_formulario(notas[0])
                else:
                    self.mostrar_advertencia("No se encontró la nota")
                    
            except Exception as e:
                self.mostrar_error(f"Error al buscar: {e}")

    def abrir_ventana_notas(self):
        if BuscarNotasProveedorDialog is None:
            self.mostrar_error("Error Crítico: No se pudo cargar el módulo 'BuscarNotasProveedorDialog'.")
            return
            
        dialog = BuscarNotasProveedorDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.nota_seleccionada:
            self.cargar_nota_en_formulario(dialog.nota_seleccionada)

    def _crear_item(self, texto, alineacion):
        item = QStandardItem(texto)
        item.setTextAlignment(alineacion)
        return item

    def cargar_nota_en_formulario(self, nota):
        if not nota:
            self.mostrar_error("Error: Se intentó cargar una nota nula.")
            return

        self.nota_actual_id = nota['id']
        self.modo_edicion = False
        
        self.txt_folio.setText(nota['folio'])
        self.date_fecha.setDate(QDate.fromString(nota['fecha'], "dd/MM/yyyy"))
        self.txt_referencia.setText(nota['observaciones'])
        self.txt_estado.setText(nota.get('estado', 'Registrado'))
        
        self.txt_proveedor.clear()
        for nombre, id_proveedor in self.proveedores_dict.items():
            if id_proveedor == nota['proveedor_id']:
                self.txt_proveedor.setText(nombre)
                break
        
        self.tabla_model.setRowCount(0)
        self.iva_por_fila.clear()
        self.tipo_por_fila.clear()
        
        if 'items' in nota:
            for item in nota['items']:
                cantidad = str(item['cantidad'])
                descripcion = item['descripcion']
                precio_formateado = f"${item['precio_unitario']:.2f}"
                iva_porcentaje = item['impuesto']
                iva_texto = f"{iva_porcentaje:.1f} %"
                importe_calculado = item['cantidad'] * item['precio_unitario']
                importe_formateado = f"${importe_calculado:.2f}"

                fila = self.tabla_model.rowCount()
                self.tabla_model.insertRow(fila)
                
                self.tabla_model.setItem(fila, 0, self._crear_item(cantidad, Qt.AlignCenter))
                self.tabla_model.setItem(fila, 1, self._crear_item(descripcion, Qt.AlignLeft | Qt.AlignVCenter))
                self.tabla_model.setItem(fila, 2, self._crear_item(precio_formateado, Qt.AlignCenter))
                self.tabla_model.setItem(fila, 3, self._crear_item(iva_texto, Qt.AlignCenter))
                self.tabla_model.setItem(fila, 4, self._crear_item(importe_formateado, Qt.AlignCenter))
                
                self.iva_por_fila[fila] = iva_porcentaje
                self.tipo_por_fila[fila] = 'normal'
        
        self.calcular_totales()

        if hasattr(self, 'botones') and len(self.botones) > 1:
            self.botones[1].setText("Guardar")

        self.controlar_estado_campos(False)

    def cancelar_nota(self):
        if not self.nota_actual_id:
            self.mostrar_advertencia("No hay una nota para cancelar")
            return
        
        respuesta = QMessageBox.question(
            self, 
            "Confirmar Cancelación", 
            f"¿Cancelar la nota {self.txt_folio.text()}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                success = db_helper.cancelar_nota_proveedor(self.nota_actual_id)

                if success:
                    self.mostrar_exito("Nota cancelada")
                    nota_actualizada = db_helper.get_nota_proveedor(self.nota_actual_id)
                    if nota_actualizada:
                        self.cargar_nota_en_formulario(nota_actualizada)
                    else:
                        self.nueva_nota() 
                else:
                    self.mostrar_error("No se pudo cancelar (puede estar ya cancelada o pagada)")
            except Exception as e:
                self.mostrar_error(f"Error al cancelar: {e}")

    def calcular_importe(self):
        try:
            cantidad_texto = self.txt_cantidad.text()
            precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
            
            if cantidad_texto and precio_texto:
                cantidad = float(cantidad_texto)
                precio = float(precio_texto)
                importe = cantidad * precio
                self.txt_importe.setValue(importe)
            else:
                self.txt_importe.setValue(0)
        except ValueError:
            self.txt_importe.setValue(0)
    
    def agregar_a_tabla(self):
        if not self.validar_datos():
            return
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        
        precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
        precio = float(precio_texto)
        precio_formateado = f"${precio:.2f}"
        
        cantidad_calculo = float(cantidad) if cantidad else 1
        importe = cantidad_calculo * precio
        importe_formateado = f"${importe:.2f}"

        iva_porcentaje = self.txt_impuestos.value()
        iva_texto = f"{iva_porcentaje:.1f} %"
        
        fila = self.tabla_model.rowCount()
        self.tabla_model.insertRow(fila)
        
        self.tabla_model.setItem(fila, 0, self._crear_item(cantidad, Qt.AlignCenter))
        self.tabla_model.setItem(fila, 1, self._crear_item(descripcion, Qt.AlignLeft | Qt.AlignVCenter))
        self.tabla_model.setItem(fila, 2, self._crear_item(precio_formateado, Qt.AlignCenter))
        self.tabla_model.setItem(fila, 3, self._crear_item(iva_texto, Qt.AlignCenter))
        self.tabla_model.setItem(fila, 4, self._crear_item(importe_formateado, Qt.AlignCenter))
        
        self.iva_por_fila[fila] = iva_porcentaje
        self.tipo_por_fila[fila] = 'normal'
        
        self.calcular_totales()
        self._limpiar_campos_item()
        self.tabla_items.selectRow(fila)
    
    def cargar_item_para_editar(self, index):
        fila = index.row()
        tipo_fila = self.tipo_por_fila.get(fila, 'normal')
        
        if tipo_fila in ['nota', 'seccion']:
            self.editar_nota_o_seccion(fila)
            return
        
        cantidad = self.tabla_model.index(fila, 0).data()
        descripcion = self.tabla_model.index(fila, 1).data()
        precio = self.tabla_model.index(fila, 2).data()
        
        precio = precio.replace("$", "").replace(",", "").strip()
        
        self.txt_cantidad.setText(cantidad)
        self.txt_descripcion.setText(descripcion)
        self.txt_precio.setText(precio)

        if fila in self.iva_por_fila:
            self.txt_impuestos.setValue(self.iva_por_fila[fila])
        else:
            self.txt_impuestos.setValue(16.0)
        
        self.fila_en_edicion = fila
        
        self.btn_agregar.setText("Actualizar")
        
        try:
            self.btn_agregar.clicked.disconnect()
        except TypeError:
            pass
        
        self.btn_agregar.clicked.connect(self.actualizar_item)
    
    def actualizar_item(self):
        if self.fila_en_edicion == -1:
            return
        
        if not self.validar_datos():
            return
        
        fila = self.fila_en_edicion
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        
        precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
        precio = float(precio_texto)
        precio_formateado = f"${precio:.2f}"
        
        cantidad_calculo = float(cantidad) if cantidad else 1
        importe = cantidad_calculo * precio
        importe_formateado = f"${importe:.2f}"
        
        iva_porcentaje = self.txt_impuestos.value()
        iva_texto = f"{iva_porcentaje:.1f} %"
        
        self.tabla_model.setItem(fila, 0, self._crear_item(cantidad, Qt.AlignCenter))
        self.tabla_model.setItem(fila, 1, self._crear_item(descripcion, Qt.AlignLeft | Qt.AlignVCenter))
        self.tabla_model.setItem(fila, 2, self._crear_item(precio_formateado, Qt.AlignCenter))
        self.tabla_model.setItem(fila, 3, self._crear_item(iva_texto, Qt.AlignCenter))
        self.tabla_model.setItem(fila, 4, self._crear_item(importe_formateado, Qt.AlignCenter))
        
        self.iva_por_fila[fila] = iva_porcentaje
        
        self.calcular_totales()
        self._limpiar_campos_item()
    
    def calcular_totales(self):
        subtotal = 0
        total_impuestos = 0
        
        for fila in range(self.tabla_model.rowCount()):
            tipo_fila = self.tipo_por_fila.get(fila, 'normal')
            if tipo_fila != 'normal':
                continue
                
            importe_item = self.tabla_model.item(fila, 4)
            if importe_item:
                importe_texto = importe_item.text()
                importe = float(importe_texto.replace("$", "").replace(",", "").strip())
                
                iva_porcentaje = self.iva_por_fila.get(fila, 16.0)
                iva_monto = importe * (iva_porcentaje / 100)
                
                subtotal += importe
                total_impuestos += iva_monto
        
        total = subtotal + total_impuestos
        
        self.lbl_subtotal_valor.setText(f"$ {subtotal:,.2f}")
        self.lbl_impuestos_valor.setText(f"$ {total_impuestos:,.2f}")
        self.lbl_total_valor.setText(f"$ {total:,.2f}")
    
    def mostrar_menu_contextual(self, position):
        indexes = self.tabla_items.selectedIndexes()
        menu = QMenu(self)
        
        menu.addSection("Insertar")
        action_nota = QAction("➕ Agregar Nota", self)
        action_nota.triggered.connect(self.insertar_nota)
        menu.addAction(action_nota)
        
        action_seccion = QAction("📁 Agregar Sección", self)
        action_seccion.triggered.connect(self.insertar_seccion)
        menu.addAction(action_seccion)
        
        menu.addSeparator()
        
        if indexes:
            fila = indexes[0].row()
            tipo_fila = self.tipo_por_fila.get(fila, 'normal')
            
            menu.addSection("Acciones")
            
            if tipo_fila in ['nota', 'seccion']:
                action_editar = QAction("✏️ Editar", self)
                action_editar.triggered.connect(lambda: self.editar_nota_o_seccion(fila))
                menu.addAction(action_editar)
                menu.addSeparator()
            
            es_primera_fila = (fila == 0)
            es_ultima_fila = (fila == self.tabla_model.rowCount() - 1)
            
            action_subir = QAction("Mover Arriba", self)
            action_subir.setEnabled(not es_primera_fila)
            action_subir.triggered.connect(lambda: self.mover_fila_arriba(fila))
            menu.addAction(action_subir)
            
            action_bajar = QAction("Mover Abajo", self)
            action_bajar.setEnabled(not es_ultima_fila)
            action_bajar.triggered.connect(lambda: self.mover_fila_abajo(fila))
            menu.addAction(action_bajar)
            
            menu.addSeparator()
            
            action_eliminar = QAction("Eliminar", self)
            action_eliminar.triggered.connect(lambda: self.eliminar_fila(fila))
            menu.addAction(action_eliminar)
        
        menu.exec_(self.tabla_items.viewport().mapToGlobal(position))
    
    def _insertar_fila_especial(self, texto, tipo, bg_color, fg_color, bold=False):
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

    def insertar_nota(self):
        texto, ok = QInputDialog.getText(
            self, "Agregar Nota", "Ingrese el texto de la nota:", QLineEdit.Normal, ""
        )
        if ok and texto:
            self._insertar_fila_especial(
                f"📝 {texto}", 'nota', 
                QColor(245, 245, 245), QColor(100, 100, 100)
            )
            self.calcular_totales()

    def insertar_seccion(self):
        texto, ok = QInputDialog.getText(
            self, "Agregar Sección", "Nombre de la sección:", QLineEdit.Normal, ""
        )
        if ok and texto:
            self._insertar_fila_especial(
                texto.upper(), 'seccion',
                QColor(0, 120, 142, 30), QColor(0, 120, 142), bold=True
            )
            self.calcular_totales()

    def editar_nota_o_seccion(self, fila):
        tipo = self.tipo_por_fila.get(fila, 'normal')
        if tipo == 'normal': return
        item_actual = self.tabla_model.item(fila, 0)
        if not item_actual: return
        texto_actual = item_actual.text()
        if tipo == 'nota':
            texto_actual = texto_actual.replace("📝 ", "")
            titulo = "Editar Nota"
            mensaje = "Modifique el texto de la nota:"
        else:
            titulo = "Editar Sección"
            mensaje = "Modifique el nombre de la sección:"
        texto_nuevo, ok = QInputDialog.getText(
            self, titulo, mensaje, QLineEdit.Normal, texto_actual
        )
        if ok and texto_nuevo:
            if tipo == 'nota':
                item_actual.setText(f"📝 {texto_nuevo}")
                item_actual.setBackground(QColor(245, 245, 245))
                item_actual.setForeground(QColor(100, 100, 100))
            else:
                item_actual.setText(texto_nuevo.upper())
                item_actual.setBackground(QColor(0, 120, 142, 30))
                item_actual.setForeground(QColor(0, 120, 142))
                font = item_actual.font(); font.setBold(True); font.setPointSize(10)
                item_actual.setFont(font)
    
    def mover_fila_arriba(self, fila):
        if fila <= 0: return
        self.intercambiar_filas(fila, fila - 1)
        self.tabla_items.selectRow(fila - 1)
    
    def mover_fila_abajo(self, fila):
        if fila >= self.tabla_model.rowCount() - 1: return
        self.intercambiar_filas(fila, fila + 1)
        self.tabla_items.selectRow(fila + 1)
    
    def intercambiar_filas(self, fila1, fila2):
        items1 = [self.tabla_model.takeItem(fila1, col) for col in range(self.tabla_model.columnCount())]
        items2 = [self.tabla_model.takeItem(fila2, col) for col in range(self.tabla_model.columnCount())]
        
        for col, item in enumerate(items2):
            self.tabla_model.setItem(fila1, col, item)
        for col, item in enumerate(items1):
            self.tabla_model.setItem(fila2, col, item)

        tipo1 = self.tipo_por_fila.get(fila1, 'normal')
        self.tipo_por_fila[fila1] = self.tipo_por_fila.get(fila2, 'normal')
        self.tipo_por_fila[fila2] = tipo1
        
        iva1 = self.iva_por_fila.get(fila1, 16.0)
        self.iva_por_fila[fila1] = self.iva_por_fila.get(fila2, 16.0)
        self.iva_por_fila[fila2] = iva1

        for fila in [fila1, fila2]:
            if self.tipo_por_fila.get(fila, 'normal') in ['nota', 'seccion']:
                self.tabla_items.setSpan(fila, 0, 1, 5)
            else:
                self.tabla_items.setSpan(fila, 0, 1, 1)
                for col in range(1, 5):
                    self.tabla_items.setSpan(fila, col, 1, 1)
    
    def eliminar_fila(self, fila):
        respuesta = QMessageBox.question(
            self, 'Confirmar', '¿Eliminar este item?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            self.tabla_model.removeRow(fila)
            
            nuevo_iva = {}
            nuevo_tipo = {}
            for key in range(self.tabla_model.rowCount()):
                if key < fila:
                    nuevo_iva[key] = self.iva_por_fila.get(key, 16.0)
                    nuevo_tipo[key] = self.tipo_por_fila.get(key, 'normal')
                else:
                    nuevo_iva[key] = self.iva_por_fila.get(key + 1, 16.0)
                    nuevo_tipo[key] = self.tipo_por_fila.get(key + 1, 'normal')
            
            self.iva_por_fila = nuevo_iva
            self.tipo_por_fila = nuevo_tipo
            
            self.calcular_totales()
            if fila == self.fila_en_edicion:
                self._limpiar_campos_item()

    def editar_nota(self):
        if not self.nota_actual_id:
            self.mostrar_advertencia("No hay una nota cargada para editar")
            return
        if self.txt_estado.text() == 'Cancelada':
            self.mostrar_advertencia("No se puede editar una nota cancelada.")
            return            
        self.modo_edicion = True
        self.controlar_estado_campos(True)
        if hasattr(self, 'botones') and len(self.botones) > 1:
            self.botones[1].setText("Actualizar")
        self.mostrar_exito("Modo edición activado")
    
    def controlar_estado_campos(self, habilitar):
        if hasattr(self, 'txt_proveedor'):
            self.txt_proveedor.setReadOnly(not habilitar)
        if hasattr(self, 'date_fecha'):
            self.date_fecha.setEnabled(habilitar)
        if hasattr(self, 'txt_referencia'):
            self.txt_referencia.setReadOnly(not habilitar)
        if hasattr(self, 'cmb_producto'):
            self.cmb_producto.setEnabled(habilitar)
        if hasattr(self, 'txt_cantidad'):
            self.txt_cantidad.setReadOnly(not habilitar)
        if hasattr(self, 'txt_descripcion'):
            self.txt_descripcion.setReadOnly(not habilitar)
        if hasattr(self, 'txt_precio'):
            self.txt_precio.setReadOnly(not habilitar)
        if hasattr(self, 'btn_agregar'):
            self.btn_agregar.setEnabled(habilitar)
        
        if hasattr(self, 'botones'):
            self.botones[0].setEnabled(True) 
            self.botones[1].setEnabled(habilitar) 
            self.botones[2].setEnabled(self.nota_actual_id is not None and not habilitar) 
            self.botones[3].setEnabled(True) 
            self.botones[4].setEnabled(self.nota_actual_id is not None and not habilitar) 
            self.botones[5].setEnabled(True) 
            self.botones[6].setEnabled(self.nota_actual_id is not None) 

        if hasattr(self, 'tabla_items'):
            if habilitar:
                self.tabla_items.setEditTriggers(QTableView.DoubleClicked)
            else:
                self.tabla_items.setEditTriggers(QTableView.NoEditTriggers)
    
    def abrir_ventana_pagos(self):
        if PagosNotaProveedorDialog is None:
            self.mostrar_error("Error Crítico: No se pudo cargar el módulo de pagos (PagosNotaProveedorDialog).")
            return
            
        dialog = PagosNotaProveedorDialog(self)
        
        if self.nota_actual_id:
            try:
                nota_para_pago = db_helper.get_nota_proveedor(self.nota_actual_id)
                if nota_para_pago:
                    dialog.cargar_nota(nota_para_pago)
                else:
                    self.mostrar_advertencia(f"No se encontró la nota ID {self.nota_actual_id} para cargar pagos.")
            except Exception as e:
                self.mostrar_error(f"No se pudo cargar la nota para pagos: {e}")
                
        dialog.exec_()
        
        if self.nota_actual_id:
            try:
                nota_actualizada = db_helper.get_nota_proveedor(self.nota_actual_id)
                if nota_actualizada:
                    self.cargar_nota_en_formulario(nota_actualizada)
            except Exception as e:
                self.mostrar_error(f"No se pudo recargar la nota: {e}")
    
    def validar_datos(self):
        cantidad_texto = self.txt_cantidad.text().strip()
        if not cantidad_texto:
             self.mostrar_advertencia("Ingrese una cantidad.")
             return False
        try:
             if float(cantidad_texto) <= 0:
                 self.mostrar_advertencia("La cantidad debe ser mayor a 0.")
                 return False
        except ValueError:
             self.mostrar_advertencia("Ingrese una cantidad numérica válida.")
             return False

        if not self.txt_descripcion.text():
            self.mostrar_advertencia("Ingrese una descripción.")
            return False
        
        precio_texto = self.txt_precio.text().replace("$", "").replace(",", "").strip()
        if not precio_texto:
            self.mostrar_advertencia("Ingrese un precio.")
            return False
        try:
            if float(precio_texto) <= 0:
                 self.mostrar_advertencia("El precio debe ser mayor a 0.")
                 return False
        except ValueError:
             self.mostrar_advertencia("Ingrese un precio numérico válido.")
             return False
        
        return True
    
    def _limpiar_campos_item(self):
            self.txt_cantidad.setText("")
            self.txt_descripcion.setText("")
            self.txt_precio.setText("")
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
    
    def _mostrar_mensaje(self, icono, titulo, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(icono)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(MESSAGE_BOX_STYLE)
        msg.exec_()

    def mostrar_advertencia(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Warning, "Advertencia", mensaje)
    
    def mostrar_error(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Critical, "Error", mensaje)
    
    def mostrar_exito(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Information, "Éxito", mensaje)
    
    def _obtener_estilo_calendario(self):
        return """
            QDateEdit {
                padding: 8px;
                border: 2px solid #F5F5F5;
                border-radius: 6px;
                background-color: #F5F5F5;
                min-height: 25px;
                font-size: 16px;
                margin-top: 0px;
            }
            QDateEdit:focus {
                border: 2px solid #2CD5C4;
                background-color: white;
            }
            QDateEdit::drop-down {
                border: 0px;
                background: transparent;
                subcontrol-position: right center;
                width: 30px;
            }
            QDateEdit::down-arrow {
                image: url(assets/icons/calendario.png);
                width: 16px;
                height: 16px;
            }
            QCalendarWidget {
                background-color: white;
                border: 2px solid #00788E;
                border-radius: 8px;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #00788E;
                border: none;
                border-radius: 4px;
                margin: 2px;
                padding: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #2CD5C4;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #00788E;
            }
            QCalendarWidget QAbstractItemView {
                selection-background-color: #2CD5C4;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #00788E;
            }
        """

    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        from gui.api_client import api_client as db_helper
    except ImportError:
        print("Error: No se pudo importar api_client. Asegúrate de que el servidor esté corriendo.")
        sys.exit(1)
    window = NotasProveedoresWindow()
    window.show()
    sys.exit(app.exec_())
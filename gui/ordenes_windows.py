import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QSizePolicy, QApplication,
    QLabel, QLineEdit, QGridLayout, QGroupBox,
    QMessageBox, QTableView, QHeaderView,
    QMenu, QAction, QFrame, QWidget, QDateEdit,
    QComboBox,
    QInputDialog,
    QCompleter, QFileDialog
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QFont

# Import styles
from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2,
    GROUP_BOX_STYLE, LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, FORM_BUTTON_STYLE, MESSAGE_BOX_STYLE
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gui.api_client import api_client as db_helper
    from gui.websocket_client import ws_client

except ImportError:
    print("Error: No se pudo importar 'api_client' o 'ws_client'.") 
    db_helper = None 

try:
    from dialogs.buscar_ordenes_dialog import BuscarOrdenesDialog
except ImportError as e:
    print(f"Error al importar BuscarOrdenesDialog: {e}")
    BuscarOrdenesDialog = None

try:
    # Importamos la NUEVA función que acabamos de crear
    from gui.pdf_generador import generar_pdf_orden_trabajo
except ImportError as e:
    print(f"Advertencia: No se pudo cargar pdf_generator (orden): {e}")
    generar_pdf_orden_trabajo = None

class OrdenesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Órdenes de Trabajo")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self.setMinimumSize(800, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        # Variables de control de UI
        self.fila_en_edicion = -1
        self.tipo_por_fila = {}  # 'normal', 'nota', 'seccion'

        # Variables de control de Lógica/BD
        self.orden_actual_id = None
        self.orden_actual_obj = None
        self.modo_edicion = False
        self.clientes_dict = {}
        self._datos_cargados = False

        self.setup_ui()
        self.conectar_senales()
        
        if ws_client:
            ws_client.cliente_creado.connect(self.on_notificacion_cliente)
            ws_client.cliente_actualizado.connect(self.on_notificacion_cliente)
            ws_client.orden_creada.connect(self.on_notificacion_orden) 
        
        self.nueva_orden()
        
        QTimer.singleShot(100, self._cargar_datos_inicial)
    
    def _cargar_datos_inicial(self):
        if not self._datos_cargados:
            self.cargar_clientes_bd()
            self._datos_cargados = True

    def on_notificacion_cliente(self, data):
        self.cargar_clientes_bd()

    def on_notificacion_orden(self, data):
        if self.orden_actual_id and data.get('id') == self.orden_actual_id:
            print(f"Recargando orden {self.orden_actual_id} por notificación remota.")
            try:
                orden_actualizada = db_helper.get_orden(self.orden_actual_id)
                if orden_actualizada:
                    self.cargar_orden_en_formulario(orden_actualizada)
                else:
                    self.nueva_orden()
                    self.mostrar_advertencia("La orden que estaba viendo fue eliminada remotamente.")
            except Exception as e:
                print(f"Error recargando orden: {e}")
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.crear_grupo_orden(main_layout)
        self.crear_grupo_vehiculo(main_layout)
        self.crear_grupo_servicio(main_layout)
        self.crear_tabla_items(main_layout)
        
        main_layout.addStretch(1)
        self.crear_botones(main_layout)

        self.setLayout(main_layout)

    def crear_grupo_orden(self, parent_layout):
        grupo_orden = QGroupBox("")
        grupo_orden.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        lbl_folio = QLabel("Folio Orden")
        lbl_folio.setStyleSheet(LABEL_STYLE)
        self.txt_folio = QLineEdit()
        self.txt_folio.setStyleSheet(INPUT_STYLE + "QLineEdit { background-color: #E8E8E8; color: #666666; }")
        self.txt_folio.setReadOnly(True)
        self.txt_folio.setPlaceholderText("ORD-Auto")
        
        lbl_cliente = QLabel("Cliente")
        lbl_cliente.setStyleSheet(LABEL_STYLE)
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setStyleSheet(INPUT_STYLE)
        self.txt_cliente.setPlaceholderText("Escriba para buscar cliente...")
        
        lbl_fecha = QLabel("Fecha")
        lbl_fecha.setStyleSheet(LABEL_STYLE)
        self.date_fecha = QDateEdit()
        self.date_fecha.setCalendarPopup(True)
        self.date_fecha.setDate(QDate.currentDate())
        self.date_fecha.setDisplayFormat("dd/MM/yyyy")
        self.date_fecha.setStyleSheet(self._obtener_estilo_calendario())
        
        lbl_estado = QLabel("Estado")
        lbl_estado.setStyleSheet(LABEL_STYLE)
        self.cmb_estado = QComboBox()
        self.cmb_estado.setStyleSheet(INPUT_STYLE)
        self.cmb_estado.addItems(["Pendiente", "En Proceso", "Completada", "Cancelada", "Facturada"])
        
        layout.addWidget(lbl_folio)
        layout.addWidget(self.txt_folio, 1)
        layout.addWidget(lbl_cliente)
        layout.addWidget(self.txt_cliente, 2)
        layout.addWidget(lbl_fecha)
        layout.addWidget(self.date_fecha, 1)
        layout.addWidget(lbl_estado)
        layout.addWidget(self.cmb_estado, 1)
        
        grupo_orden.setLayout(layout)
        parent_layout.addWidget(grupo_orden)
    
    def crear_grupo_vehiculo(self, parent_layout):
        grupo_vehiculo = QGroupBox("")
        grupo_vehiculo.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QGridLayout()
        layout.setVerticalSpacing(8)
        layout.setHorizontalSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        campos = [
            ("Marca", "txt_marca", "Marca del vehículo"),
            ("Modelo", "txt_modelo", "Modelo del vehículo"),
            ("Año", "txt_ano", "Año"),
            ("Placa", "txt_placa", "Placa del vehículo")
        ]
        
        for i, (texto, nombre_campo, placeholder) in enumerate(campos):
            label = QLabel(texto)
            label.setStyleSheet(LABEL_STYLE)
            layout.addWidget(label, 0, i)
            
            campo = QLineEdit()
            campo.setStyleSheet(INPUT_STYLE)
            campo.setPlaceholderText(placeholder)
            setattr(self, nombre_campo, campo)
            layout.addWidget(campo, 1, i)
        
        grupo_vehiculo.setLayout(layout)
        parent_layout.addWidget(grupo_vehiculo)

    def crear_grupo_servicio(self, parent_layout):
        grupo = QGroupBox("")
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(8)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 8)
        grid_layout.setColumnStretch(2, 1)
        
        lbl_cantidad = QLabel("Cantidad")
        lbl_cantidad.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_cantidad, 0, 0)
        
        lbl_descripcion = QLabel("Descripción del Servicio/Trabajo")
        lbl_descripcion.setStyleSheet(LABEL_STYLE)
        grid_layout.addWidget(lbl_descripcion, 0, 1)
        
        self.txt_cantidad = QLineEdit()
        self.txt_cantidad.setStyleSheet(INPUT_STYLE)
        self.txt_cantidad.setPlaceholderText("Cant.")
        grid_layout.addWidget(self.txt_cantidad, 1, 0)
        
        self.txt_descripcion = QLineEdit()
        self.txt_descripcion.setStyleSheet(INPUT_STYLE)
        self.txt_descripcion.setPlaceholderText("Descripción del trabajo a realizar")
        grid_layout.addWidget(self.txt_descripcion, 1, 1)
        
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setStyleSheet(FORM_BUTTON_STYLE)
        self.btn_agregar.setCursor(Qt.PointingHandCursor)
        grid_layout.addWidget(self.btn_agregar, 1, 2)
        
        grupo.setLayout(grid_layout)
        parent_layout.addWidget(grupo)
    
    def crear_tabla_items(self, parent_layout):
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels(["Cantidad", "Descripción del Trabajo/Servicio"])
        
        self.tabla_items = QTableView()
        self.tabla_items.setModel(self.tabla_model)
        self.tabla_items.horizontalHeader().setVisible(True)
        self.tabla_items.verticalHeader().setVisible(False)
        self.tabla_items.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_items.setStyleSheet(TABLE_STYLE)
        
        header = self.tabla_items.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setFixedHeight(40)
        
        self.tabla_items.verticalHeader().setDefaultSectionSize(30)
        self.tabla_items.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_items.setSelectionMode(QTableView.SingleSelection)
        
        self.tabla_items.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_items.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        
        self.tabla_items.setMinimumHeight(15 * 30 + 40)
        parent_layout.addWidget(self.tabla_items)

    def crear_botones(self, parent_layout):
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)
        
        textos_botones = [
            "Nueva", "Guardar", "Cancelar", "Buscar", "Editar", "Limpiar", "Imprimir", 
            "Mostrar Órdenes", "Generar Nota"
        ]
        
        self.botones = []
        
        for texto in textos_botones:
            boton = QPushButton(texto)
            boton.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            boton.setCursor(Qt.PointingHandCursor)
            boton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            botones_layout.addWidget(boton)
            self.botones.append(boton)
        
        self.btn_nueva = self.botones[0]
        self.btn_guardar = self.botones[1]
        self.btn_cancelar = self.botones[2]
        self.btn_buscar = self.botones[3]
        self.btn_editar = self.botones[4]
        self.btn_limpiar = self.botones[5]
        self.btn_imprimir = self.botones[6]
        self.btn_mostrar_ordenes = self.botones[7] 
        self.btn_generar_nota = self.botones[8] 
        
        parent_layout.addLayout(botones_layout)

    def _obtener_estilo_calendario(self):
        return """
            QDateEdit {
                padding: 8px;
                border: 2px solid #F5F5F5;
                border-radius: 6px;
                background-color: #F5F5F5;
                min-height: 25px;
                font-size: 16px;
            }
            QDateEdit:focus {
                border: 2px solid #2CD5C4;
                background-color: white;
            }
            QDateEdit::drop-down {
                border: 0px;
                background: transparent;
                width: 30px;
            }
            QDateEdit::down-arrow {
                image: url(assets/icons/calendario.png);
                width: 16px;
                height: 16px;
            }
        """

    def conectar_senales(self):
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        self.tabla_items.doubleClicked.connect(self.cargar_item_para_editar)

        self.btn_nueva.clicked.connect(self.nueva_orden)
        self.btn_guardar.clicked.connect(self.guardar_orden)
        self.btn_cancelar.clicked.connect(self.cancelar_orden)
        self.btn_buscar.clicked.connect(self.buscar_orden)
        self.btn_editar.clicked.connect(self.habilitar_edicion)
        self.btn_limpiar.clicked.connect(self.nueva_orden) 
        self.btn_imprimir.clicked.connect(self.imprimir_orden)
        self.btn_mostrar_ordenes.clicked.connect(self.abrir_ventana_ordenes)
        self.btn_generar_nota.clicked.connect(self.generar_nota_desde_orden)

    # ==================================================
    # LÓGICA DE BASE DE DATOS Y ESTADO
    # ==================================================

    def abrir_ventana_ordenes(self):
        if BuscarOrdenesDialog is None:
            self.mostrar_error("Error Crítico: No se pudo cargar el módulo de 'BuscarOrdenesDialog'.")
            return
            
        dialog = BuscarOrdenesDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.orden_seleccionada:
            self.cargar_orden_en_formulario(dialog.orden_seleccionada)
            estado = dialog.orden_seleccionada.get('estado')
            if estado == 'Cancelada':
                self.mostrar_advertencia("Esta orden está cancelada y no puede ser editada o convertida a nota.")
            elif estado == 'Facturada' or dialog.orden_seleccionada.get('nota_folio'):
                self.mostrar_advertencia("Esta orden ya fue facturada y/o convertida a nota. Solo puede ser consultada.")

    def nueva_orden(self):
        self.orden_actual_id = None
        self.orden_actual_obj = None
        self.modo_edicion = True
        self.fila_en_edicion = -1
        self.tipo_por_fila.clear()
        
        self.txt_folio.clear()
        self.txt_cliente.clear()
        self.txt_marca.clear()
        self.txt_modelo.clear()
        self.txt_ano.clear()
        self.txt_placa.clear()
        
        self._limpiar_campos_item()
        
        self.cmb_estado.setCurrentText("Pendiente")
        self.date_fecha.setDate(QDate.currentDate())
        self.tabla_model.removeRows(0, self.tabla_model.rowCount())
        
        self.controlar_estado_campos(True)
        self.btn_agregar.setText("Agregar")
        
        self.btn_guardar.setText("Guardar")

    def cargar_clientes_bd(self):
        if not db_helper: return
        
        try:
            clientes = db_helper.get_clientes()
            self.clientes_dict.clear()
            nombres_clientes = []
            
            for cliente in clientes:
                nombre_completo = f"{cliente['nombre']} - {cliente['tipo']}"
                nombres_clientes.append(nombre_completo)
                self.clientes_dict[nombre_completo] = cliente['id']
            
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
            
            self.txt_cliente.setCompleter(completer)
            
        except Exception as e:
            self.mostrar_error(f"Error al cargar clientes: {e}")

    def guardar_orden(self):
        if not db_helper: 
            self.mostrar_error("No hay conexión a la base de datos.")
            return

        if not self.validar_datos_orden():
            return
        
        nombre_cliente = self.txt_cliente.text()
        cliente_id = self.clientes_dict.get(nombre_cliente, None)
        
        if not cliente_id:
            self.mostrar_advertencia("Seleccione un cliente válido.")
            return
        
        items_a_guardar = []
        for fila in range(self.tabla_model.rowCount()):
            tipo = self.tipo_por_fila.get(fila, 'normal')
            
            if tipo == 'normal':
                try:
                    cantidad_str = self.tabla_model.item(fila, 0).text()
                    cantidad = int(float(cantidad_str))
                    
                    if cantidad <= 0:
                        raise ValueError()
                        
                    items_a_guardar.append({
                        'cantidad': cantidad,
                        'descripcion': self.tabla_model.item(fila, 1).text()
                    })
                except (ValueError, AttributeError):
                    self.mostrar_error(f"Error en la cantidad de la fila {fila+1}.")
                    return

        if not items_a_guardar:
            self.mostrar_advertencia("Agregue al menos un servicio.")
            return
        
        orden_data = {
            'cliente_id': cliente_id,
            'vehiculo_marca': self.txt_marca.text(),
            'vehiculo_modelo': self.txt_modelo.text(),
            'vehiculo_ano': self.txt_ano.text(),
            'vehiculo_placas': self.txt_placa.text(),
            'estado': self.cmb_estado.currentText(),
            'fecha_recepcion': self.date_fecha.date().toPyDate().isoformat()
        }
        
        try:
            if self.orden_actual_id:
                orden = db_helper.actualizar_orden(self.orden_actual_id, orden_data, items_a_guardar)
                if not orden:
                    raise Exception("La API no devolvió la orden actualizada.")

                self.mostrar_exito("Orden actualizada")
                self.orden_actual_obj = orden
            else:
                orden = db_helper.crear_orden(orden_data, items_a_guardar)
                if not orden:
                    raise Exception("La API no devolvió la orden creada.")

                self.mostrar_exito("Orden guardada")
                self.orden_actual_id = orden['id']
                self.orden_actual_obj = orden
            
            self.nueva_orden() 
            
        except Exception as e:
            self.mostrar_error(f"Error al guardar: {e}")

    def buscar_orden(self):
        if not db_helper: 
            return
        
        folio, ok = QInputDialog.getText(self, "Buscar Orden", "Ingrese el folio (ej: ORD-2025-0001):")
        if ok and folio:
            try:
                ordenes = db_helper.buscar_ordenes(folio=folio.strip())
                
                if ordenes:
                    self.cargar_orden_en_formulario(ordenes[0])
                    if len(ordenes) > 1:
                        self.mostrar_info(f"Se encontraron {len(ordenes)} órdenes. Mostrando la primera.")
                else:
                    self.mostrar_advertencia("Orden no encontrada.")
            except Exception as e:
                self.mostrar_error(f"Error al buscar: {e}")

    def cargar_orden_en_formulario(self, orden):
        self.orden_actual_id = orden['id']
        self.orden_actual_obj = orden
        self.modo_edicion = False
        self.tipo_por_fila.clear()
        
        self.txt_folio.setText(orden['folio'])
        self.txt_marca.setText(orden['vehiculo_marca'])
        self.txt_modelo.setText(orden['vehiculo_modelo'])
        self.txt_ano.setText(str(orden['vehiculo_ano']))
        self.txt_placa.setText(orden['vehiculo_placas'])
        self.cmb_estado.setCurrentText(orden['estado'])
        
        try:
            fecha_dt = orden['fecha_recepcion']
            if isinstance(fecha_dt, str):
                fecha_dt = datetime.fromisoformat(fecha_dt)
            
            if fecha_dt:
                self.date_fecha.setDate(QDate(fecha_dt.year, fecha_dt.month, fecha_dt.day))
            else:
                self.date_fecha.setDate(QDate.currentDate())
        except Exception as e:
            print(f"Error al parsear fecha: {e}. Usando fecha actual.")
            self.date_fecha.setDate(QDate.currentDate())

        self.txt_cliente.clear()
        for nombre, id_cliente in self.clientes_dict.items():
            if id_cliente == orden['cliente_id']:
                self.txt_cliente.setText(nombre)
                break
        
        self.tabla_model.removeRows(0, self.tabla_model.rowCount())
        for item in orden['items']:
            fila = self.tabla_model.rowCount()
            self.tabla_model.insertRow(fila)
            self.tabla_model.setItem(fila, 0, self._crear_item(str(item['cantidad']), Qt.AlignCenter))
            self.tabla_model.setItem(fila, 1, self._crear_item(item['descripcion'], Qt.AlignLeft | Qt.AlignVCenter))
            self.tipo_por_fila[fila] = 'normal'
        
        self.controlar_estado_campos(False)

    def habilitar_edicion(self):
        if not self.orden_actual_id:
            self.mostrar_advertencia("No hay orden cargada.")
            return
        
        if self.orden_actual_obj and self.orden_actual_obj.get('nota_folio'):
            self.mostrar_advertencia(f"Esta orden ya generó la nota {self.orden_actual_obj['nota_folio']} y no puede ser modificada.")
            return

        if self.orden_actual_obj and self.orden_actual_obj.get('estado') == 'Cancelada':
            self.mostrar_advertencia("No se puede editar una orden que ya está cancelada.")
            return
        
        self.modo_edicion = True
        self.controlar_estado_campos(True)
        self.mostrar_info("Modo edición activado.")
        
        self.btn_guardar.setText("Actualizar")

    def cancelar_orden(self):
        if not self.orden_actual_id:
            self.mostrar_advertencia("No hay orden cargada.")
            return
        
        if self.orden_actual_obj and self.orden_actual_obj.get('estado') == 'Cancelada':
            self.mostrar_advertencia("Esta orden ya se encuentra cancelada.")
            return
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            "¿Cancelar esta orden?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                orden_cancelada = db_helper.cancelar_orden(self.orden_actual_id)
                if orden_cancelada:
                    self.mostrar_exito("Orden cancelada.")
                    self.nueva_orden()
                else:
                    self.mostrar_error("No se pudo cancelar la orden.")

            except Exception as e:
                self.mostrar_error(f"Error al cancelar: {e}")

    def controlar_estado_campos(self, habilitar):
        self.txt_cliente.setReadOnly(not habilitar)
        self.date_fecha.setEnabled(habilitar)
        self.cmb_estado.setEnabled(habilitar)
        
        self.txt_marca.setReadOnly(not habilitar)
        self.txt_modelo.setReadOnly(not habilitar)
        self.txt_ano.setReadOnly(not habilitar)
        self.txt_placa.setReadOnly(not habilitar)
        
        self.txt_cantidad.setReadOnly(not habilitar)
        self.txt_descripcion.setReadOnly(not habilitar)
        
        self.btn_agregar.setEnabled(habilitar)
        self.btn_guardar.setEnabled(habilitar)
        
        orden_cargada = self.orden_actual_obj is not None
        nota_generada = False
        esta_cancelada = False
        
        if orden_cargada:
            nota_generada = bool(self.orden_actual_obj.get('nota_folio'))
            esta_cancelada = (self.orden_actual_obj.get('estado') == 'Cancelada')

        puede_modificar = orden_cargada and not habilitar and not nota_generada and not esta_cancelada

        self.btn_editar.setEnabled(puede_modificar)
        self.btn_cancelar.setEnabled(puede_modificar)
        self.btn_generar_nota.setEnabled(puede_modificar)
        self.btn_mostrar_ordenes.setEnabled(True)
        
        tooltip = ""
        if nota_generada:
            tooltip = f"Nota ya generada: {self.orden_actual_obj.get('nota_folio')}"
        elif esta_cancelada:
            tooltip = "La orden está cancelada y no puede ser modificada"
        
        if nota_generada or esta_cancelada:
            self.btn_editar.setToolTip(tooltip)
            self.btn_cancelar.setToolTip(tooltip)
            self.btn_generar_nota.setToolTip(tooltip)
        else:
            self.btn_editar.setToolTip("Habilitar edición para esta orden")
            self.btn_cancelar.setToolTip("Cancelar esta orden")
            self.btn_generar_nota.setToolTip("Generar Nota de Venta a partir de esta orden")

    # ==================================================
    # LÓGICA DE LA TABLA (Notas, Secciones, Items)
    # ==================================================

    def _crear_item(self, texto, alineacion):
        item = QStandardItem(texto)
        item.setTextAlignment(alineacion)
        return item

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
        self.tabla_items.setSpan(fila, 0, 1, 2)
        self.tipo_por_fila[fila] = tipo

    def mostrar_menu_contextual(self, position):
        menu = QMenu(self)
        indexes = self.tabla_items.selectedIndexes()
        
        if not self.modo_edicion:
            action_info = QAction("Presione 'Editar' para modificar", self)
            action_info.setEnabled(False)
            menu.addAction(action_info)
            menu.exec_(self.tabla_items.viewport().mapToGlobal(position))
            return

        menu.addSection("Insertar")
        action_nota = QAction("➕ Agregar Nota", self)
        action_nota.triggered.connect(self.insertar_nota)
        menu.addAction(action_nota)
        
        action_seccion = QAction("📁 Agregar Sección", self)
        action_seccion.triggered.connect(self.insertar_seccion)
        menu.addAction(action_seccion)
        
        if indexes:
            fila = indexes[0].row()
            tipo_fila = self.tipo_por_fila.get(fila, 'normal')
            
            menu.addSeparator()
            menu.addSection("Acciones")
            
            if tipo_fila in ['nota', 'seccion']:
                action_editar = QAction("✏️ Editar", self)
                action_editar.triggered.connect(lambda: self.editar_elemento_especial(fila))
                menu.addAction(action_editar)
                menu.addSeparator()
            
            action_subir = QAction("Mover Arriba", self)
            action_subir.setEnabled(fila > 0)
            action_subir.triggered.connect(lambda: self.mover_fila_arriba(fila))
            menu.addAction(action_subir)
            
            action_bajar = QAction("Mover Abajo", self)
            action_bajar.setEnabled(fila < self.tabla_model.rowCount() - 1)
            action_bajar.triggered.connect(lambda: self.mover_fila_abajo(fila))
            menu.addAction(action_bajar)
            
            menu.addSeparator()
            action_eliminar = QAction("Eliminar", self)
            action_eliminar.triggered.connect(lambda: self.eliminar_fila(fila))
            menu.addAction(action_eliminar)
        
        menu.exec_(self.tabla_items.viewport().mapToGlobal(position))

    def insertar_nota(self):
        texto, ok = QInputDialog.getText(self, "Agregar Nota", "Texto de la nota:")
        if ok and texto:
            self._insertar_fila_especial(
                f"📝 {texto}", 'nota', 
                QColor(245, 245, 245), QColor(100, 100, 100)
            )
            self._actualizar_mapa_tipos()

    def insertar_seccion(self):
        texto, ok = QInputDialog.getText(self, "Agregar Sección", "Nombre de la sección:")
        if ok and texto:
            self._insertar_fila_especial(
                texto.upper(), 'seccion',
                QColor(0, 120, 142, 30), QColor(0, 120, 142), bold=True
            )
            self._actualizar_mapa_tipos()

    def editar_elemento_especial(self, fila):
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
        
        texto_nuevo, ok = QInputDialog.getText(self, titulo, mensaje, QLineEdit.Normal, texto_actual)
        
        if ok and texto_nuevo:
            if tipo == 'nota':
                item_actual.setText(f"📝 {texto_nuevo}")
                item_actual.setBackground(QColor(245, 245, 245))
                item_actual.setForeground(QColor(100, 100, 100))
            else:
                item_actual.setText(texto_nuevo.upper())
                item_actual.setBackground(QColor(0, 120, 142, 30))
                item_actual.setForeground(QColor(0, 120, 142))
                font = item_actual.font()
                font.setBold(True)
                font.setPointSize(10)
                item_actual.setFont(font)

    def mover_fila_arriba(self, fila):
        if fila <= 0: return
        self._intercambiar_filas(fila, fila - 1)
        self.tabla_items.selectRow(fila - 1)

    def mover_fila_abajo(self, fila):
        if fila >= self.tabla_model.rowCount() - 1: return
        self._intercambiar_filas(fila, fila + 1)
        self.tabla_items.selectRow(fila + 1)

    def _intercambiar_filas(self, fila1, fila2):
        for col in range(self.tabla_model.columnCount()):
            item1 = self.tabla_model.takeItem(fila1, col)
            item2 = self.tabla_model.takeItem(fila2, col)
            self.tabla_model.setItem(fila1, col, item2)
            self.tabla_model.setItem(fila2, col, item1)
        
        self._actualizar_mapa_tipos()
        
        for fila in [fila1, fila2]:
            if self.tipo_por_fila.get(fila, 'normal') in ['nota', 'seccion']:
                self.tabla_items.setSpan(fila, 0, 1, 2)
            else:
                self.tabla_items.setSpan(fila, 0, 1, 1)

    def eliminar_fila(self, fila):
        msg_box = QMessageBox(QMessageBox.Question, "Confirmar eliminación", 
            "¿Está seguro de eliminar este elemento?", QMessageBox.Yes | QMessageBox.No, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        
        if msg_box.exec_() == QMessageBox.Yes:
            self.tabla_model.removeRow(fila)
            self._actualizar_mapa_tipos()
            if fila == self.fila_en_edicion:
                self._limpiar_campos_item()

    def _actualizar_mapa_tipos(self):
        tipos_actuales = list(self.tipo_por_fila.items())
        tipos_actuales.sort()
        self.tipo_por_fila.clear()
        
        for fila_modelo in range(self.tabla_model.rowCount()):
            tipo_encontrado = 'normal'
            item_cero = self.tabla_model.item(fila_modelo, 0)
            if item_cero:
                texto = item_cero.text()
                if texto.startswith("📝 "):
                    tipo_encontrado = 'nota'
                elif item_cero.font().bold() and item_cero.foreground().color() == QColor(0, 120, 142):
                    tipo_encontrado = 'seccion'
            self.tipo_por_fila[fila_modelo] = tipo_encontrado

    def agregar_a_tabla(self):
        if not self.validar_item_formulario():
            return
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()
        
        fila = self.tabla_model.rowCount()
        self.tabla_model.insertRow(fila)
        self.tabla_model.setItem(fila, 0, self._crear_item(cantidad, Qt.AlignCenter))
        self.tabla_model.setItem(fila, 1, self._crear_item(descripcion, Qt.AlignLeft | Qt.AlignVCenter))
        self.tipo_por_fila[fila] = 'normal'
        
        self._limpiar_campos_item()
        self.tabla_items.selectRow(fila)

    def cargar_item_para_editar(self, index):
        if not self.modo_edicion:
            self.mostrar_info("Presione 'Editar' para modificar una orden guardada.")
            return
            
        fila = index.row()
        tipo_fila = self.tipo_por_fila.get(fila, 'normal')
        
        if tipo_fila in ['nota', 'seccion']:
            self.editar_elemento_especial(fila)
            return
        
        cantidad = self.tabla_model.index(fila, 0).data()
        descripcion = self.tabla_model.index(fila, 1).data()
        
        self.txt_cantidad.setText(cantidad)
        self.txt_descripcion.setText(descripcion)
        
        self.fila_en_edicion = fila
        self.btn_agregar.setText("Actualizar")
        
        try: self.btn_agregar.clicked.disconnect()
        except TypeError: pass
        self.btn_agregar.clicked.connect(self.actualizar_item)

    def actualizar_item(self):
        if not self.validar_item_formulario():
            return
        
        cantidad = self.txt_cantidad.text()
        descripcion = self.txt_descripcion.text()

        self.tabla_model.setItem(self.fila_en_edicion, 0, self._crear_item(cantidad, Qt.AlignCenter))
        self.tabla_model.setItem(self.fila_en_edicion, 1, self._crear_item(descripcion, Qt.AlignLeft | Qt.AlignVCenter))
        self.tipo_por_fila[self.fila_en_edicion] = 'normal'
        
        self._limpiar_campos_item()

    def _limpiar_campos_item(self):
        self.txt_cantidad.setText("")
        self.txt_descripcion.setText("")
        self.txt_cantidad.setFocus()
        self.btn_agregar.setText("Agregar")
        
        try: self.btn_agregar.clicked.disconnect()
        except TypeError: pass
        self.btn_agregar.clicked.connect(self.agregar_a_tabla)
        
        self.fila_en_edicion = -1

    # ==================================================
    # UTILIDADES (Validación y Mensajes)
    # ==================================================

    def generar_nota_desde_orden(self):
        if not self.orden_actual_id or not self.orden_actual_obj:
            self.mostrar_advertencia("No hay una orden cargada para generar una nota.")
            return

        if self.cmb_estado.currentText() != "Completada":
            self.mostrar_advertencia("Solo se puede generar una nota si el estado de la Orden es 'Completada'.")
            return

        if self.orden_actual_obj.get('nota_folio'):
            self.mostrar_advertencia(f"Ya se generó una Nota de Venta para esta orden (Folio Nota: {self.orden_actual_obj['nota_folio']}).")
            return
        
        try:
            notas_existentes = db_helper.buscar_notas(orden_folio=self.txt_folio.text())
            if notas_existentes:
                self.mostrar_advertencia(f"Ya se generó una Nota de Venta para esta orden (Folio Nota: {notas_existentes[0]['folio']}).")
                return
        except Exception as e:
            self.mostrar_error(f"Error al verificar notas existentes: {e}")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar Generación", 
            f"¿Generar una Nota de Venta para la Orden {self.txt_folio.text()}?\n\n"
            "Los items se agregarán con precio $0.00 y la nota quedará en estado 'Borrador'.\n"
            "La orden cambiará a estado 'Facturada' y ya no se podrá modificar.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.No:
            return

        nombre_cliente = self.txt_cliente.text()
        cliente_id = self.clientes_dict.get(nombre_cliente, None)
        
        if not cliente_id:
            self.mostrar_advertencia("El cliente seleccionado no es válido.")
            return

        marca = self.txt_marca.text()
        modelo = self.txt_modelo.text()
        ano = self.txt_ano.text()
        placa = self.txt_placa.text()
        
        observaciones_list = []
        if marca: observaciones_list.append(f"Marca: {marca}")
        if modelo: observaciones_list.append(f"Modelo: {modelo}")
        if ano: observaciones_list.append(f"Año: {ano}")
        if placa: observaciones_list.append(f"Placa: {placa}")
        
        observaciones_str = ", ".join(observaciones_list)
        
        nota_data = {
            'cliente_id': cliente_id,
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'observaciones': observaciones_str,
            'metodo_pago': None 
        }

        items_para_nota = []
        for fila in range(self.tabla_model.rowCount()):
            tipo = self.tipo_por_fila.get(fila, 'normal')
            
            if tipo == 'normal':
                try:
                    cantidad_str = self.tabla_model.item(fila, 0).text()
                    cantidad = int(float(cantidad_str))
                    descripcion = self.tabla_model.item(fila, 1).text()
                    
                    items_para_nota.append({
                        'cantidad': cantidad,
                        'descripcion': descripcion,
                        'precio_unitario': 0.00,
                        'importe': 0.00,
                        'impuesto': 16.0
                    })
                except Exception as e:
                    print(f"Omitiendo fila {fila} por error al leer datos: {e}")

        if not items_para_nota:
            self.mostrar_advertencia("La orden no tiene items válidos para transferir a la nota.")
            return
        
        try:
            nueva_nota = db_helper.crear_nota(
                nota_data, 
                items_para_nota,
                cotizacion_folio=None,
                orden_folio=self.txt_folio.text(),
                estado='Borrador'
            )
            
            if nueva_nota and nueva_nota.get('folio'):
                
                datos_orden_update = {
                    'estado': 'Facturada',
                    'nota_folio': nueva_nota['folio']
                }
                orden_actualizada = db_helper.actualizar_orden_campos_simples(
                    self.orden_actual_id, 
                    datos_orden_update
                )
                
                if orden_actualizada:
                    self.cargar_orden_en_formulario(orden_actualizada)
                    self.mostrar_exito(
                        f"Nota generada: {nueva_nota['folio']} (en estado Borrador)\n"
                        f"Orden {self.txt_folio.text()} actualizada a 'Facturada' y bloqueada."
                    )
                else:
                    self.mostrar_error("Se creó la nota, pero no se pudo actualizar la orden.")

            else:
                self.mostrar_error("No se pudo crear la nota (respuesta nula de la BD).")
                
        except Exception as e:
            self.mostrar_error(f"Error al crear la nota: {e}")
            import traceback
            traceback.print_exc()

    def validar_datos_orden(self):
        if not self.clientes_dict.get(self.txt_cliente.text(), None):
            self.mostrar_advertencia("Seleccione un cliente válido de la lista.")
            return False
        if not self.txt_marca.text() or not self.txt_modelo.text():
            self.mostrar_advertencia("Ingrese al menos Marca y Modelo del vehículo.")
            return False
        return True

    def validar_item_formulario(self):
        try:
            cantidad_str = self.txt_cantidad.text().strip()
            if not cantidad_str:
                self.mostrar_advertencia("Ingrese una cantidad.")
                return False
                
            cantidad = float(cantidad_str)
            if cantidad <= 0:
                self.mostrar_advertencia("Ingrese una cantidad válida (mayor a 0).")
                return False
        except ValueError:
            self.mostrar_advertencia("Ingrese una cantidad numérica válida.")
            return False
        
        if not self.txt_descripcion.text().strip():
            self.mostrar_advertencia("Ingrese una descripción del trabajo.")
            return False
        
        return True

    def mostrar_advertencia(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Warning, "Advertencia", mensaje)

    def mostrar_exito(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Information, "Éxito", mensaje)

    def mostrar_error(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Critical, "Error", mensaje)

    def mostrar_info(self, mensaje):
        self._mostrar_mensaje(QMessageBox.Information, "Información", mensaje)

    def _mostrar_mensaje(self, icono, titulo, mensaje):
        msg = QMessageBox(self)
        msg.setIcon(icono)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setStyleSheet(MESSAGE_BOX_STYLE)
        msg.exec_()

    def closeEvent(self, event):
        event.accept()

    def imprimir_orden(self):
        if not self.orden_actual_id:
            self.mostrar_advertencia("Primero debe buscar y cargar una orden para imprimir.")
            return

        if not generar_pdf_orden_trabajo:
            self.mostrar_error("Error: El módulo de generación de PDF no está disponible.")
            return
            
        try:
            # 1. Obtener los datos completos
            orden_data = db_helper.get_orden(self.orden_actual_id)
            empresa_data = db_helper.get_config_empresa()
            
            if not orden_data or not empresa_data:
                self.mostrar_error("No se pudieron obtener los datos completos para la impresión.")
                return

            # 2. Preguntar al usuario dónde guardar
            folio = orden_data.get('folio', 'Orden')
            cliente = orden_data.get('cliente_nombre', 'Cliente').replace(" ", "_")
            default_filename = f"{folio}_{cliente}.pdf"

            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar PDF de Orden de Trabajo",
                default_filename,
                "Archivos PDF (*.pdf)"
            )

            # 3. Generar y abrir el PDF
            if save_path:
                exito = generar_pdf_orden_trabajo(orden_data, empresa_data, save_path)
                
                if exito:
                    self.mostrar_exito(f"PDF generado exitosamente en:\n{save_path}")
                    # Intentar abrir el archivo
                    try:
                        if sys.platform == "win32":
                            os.startfile(save_path)
                        elif sys.platform == "darwin":
                            subprocess.call(["open", save_path])
                        else:
                            subprocess.call(["xdg-open", save_path])
                    except Exception as e:
                        print(f"No se pudo abrir el PDF automáticamente: {e}")
                else:
                    self.mostrar_error("Ocurrió un error al generar el archivo PDF.")

        except Exception as e:
            self.mostrar_error(f"Error al preparar la impresión: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        from gui.api_client import api_client as db_helper
    except ImportError:
        db_helper = None 
        
    if not db_helper:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error Crítico")
        msg.setText("No se pudo cargar el módulo 'api_client'.")
        msg.setInformativeText("La aplicación no puede funcionar sin acceso a la base de datos (API Server).")
        msg.exec_()
    else:
        window = OrdenesWindow()
        window.show()
        sys.exit(app.exec_())
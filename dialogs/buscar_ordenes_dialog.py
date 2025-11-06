import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableView, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from datetime import datetime

# --- Asegurar imports ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from gui.api_client import api_client
    from gui.websocket_client import ws_client

    from gui.styles import (
        SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, INPUT_STYLE, TABLE_STYLE, LABEL_STYLE
    )
except ImportError as e:
    print(f"Error importando dependencias en BuscarOrdenesDialog: {e}")
    # Fallback de estilos
    SECONDARY_WINDOW_GRADIENT = "QDialog { background-color: #f0f0f0; }"
    BUTTON_STYLE_2 = "QPushButton { background-color: #00788E; color: white; padding: 10px; }"
    INPUT_STYLE = "QLineEdit, QComboBox { padding: 5px; background-color: #F5F5F5; border-radius: 5px; border: 1px solid #CCC; }"
    TABLE_STYLE = "QTableView { background-color: white; }"
    LABEL_STYLE = "QLabel { color: white; font-weight: bold; background: transparent; }"
# --- Fin asegurar imports ---


class BuscarOrdenesDialog(QDialog):
    """
    Diálogo para buscar y seleccionar entre TODAS las órdenes de trabajo.
    Permite filtrar y ordenar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.orden_seleccionada = None
        self.setup_ui()
        self.cargar_ordenes()

        if ws_client:
            ws_client.orden_creada.connect(self.on_notificacion_remota)
    def on_notificacion_remota(self, data):
        """
        Slot para manejar las notificaciones del WebSocket.
        Recarga la lista de órdenes.
        """
        print(f"Notificación de orden recibida ({data.get('type', 'desconocido')}), recargando lista...")
        self.cargar_ordenes()

    def setup_ui(self):
        self.setWindowTitle("Todas las Órdenes de Trabajo")
        self.setMinimumSize(900, 600)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)
        
        layout = QVBoxLayout()
        
        # Búsqueda
        busqueda_layout = QHBoxLayout()
        busqueda_layout.setSpacing(10)
        
        lbl_buscar = QLabel("Buscar por:")
        lbl_buscar.setStyleSheet(LABEL_STYLE)
        
        self.cmb_filtro = QComboBox()
        # Filtros (Req 4)
        self.cmb_filtro.addItems(["Folio", "Cliente", "Vehículo", "Estado", "Mecánico", "Nota Folio"])
        self.cmb_filtro.setStyleSheet(INPUT_STYLE) 
        
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar...")
        self.txt_buscar.setStyleSheet(INPUT_STYLE)
        self.txt_buscar.textChanged.connect(self.filtrar_ordenes)
        
        busqueda_layout.addWidget(lbl_buscar)
        busqueda_layout.addWidget(self.cmb_filtro, 1)
        busqueda_layout.addWidget(self.txt_buscar, 2)
        layout.addLayout(busqueda_layout)
        
        # Tabla
        self.tabla = QTableView()
        self.tabla.setStyleSheet(TABLE_STYLE)
        self.tabla.setSelectionBehavior(QTableView.SelectRows)
        self.tabla.doubleClicked.connect(self.seleccionar_orden)
        
        self.tabla.setSortingEnabled(True) # Ordenamiento (Req 4)
        
        self.modelo = QStandardItemModel()
        self.modelo.setSortRole(Qt.UserRole)
        # Nuevos Headers
        self.modelo.setHorizontalHeaderLabels(["ID", "Folio", "Fecha", "Cliente", "Vehículo", "Estado", "Mecánico", "Nota Folio"])
        self.tabla.setModel(self.modelo)
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setColumnHidden(0, True)
        
        layout.addWidget(self.tabla)
        
        # Botones
        botones_layout = QHBoxLayout()
        self.btn_seleccionar = QPushButton("Seleccionar")
        self.btn_cerrar = QPushButton("Cerrar")
        
        for btn in [self.btn_seleccionar, self.btn_cerrar]:
            btn.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        
        self.btn_seleccionar.clicked.connect(self.seleccionar_orden)
        self.btn_cerrar.clicked.connect(self.reject)
        
        botones_layout.addWidget(self.btn_seleccionar)
        botones_layout.addWidget(self.btn_cerrar)
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)

    def cargar_ordenes(self):
        """Carga TODAS las órdenes."""
        self.modelo.setRowCount(0)
        if not api_client:
            QMessageBox.critical(self, "Error", "El cliente API no está inicializado.")
            return
            
        try:
            ordenes = api_client.get_all_ordenes() 
            if ordenes is None:
                 raise Exception("No se pudo obtener respuesta del servidor (api_client devolvió None)")
            
            for orden in ordenes:
                item_id = QStandardItem()
                item_folio = QStandardItem()
                item_fecha = QStandardItem()
                item_cliente = QStandardItem()
                item_vehiculo = QStandardItem()
                item_estado = QStandardItem()
                item_mecanico = QStandardItem()
                item_nota_folio = QStandardItem()
                
                # ID (Col 0)
                item_id.setData(str(orden['id']), Qt.DisplayRole)
                item_id.setData(orden['id'], Qt.UserRole)
                
                # Folio (Col 1)
                item_folio.setData(orden['folio'], Qt.DisplayRole)
                item_folio.setData(orden['folio'], Qt.UserRole)
                
                # Fecha (Col 2)
                fecha_obj_iso = orden.get('fecha_recepcion', '') # Obtenemos el campo corregido
                fecha_str = "N/A"
                fecha_obj_qdate = QDate()

                if fecha_obj_iso:
                    try:
                        fecha_dt = datetime.fromisoformat(fecha_obj_iso)
                        fecha_str = fecha_dt.strftime("%d/%m/%Y")
                        fecha_obj_qdate = QDate(fecha_dt.year, fecha_dt.month, fecha_dt.day)
                    except ValueError:
                        fecha_str = fecha_obj_iso # Mostrar ISO si falla
                    
                item_fecha.setData(fecha_str, Qt.DisplayRole)
                item_fecha.setData(fecha_obj_qdate, Qt.UserRole) # Para ordenar
                
                # Cliente (Col 3)
                # (Asegurado por el Paso 1 y 2)
                cliente_nombre = orden.get('cliente_nombre', '') 
                item_cliente.setData(cliente_nombre, Qt.DisplayRole)
                item_cliente.setData(cliente_nombre, Qt.UserRole)
                
                # Vehiculo (Col 4)
                vehiculo_str = f"{orden.get('vehiculo_marca','')} {orden.get('vehiculo_modelo','')} ({orden.get('vehiculo_ano','')})"
                item_vehiculo.setData(vehiculo_str, Qt.DisplayRole)
                item_vehiculo.setData(vehiculo_str, Qt.UserRole)
                
                # Estado (Col 5)
                estado_val = orden['estado']
                item_estado.setData(estado_val, Qt.DisplayRole)
                item_estado.setData(estado_val, Qt.UserRole)
                
                # Mecanico (Col 6)
                # (Asegurado por el Paso 1 y 2)
                mecanico_val = orden.get('mecanico_asignado', '-')
                item_mecanico.setData(mecanico_val, Qt.DisplayRole)
                item_mecanico.setData(mecanico_val, Qt.UserRole)

                # Nota Folio (Col 7)
                # (Asegurado por el Paso 1 y 2)
                nota_val = orden.get('nota_folio', '-')
                item_nota_folio.setData(nota_val, Qt.DisplayRole)
                item_nota_folio.setData(nota_val, Qt.UserRole)
                
                fila = [
                    item_id, item_folio, item_fecha, item_cliente,
                    item_vehiculo, item_estado, item_mecanico, item_nota_folio
                ]
                
                for item in fila:
                    item.setTextAlignment(Qt.AlignCenter)
                
                self.modelo.appendRow(fila)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar órdenes: {e}")

    def filtrar_ordenes(self):
        """Filtra órdenes según criterio"""
        texto = self.txt_buscar.text().lower()
        criterio = self.cmb_filtro.currentText()
        
        columnas = {
            "Folio": 1, 
            "Cliente": 3, 
            "Vehículo": 4, 
            "Estado": 5, 
            "Mecánico": 6,
            "Nota Folio": 7
        }
        col = columnas.get(criterio, 1)
        
        for fila in range(self.modelo.rowCount()):
            valor = self.modelo.item(fila, col).text().lower()
            self.tabla.setRowHidden(fila, texto not in valor)

    def seleccionar_orden(self):
        """Selecciona la orden y cierra"""
        indices = self.tabla.selectedIndexes()
        if not indices:
            QMessageBox.warning(self, "Aviso", "Seleccione una orden")
            return
        
        fila = indices[0].row()
        orden_id = int(self.modelo.item(fila, 0).data(Qt.UserRole))

        if not api_client:
            QMessageBox.critical(self, "Error", "El cliente API no está inicializado.")
            return
            
        try:
            ordenes = api_client.get_all_ordenes() 
            self.orden_seleccionada = next((o for o in ordenes if o['id'] == orden_id), None)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al seleccionar orden: {e}")
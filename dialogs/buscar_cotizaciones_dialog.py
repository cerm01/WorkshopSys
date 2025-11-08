import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableView, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from datetime import datetime

# --- Inicio: Asegurar imports ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from gui.api_client import api_client
    from gui.websocket_client import ws_client
    from gui.styles import (
        SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, INPUT_STYLE, TABLE_STYLE, LABEL_STYLE, MESSAGE_BOX_STYLE
    )
except ImportError as e:
    print(f"Error importando dependencias en BuscarCotizacionesDialog: {e}")
    # Definir estilos de fallback en caso de error
    SECONDARY_WINDOW_GRADIENT = "QDialog { background-color: #f0f0f0; }"
    BUTTON_STYLE_2 = "QPushButton { background-color: #00788E; color: white; padding: 10px; }"
    INPUT_STYLE = "QLineEdit, QComboBox { padding: 5px; background-color: #F5F5F5; border-radius: 5px; border: 1px solid #CCC; }"
    TABLE_STYLE = "QTableView { background-color: white; }"
    LABEL_STYLE = "QLabel { color: white; font-weight: bold; background: transparent; }"
    MESSAGE_BOX_STYLE = "QMessageBox { background-color: white; }"
# --- Fin: Asegurar imports ---


class BuscarCotizacionesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cotizacion_seleccionada = None
        self.setup_ui()
        if ws_client:
            ws_client.cotizacion_creada.connect(self.on_notificacion_remota)
        QTimer.singleShot(1, self.cargar_cotizaciones)


    def on_notificacion_remota(self, data):
        """
        Slot para manejar las notificaciones del WebSocket.
        Recarga la lista de cotizaciones.
        """
        print(f"Notificación de cotización recibida ({data.get('type', 'desconocido')}), recargando lista...")
        self.cargar_cotizaciones()

    def setup_ui(self):
        self.setWindowTitle("Todas las Cotizaciones")
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
        # --- MODIFICADO: Añadir "Nota" al filtro ---
        self.cmb_filtro.addItems(["Folio", "Cliente", "Total", "Estado", "Nota"])
        self.cmb_filtro.setStyleSheet(INPUT_STYLE) 
        
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar...")
        self.txt_buscar.setStyleSheet(INPUT_STYLE)
        self.txt_buscar.textChanged.connect(self.filtrar_cotizaciones)
        
        busqueda_layout.addWidget(lbl_buscar)
        busqueda_layout.addWidget(self.cmb_filtro, 1)
        busqueda_layout.addWidget(self.txt_buscar, 2)
        layout.addLayout(busqueda_layout)
        
        # Tabla
        self.tabla = QTableView()
        self.tabla.setStyleSheet(TABLE_STYLE)
        self.tabla.setSelectionBehavior(QTableView.SelectRows)
        self.tabla.doubleClicked.connect(self.seleccionar_cotizacion)
        
        self.tabla.setSortingEnabled(True) 
        
        self.modelo = QStandardItemModel()
        self.modelo.setSortRole(Qt.UserRole)
        # --- MODIFICADO: Añadir "Nota" a las cabeceras ---
        self.modelo.setHorizontalHeaderLabels(["ID", "Folio", "Fecha", "Vigencia", "Cliente", "Total", "Estado", "Nota"])
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
        
        self.btn_seleccionar.clicked.connect(self.seleccionar_cotizacion)
        self.btn_cerrar.clicked.connect(self.reject)
        
        botones_layout.addWidget(self.btn_seleccionar)
        botones_layout.addWidget(self.btn_cerrar)
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)

    def cargar_cotizaciones(self):
        """Carga todas las cotizaciones (con datos para ordenamiento)"""
        self.modelo.setRowCount(0)
        try:
            cotizaciones = api_client.get_all_cotizaciones()

            if cotizaciones is None:
                raise Exception("No se pudo obtener respuesta del servidor (api_client devolvió None)")

            for cotizacion in cotizaciones:
                item_id = QStandardItem()
                item_folio = QStandardItem()
                item_fecha = QStandardItem()
                item_vigencia = QStandardItem()
                item_cliente = QStandardItem()
                item_total = QStandardItem()
                item_estado = QStandardItem()
                item_nota_folio = QStandardItem() 
                
                # ID (Col 0)
                item_id.setData(str(cotizacion['id']), Qt.DisplayRole)
                item_id.setData(cotizacion['id'], Qt.UserRole)
                
                # Folio (Col 1)
                item_folio.setData(cotizacion['folio'], Qt.DisplayRole)
                item_folio.setData(cotizacion['folio'], Qt.UserRole)
                
                # Fecha (Col 2)
                # --- INICIO DE CAMBIOS: Ajuste de formato de fecha ---
                # El api_client devuelve formato ISO (ej: "2025-11-05T10:00:00")
                # El db_helper devolvía "dd/MM/yyyy"
                fecha_str_iso = cotizacion.get('fecha', '')
                fecha_obj = QDate()
                if fecha_str_iso:
                    try:
                        fecha_dt = datetime.fromisoformat(fecha_str_iso)
                        fecha_str_display = fecha_dt.strftime("%d/%m/%Y")
                        fecha_obj = QDate(fecha_dt.year, fecha_dt.month, fecha_dt.day)
                    except ValueError:
                        fecha_str_display = fecha_str_iso # Mostrar ISO si no se puede parsear
                else:
                    fecha_str_display = "N/A"
                
                item_fecha.setData(fecha_str_display, Qt.DisplayRole)
                item_fecha.setData(fecha_obj, Qt.UserRole)
                
                # Vigencia (Col 3)
                vigencia_str = cotizacion.get('vigencia', '')
                vigencia_obj = QDate.fromString(vigencia_str, "dd/MM/yyyy")
                item_vigencia.setData(vigencia_str, Qt.DisplayRole)
                item_vigencia.setData(vigencia_obj, Qt.UserRole) 
                
                # Cliente (Col 4)
                # NOTA: Asumimos que el endpoint /cotizaciones devuelve 'cliente_nombre'
                # Si no lo hace, el servidor (server/main.py) debe ser ajustado.
                cliente_nombre = cotizacion.get('cliente_nombre', f"ID: {cotizacion['cliente_id']}")
                item_cliente.setData(cliente_nombre, Qt.DisplayRole)
                item_cliente.setData(cliente_nombre, Qt.UserRole)
                
                # Total (Col 5)
                item_total.setData(f"${cotizacion['total']:.2f}", Qt.DisplayRole)
                item_total.setData(cotizacion['total'], Qt.UserRole)
                
                # Estado (Col 6)
                estado_val = cotizacion['estado']
                item_estado.setData(estado_val, Qt.DisplayRole)
                item_estado.setData(estado_val, Qt.UserRole) 
                
                # Nota (Col 7)
                nota_folio_val = cotizacion.get('nota_folio') or "-"
                item_nota_folio.setData(nota_folio_val, Qt.DisplayRole)
                item_nota_folio.setData(nota_folio_val, Qt.UserRole)

                # --- Añadir la fila ---
                fila = [
                    item_id, item_folio, item_fecha, item_vigencia, 
                    item_cliente, item_total, item_estado, item_nota_folio
                ]
                
                for item in fila:
                    item.setTextAlignment(Qt.AlignCenter)
                
                self.modelo.appendRow(fila)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar cotizaciones: {e}")

    def filtrar_cotizaciones(self):
        """Filtra cotizaciones según criterio"""
        texto = self.txt_buscar.text().lower()
        criterio = self.cmb_filtro.currentText()
        
        # --- MODIFICADO: Añadir "Nota" a las columnas de filtro ---
        columnas = {"Folio": 1, "Cliente": 4, "Total": 5, "Estado": 6, "Nota": 7}
        col = columnas.get(criterio, 1)
        
        for fila in range(self.modelo.rowCount()):
            valor = self.modelo.item(fila, col).text().lower()
            self.tabla.setRowHidden(fila, texto not in valor)

    def seleccionar_cotizacion(self):
        """Selecciona la cotización y cierra"""
        indices = self.tabla.selectedIndexes()
        if not indices:
            QMessageBox.warning(self, "Aviso", "Seleccione una cotización")
            return
        
        fila = indices[0].row()
        cotizacion_id = int(self.modelo.item(fila, 0).data(Qt.UserRole))
        
        try:
            cotizaciones = api_client.get_all_cotizaciones()
            self.cotizacion_seleccionada = next((c for c in cotizaciones if c['id'] == cotizacion_id), None)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")
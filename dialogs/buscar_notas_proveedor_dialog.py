import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableView, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from gui.api_client import api_client
    from gui.websocket_client import ws_client
except ImportError as e:
    print(f"Error importando api_client o ws_client: {e}")
    # Fallback para evitar que el editor marque error
    api_client = None 
    ws_client = None

from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, INPUT_STYLE, TABLE_STYLE, LABEL_STYLE, MESSAGE_BOX_STYLE
)

class BuscarNotasProveedorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nota_seleccionada = None
        self.setup_ui()
        if ws_client:
            try:

                ws_client.nota_proveedor_creada.connect(self.on_notificacion_remota)
            except AttributeError:
                print("Advertencia: La señal 'nota_proveedor_creada' no está definida en ws_client.")

        QTimer.singleShot(5, self.cargar_notas)

    def on_notificacion_remota(self, data):
        """
        Slot para manejar las notificaciones del WebSocket.
        Recarga la lista de notas de proveedor.
        """
        print(f"Notificación de nota de proveedor recibida, recargando lista...")
        self.cargar_notas()

    def setup_ui(self):
        self.setWindowTitle("Todas las Notas de Proveedor")
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
        self.cmb_filtro.addItems(["Folio", "Proveedor", "Total"])
        self.cmb_filtro.setStyleSheet(INPUT_STYLE) 
        
        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText("Buscar...")
        self.txt_buscar.setStyleSheet(INPUT_STYLE)
        self.txt_buscar.textChanged.connect(self.filtrar_notas)
        
        busqueda_layout.addWidget(lbl_buscar)
        busqueda_layout.addWidget(self.cmb_filtro, 1)
        busqueda_layout.addWidget(self.txt_buscar, 2)
        layout.addLayout(busqueda_layout)
        
        # Tabla
        self.tabla = QTableView()
        self.tabla.setStyleSheet(TABLE_STYLE)
        self.tabla.setSelectionBehavior(QTableView.SelectRows)
        self.tabla.doubleClicked.connect(self.seleccionar_nota)
        
        # --- Configuración de Ordenamiento ---
        self.tabla.setSortingEnabled(True) 
        
        self.modelo = QStandardItemModel()
        self.modelo.setSortRole(Qt.UserRole)
        self.modelo.setHorizontalHeaderLabels(["ID", "Folio", "Fecha", "Proveedor", "Subtotal", "IVA", "Total", "Estado"])
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
        
        self.btn_seleccionar.clicked.connect(self.seleccionar_nota)
        self.btn_cerrar.clicked.connect(self.reject)
        
        botones_layout.addWidget(self.btn_seleccionar)
        botones_layout.addWidget(self.btn_cerrar)
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)

    def cargar_notas(self):
        """Carga todas las notas (con datos para ordenamiento)"""
        self.modelo.setRowCount(0)
        if not api_client:
            QMessageBox.critical(self, "Error", "El cliente API no está inicializado.")
            return

        try:
            notas = api_client.get_all_notas_proveedor()
            
            if notas is None:
                raise Exception("No se pudo obtener respuesta del servidor (api_client devolvió None)")
                
            for nota in notas:
                item_id = QStandardItem()
                item_folio = QStandardItem()
                item_fecha = QStandardItem()
                item_proveedor = QStandardItem()
                item_subtotal = QStandardItem()
                item_iva = QStandardItem()
                item_total = QStandardItem()
                item_estado = QStandardItem()
                
                # ID (Col 0)
                item_id.setData(str(nota['id']), Qt.DisplayRole)
                item_id.setData(nota['id'], Qt.UserRole) # Ordenar como número
                
                # Folio (Col 1)
                item_folio.setData(nota['folio'], Qt.DisplayRole)
                item_folio.setData(nota['folio'], Qt.UserRole) # Ordenar como texto
                
                # Fecha (Col 2)
                fecha_str_iso = nota.get('fecha', '')
                fecha_obj = QDate()
                if fecha_str_iso:
                    try:
                        fecha_dt = datetime.fromisoformat(fecha_str_iso)
                        fecha_str_display = fecha_dt.strftime("%d/%m/%Y")
                        fecha_obj = QDate(fecha_dt.year, fecha_dt.month, fecha_dt.day)
                    except ValueError:
                        fecha_str_display = fecha_str_iso
                else:
                    fecha_str_display = "N/A"
                
                item_fecha.setData(fecha_str_display, Qt.DisplayRole)
                item_fecha.setData(fecha_obj, Qt.UserRole)
                
                # Proveedor (Col 3)
                proveedor_nombre = nota.get('proveedor_nombre', '')
                item_proveedor.setData(proveedor_nombre, Qt.DisplayRole)
                item_proveedor.setData(proveedor_nombre, Qt.UserRole) # Ordenar como texto
                
                # Subtotal (Col 4)
                subtotal_val = nota.get('subtotal', 0.0)
                item_subtotal.setData(f"${subtotal_val:.2f}", Qt.DisplayRole)
                item_subtotal.setData(subtotal_val, Qt.UserRole) # Ordenar como número
                
                # IVA (Col 5)
                impuestos_val = nota.get('impuestos', 0.0)
                item_iva.setData(f"${impuestos_val:.2f}", Qt.DisplayRole) # <-- 'impuestos'
                item_iva.setData(impuestos_val, Qt.UserRole) # Ordenar como número
                
                # Total (Col 6)
                total_val = nota.get('total', 0.0)
                item_total.setData(f"${total_val:.2f}", Qt.DisplayRole)
                item_total.setData(total_val, Qt.UserRole) # Ordenar como número
                
                # Estado (Col 7)
                estado_val = nota.get('estado', 'N/A')
                item_estado.setData(estado_val, Qt.DisplayRole)
                item_estado.setData(estado_val, Qt.UserRole) # Ordenar como texto

                # --- Añadir la fila ---
                fila = [
                    item_id, item_folio, item_fecha, item_proveedor,
                    item_subtotal, item_iva, item_total, item_estado
                ]
                
                # Mantener la alineación
                for item in fila:
                    item.setTextAlignment(Qt.AlignCenter)
                
                self.modelo.appendRow(fila)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar notas de proveedor: {e}")

    def filtrar_notas(self):
        """Filtra notas según criterio"""
        texto = self.txt_buscar.text().lower()
        criterio = self.cmb_filtro.currentText()
        
        columnas = {"Folio": 1, "Proveedor": 3, "Total": 6}
        col = columnas.get(criterio, 1)
        
        for fila in range(self.modelo.rowCount()):
            valor = self.modelo.item(fila, col).text().lower()
            self.tabla.setRowHidden(fila, texto not in valor)

    def seleccionar_nota(self):
        """Selecciona la nota y cierra"""
        indices = self.tabla.selectedIndexes()
        if not indices:
            QMessageBox.warning(self, "Aviso", "Seleccione una nota")
            return
        
        fila = indices[0].row()
        # Leemos el ID de la columna 0, usando los datos reales (UserRole)
        nota_id = int(self.modelo.item(fila, 0).data(Qt.UserRole))
        
        if not api_client:
            QMessageBox.critical(self, "Error", "El cliente API no está inicializado.")
            return
            
        try:
            notas = api_client.get_all_notas_proveedor()
        
            self.nota_seleccionada = next((n for n in notas if n['id'] == nota_id), None)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")
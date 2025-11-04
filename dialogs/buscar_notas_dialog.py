from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableView, QLineEdit, QComboBox, QLabel, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from gui.db_helper import db_helper
from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, INPUT_STYLE, TABLE_STYLE, LABEL_STYLE
)

class BuscarNotasDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nota_seleccionada = None
        self.setup_ui()
        self.cargar_notas()

    def setup_ui(self):
        self.setWindowTitle("Todas las Notas")
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
        # --- MODIFICADO: Añadir "Origen" al filtro ---
        self.cmb_filtro.addItems(["Folio", "Cliente", "Total", "Estado", "Origen"])
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
        
        self.tabla.setSortingEnabled(True) 
        
        self.modelo = QStandardItemModel()
        self.modelo.setSortRole(Qt.UserRole)
        # --- MODIFICADO: Añadir "Origen" a las cabeceras ---
        self.modelo.setHorizontalHeaderLabels(["ID", "Folio", "Fecha", "Cliente", "Subtotal", "IVA", "Total", "Estado", "Origen"])
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
        try:
            notas = db_helper.get_notas()
            for nota in notas:
                item_id = QStandardItem()
                item_folio = QStandardItem()
                item_fecha = QStandardItem()
                item_cliente = QStandardItem()
                item_subtotal = QStandardItem()
                item_iva = QStandardItem()
                item_total = QStandardItem()
                item_estado = QStandardItem()
                item_origen = QStandardItem() # <-- AÑADIDO
                
                # ID (Col 0)
                item_id.setData(str(nota['id']), Qt.DisplayRole)
                item_id.setData(nota['id'], Qt.UserRole)
                
                # Folio (Col 1)
                item_folio.setData(nota['folio'], Qt.DisplayRole)
                item_folio.setData(nota['folio'], Qt.UserRole)
                
                # Fecha (Col 2)
                fecha_obj = QDate.fromString(nota['fecha'], "dd/MM/yyyy")
                item_fecha.setData(nota['fecha'], Qt.DisplayRole)
                item_fecha.setData(fecha_obj, Qt.UserRole)
                
                # Cliente (Col 3)
                cliente_nombre = nota.get('cliente_nombre', '')
                item_cliente.setData(cliente_nombre, Qt.DisplayRole)
                item_cliente.setData(cliente_nombre, Qt.UserRole)
                
                # Subtotal (Col 4)
                item_subtotal.setData(f"${nota['subtotal']:.2f}", Qt.DisplayRole)
                item_subtotal.setData(nota['subtotal'], Qt.UserRole)
                
                # IVA (Col 5)
                item_iva.setData(f"${nota['impuestos']:.2f}", Qt.DisplayRole)
                item_iva.setData(nota['impuestos'], Qt.UserRole)
                
                # Total (Col 6)
                item_total.setData(f"${nota['total']:.2f}", Qt.DisplayRole)
                item_total.setData(nota['total'], Qt.UserRole)
                
                # Estado (Col 7)
                estado_val = nota['estado']
                item_estado.setData(estado_val, Qt.DisplayRole)
                item_estado.setData(estado_val, Qt.UserRole)
                
                # --- INICIO DE MODIFICACIÓN ---
                # Origen (Col 8)
                origen_val = nota.get('cotizacion_folio') or "-"
                item_origen.setData(origen_val, Qt.DisplayRole)
                item_origen.setData(origen_val, Qt.UserRole)
                # --- FIN DE MODIFICACIÓN ---

                # --- Añadir la fila ---
                fila = [
                    item_id, item_folio, item_fecha, item_cliente,
                    item_subtotal, item_iva, item_total, item_estado,
                    item_origen # <-- AÑADIDO
                ]
                
                # Mantener la alineación
                for item in fila:
                    item.setTextAlignment(Qt.AlignCenter)
                
                self.modelo.appendRow(fila)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar notas: {e}")

    def filtrar_notas(self):
        """Filtra notas según criterio"""
        texto = self.txt_buscar.text().lower()
        criterio = self.cmb_filtro.currentText()
        
        # --- MODIFICADO: Añadir "Origen" al diccionario de columnas ---
        columnas = {"Folio": 1, "Cliente": 3, "Total": 6, "Estado": 7, "Origen": 8}
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
        nota_id = int(self.modelo.item(fila, 0).data(Qt.UserRole))
        
        try:
            notas = db_helper.get_notas() 
            self.nota_seleccionada = next((n for n in notas if n['id'] == nota_id), None)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")
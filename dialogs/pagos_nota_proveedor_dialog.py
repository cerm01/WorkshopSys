import sys
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QGridLayout, QGroupBox, QDoubleSpinBox, QMessageBox, QTableView,
    QHeaderView, QWidget, QDateEdit, QComboBox, QApplication,
    QMenu, QAction
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from gui.api_client import api_client
    from gui.websocket_client import ws_client
    
    from dialogs.buscar_notas_proveedor_dialog import BuscarNotasProveedorDialog
    from gui.styles import (
        SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE,
        LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, FORM_BUTTON_STYLE, MESSAGE_BOX_STYLE
    )
except ImportError as e:
    print(f"Error de importación en pagos_nota_proveedor_dialog.py: {e}")
    # Fallback de estilos en caso de error
    SECONDARY_WINDOW_GRADIENT = "QDialog { background-color: #f0f0f0; }"
    BUTTON_STYLE_2 = "QPushButton { background-color: #00788E; color: white; padding: 10px; }"
    GROUP_BOX_STYLE = "QGroupBox { border: 1px solid #00788E; margin-top: 10px; }"
    LABEL_STYLE = "QLabel { color: white; font-weight: bold; background: transparent; }"
    INPUT_STYLE = "QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit { padding: 5px; background-color: #F5F5F5; border-radius: 5px; border: 1px solid #CCC; }"
    TABLE_STYLE = "QTableView { background-color: white; }"
    FORM_BUTTON_STYLE = "QPushButton { background-color: #2CD5C4; color: white; padding: 8px; border-radius: 5px; }"
    MESSAGE_BOX_STYLE = "QMessageBox { background-color: white; }"


class PagosNotaProveedorDialog(QDialog):
    """
    Ventana para la emisión de pagos a proveedores de una Nota de Proveedor.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Emisión de Pagos a Proveedores")  
        self.setMinimumSize(1000, 700)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        self.nota_actual = None
        self.setup_ui()
        self.conectar_senales()

        if ws_client:
            ws_client.nota_proveedor_actualizada.connect(self.on_notificacion_remota)

    def on_notificacion_remota(self, nota_actualizada):
        """
        Slot para manejar las notificaciones del WebSocket.
        Si la nota actualizada es la que estamos viendo, la recarga.
        """
        if self.nota_actual and self.nota_actual['id'] == nota_actualizada.get('id'):
            print(f"Recargando Nota Proveedor {self.nota_actual['id']} por notificación remota.")
            self.cargar_nota(nota_actualizada)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 1. Grupo de Búsqueda y Datos de la Nota
        self.crear_grupo_busqueda(main_layout)
        
        # 2. Grupo de Registro de Pago
        self.crear_grupo_registro_pago(main_layout)
        
        # 3. Historial de Pagos
        self.crear_historial_pagos(main_layout)
        
        # 4. Botón de Cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        btn_cerrar.clicked.connect(self.accept)
        
        # Layout para el botón cerrar (alineado a la derecha)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_cerrar)
        
        main_layout.addLayout(bottom_layout)

    def crear_grupo_busqueda(self, parent_layout):
        grupo = QGroupBox()  
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QGridLayout()
        layout.setSpacing(10)
        
        self.btn_buscar_nota = QPushButton("Buscar Nota de Proveedor")  
        self.btn_buscar_nota.setStyleSheet(FORM_BUTTON_STYLE)
        layout.addWidget(self.btn_buscar_nota, 0, 0, 2, 1) # Abarca 2 filas
        
        # Labels
        layout.addWidget(self.crear_label_pago("Folio:"), 0, 1)
        layout.addWidget(self.crear_label_pago("Proveedor:"), 1, 1)  
        layout.addWidget(self.crear_label_pago("Total Nota:"), 0, 3)
        layout.addWidget(self.crear_label_pago("Saldo Pendiente:"), 1, 3)
        
        # Campos (Solo Lectura)
        readonly_style = INPUT_STYLE + "QLineEdit { background-color: #E8E8E8; color: #666; }"
        self.txt_folio_nota = QLineEdit()
        self.txt_folio_nota.setReadOnly(True)
        self.txt_folio_nota.setStyleSheet(readonly_style)
        layout.addWidget(self.txt_folio_nota, 0, 2)
        
        self.txt_proveedor_nota = QLineEdit()  
        self.txt_proveedor_nota.setReadOnly(True)  
        self.txt_proveedor_nota.setStyleSheet(readonly_style)  
        layout.addWidget(self.txt_proveedor_nota, 1, 2)  
        
        self.txt_total_nota = QLineEdit()
        self.txt_total_nota.setReadOnly(True)
        self.txt_total_nota.setStyleSheet(readonly_style)
        layout.addWidget(self.txt_total_nota, 0, 4)
        
        # Estilo especial para el saldo pendiente
        saldo_style = readonly_style + """
        QLineEdit { 
            font-weight: bold; 
            font-size: 18px;
            color: #D32F2F; 
            background-color: #FFEBEE;
        }"""
        self.txt_saldo_nota = QLineEdit()
        self.txt_saldo_nota.setReadOnly(True)
        self.txt_saldo_nota.setStyleSheet(saldo_style)
        layout.addWidget(self.txt_saldo_nota, 1, 4)
        
        layout.setColumnStretch(2, 2)
        layout.setColumnStretch(4, 2)
        grupo.setLayout(layout)
        parent_layout.addWidget(grupo)

    def crear_grupo_registro_pago(self, parent_layout):
        self.grupo_pago = QGroupBox()
        self.grupo_pago.setStyleSheet(GROUP_BOX_STYLE)
        self.grupo_pago.setEnabled(False) # Deshabilitado hasta cargar nota
        
        layout = QGridLayout()
        layout.setSpacing(10)
        top_row_style = INPUT_STYLE + """
        QDoubleSpinBox, QDateEdit {
            font-size: 18px;
            min-height: 40px;
        }
        """
        # Fila 1
        layout.addWidget(self.crear_label_pago("Monto a Pagar:"), 0, 0)
        self.spin_monto_pago = QDoubleSpinBox()
        self.spin_monto_pago.setRange(0.00, 9999999.99)
        self.spin_monto_pago.setDecimals(2)
        self.spin_monto_pago.setPrefix("$ ")
        self.spin_monto_pago.setStyleSheet(top_row_style) # Estilo aplicado
        layout.addWidget(self.spin_monto_pago, 0, 1)
        
        layout.addWidget(self.crear_label_pago("Fecha de Pago:"), 0, 2)
        self.date_fecha_pago = QDateEdit()
        self.date_fecha_pago.setDate(QDate.currentDate())
        self.date_fecha_pago.setCalendarPopup(True)
        self.date_fecha_pago.setDisplayFormat("dd/MM/yyyy")
        self.date_fecha_pago.setStyleSheet(top_row_style) # Estilo aplicado
        layout.addWidget(self.date_fecha_pago, 0, 3)

        # Fila 2
        layout.addWidget(self.crear_label_pago("Método de Pago:"), 1, 0)
        self.cmb_metodo_pago = QComboBox()
        self.cmb_metodo_pago.addItems([
            "Efectivo", "TDD", "TDC", "Cheque", "Transferencia", "Otro"
        ])
        self.cmb_metodo_pago.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.cmb_metodo_pago, 1, 1)

        layout.addWidget(self.crear_label_pago("Memo:"), 1, 2)
        self.txt_memo_pago = QLineEdit()
        self.txt_memo_pago.setPlaceholderText("Ej: Pago de factura F-123, Abono...")  
        self.txt_memo_pago.setStyleSheet(INPUT_STYLE)
        layout.addWidget(self.txt_memo_pago, 1, 3)
        
        # Botón
        self.btn_aplicar_pago = QPushButton("Aplicar Pago")
        self.btn_aplicar_pago.setStyleSheet(FORM_BUTTON_STYLE)
        self.btn_aplicar_pago.setMinimumHeight(50) # Botón más alto
        layout.addWidget(self.btn_aplicar_pago, 0, 4, 2, 1) # Abarca 2 filas
        
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(3, 2)
        
        self.grupo_pago.setLayout(layout)
        parent_layout.addWidget(self.grupo_pago)

    def crear_historial_pagos(self, parent_layout):
        hist_container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        
        lbl = QLabel("Historial de Pagos de la Nota de Proveedor")
        lbl.setStyleSheet("QLabel { color: #FFFFFF; font-size: 16px; font-weight: bold; }")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        
        self.tabla_pagos_model = QStandardItemModel()
        self.tabla_pagos_model.setHorizontalHeaderLabels(
            ["ID_PAGO", "Fecha", "Monto", "Método de Pago", "Memo"]
        )
        self.tabla_pagos = QTableView()
        self.tabla_pagos.setModel(self.tabla_pagos_model)
        self.tabla_pagos.setStyleSheet(TABLE_STYLE)
        self.tabla_pagos.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_pagos.setAlternatingRowColors(True)
        
        # Habilitar menú contextual (clic derecho)
        self.tabla_pagos.setContextMenuPolicy(Qt.CustomContextMenu)
        
        header = self.tabla_pagos.horizontalHeader()
        
        # Ocultar la columna 0 (ID_PAGO)
        self.tabla_pagos.setColumnHidden(0, True)
        
        # Ajustar los índices de las columnas visibles
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Fecha
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Monto
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Método
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # Memo

        layout.addWidget(self.tabla_pagos)
        hist_container.setLayout(layout)
        parent_layout.addWidget(hist_container, 1) # Que la tabla crezca

    def conectar_senales(self):
        self.btn_buscar_nota.clicked.connect(self.abrir_busqueda_notas_proveedor)  
        self.btn_aplicar_pago.clicked.connect(self.aplicar_pago)
        
        # Conectar señal de clic derecho en la tabla de pagos
        self.tabla_pagos.customContextMenuRequested.connect(self.mostrar_menu_contextual_pagos)
    
    def crear_label_pago(self, texto):
        lbl = QLabel(texto)
        lbl.setStyleSheet(LABEL_STYLE)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return lbl

    def abrir_busqueda_notas_proveedor(self):  
        """Abre el diálogo para buscar y seleccionar una nota de proveedor."""
        dialog = BuscarNotasProveedorDialog(self)  
        if dialog.exec_() == QDialog.Accepted and dialog.nota_seleccionada:
            # Volvemos a consultar la nota para tener los datos más frescos
            try:
                nota_fresca = api_client.get_nota_proveedor(dialog.nota_seleccionada['id']) 
                if nota_fresca:
                    self.cargar_nota(nota_fresca)
                else:
                    self.mostrar_mensaje("Error", "No se pudo recargar la nota seleccionada.", QMessageBox.Critical)
            except Exception as e:
                self.mostrar_mensaje("Error", f"Error al recargar nota: {e}", QMessageBox.Critical)

    def cargar_nota(self, nota_dict):
        """Puebla la UI con los datos de la nota seleccionada."""
        self.nota_actual = nota_dict
        
        saldo = nota_dict.get('saldo', 0.0)
        
        self.txt_folio_nota.setText(nota_dict.get('folio', ''))
        self.txt_proveedor_nota.setText(nota_dict.get('proveedor_nombre', ''))  
        self.txt_total_nota.setText(f"${nota_dict.get('total', 0.0):,.2f}")
        self.txt_saldo_nota.setText(f"${saldo:,.2f}")
        
        # Ajustar el SpinBox de monto
        self.spin_monto_pago.setValue(saldo)
        self.spin_monto_pago.setMaximum(max(0.00, saldo))
        
        self.cargar_historial_pagos()
        
        # Habilitar/Deshabilitar grupo de pago
        if saldo > 0.01 and nota_dict.get('estado') != 'Cancelada':
            self.grupo_pago.setEnabled(True)
            self.spin_monto_pago.setFocus()
        else:
            self.grupo_pago.setEnabled(False)
            if nota_dict.get('estado') == 'Cancelada':
                self.mostrar_mensaje("Nota Cancelada", "No se pueden aplicar pagos a una nota cancelada.", QMessageBox.Warning)
            elif saldo <= 0.01:
                self.mostrar_mensaje("Nota Pagada", "Esta nota ya ha sido liquidada.", QMessageBox.Information)

    def cargar_historial_pagos(self):
        """Carga la tabla con los pagos existentes de la nota actual."""
        self.tabla_pagos_model.setRowCount(0)
        if not self.nota_actual:
            return
            
        try:
            # Los pagos vienen dentro del diccionario de la nota
            pagos = self.nota_actual.get('pagos', [])
            
            for pago in reversed(pagos): # Mostrar el más reciente primero
                
                # Añadir ID_PAGO a la fila (Columna 0)
                item_id_pago = QStandardItem(str(pago['id']))
                item_fecha = QStandardItem(pago['fecha_pago'])
                item_monto = QStandardItem(f"${pago['monto']:,.2f}")
                item_metodo = QStandardItem(pago['metodo_pago'])
                item_memo = QStandardItem(pago['memo'])
                
                item_monto.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                fila = [
                    item_id_pago, # Col 0 (Oculta)
                    item_fecha,   # Col 1
                    item_monto,   # Col 2
                    item_metodo,  # Col 3
                    item_memo     # Col 4
                ]
                self.tabla_pagos_model.appendRow(fila)
                
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar historial: {e}", QMessageBox.Critical)

    def aplicar_pago(self):
        """Valida y registra el nuevo pago en la base de datos."""
        if not self.nota_actual:
            return
            
        monto = self.spin_monto_pago.value()
        fecha_pago_qdate = self.date_fecha_pago.date()
        # Convertir QDate a objeto datetime.date
        fecha_pago_py = fecha_pago_qdate.toPyDate() 
        
        metodo_pago = self.cmb_metodo_pago.currentText()
        memo = self.txt_memo_pago.text().strip()
        
        # Validaciones
        if monto <= 0:
            self.mostrar_mensaje("Error", "El monto debe ser mayor a cero.", QMessageBox.Critical)
            return
            
        # Tolerancia de 1 centavo para errores de punto flotante
        if monto > (self.nota_actual['saldo'] + 0.01):
            self.mostrar_mensaje("Error", f"El monto excede el saldo pendiente de ${self.nota_actual['saldo']:.2f}", QMessageBox.Critical)
            return
            
        try:
            nota_actualizada = api_client.registrar_pago_proveedor(
                self.nota_actual['id'],
                monto,
                fecha_pago_py, # Enviar el objeto date de Python
                metodo_pago,
                memo
            )
            
            if nota_actualizada:
                self.mostrar_mensaje("Éxito", "Pago aplicado correctamente.", QMessageBox.Information)
                # Recargar la nota con los datos actualizados
                self.cargar_nota(nota_actualizada)
                self.txt_memo_pago.clear()
            else:
                self.mostrar_mensaje("Error", "No se pudo aplicar el pago (respuesta nula de la BD).", QMessageBox.Critical)
                
        except ValueError as ve: # Capturar errores de validación (ej. "Nota cancelada")
            self.mostrar_mensaje("Error de Validación", str(ve), QMessageBox.Critical)
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error inesperado al aplicar el pago: {e}", QMessageBox.Critical)

    def mostrar_menu_contextual_pagos(self, position):
        """Muestra el menú de clic derecho para la tabla de pagos."""
        indexes = self.tabla_pagos.selectedIndexes()
        
        # Solo mostrar si hay una fila seleccionada
        if not indexes:
            return

        menu = QMenu(self)
        
        # Acción para eliminar
        action_eliminar = QAction("Eliminar Abono Seleccionado", self)
        action_eliminar.triggered.connect(self.eliminar_pago_seleccionado)
        
        # No permitir eliminar si la nota está cancelada
        if self.nota_actual and self.nota_actual.get('estado') == 'Cancelada':
             action_eliminar.setEnabled(False)
             action_eliminar.setText("No se puede modificar una nota cancelada")
             
        menu.addAction(action_eliminar)
        
        # Mostrar el menú en la posición del cursor
        menu.exec_(self.tabla_pagos.viewport().mapToGlobal(position))

    def eliminar_pago_seleccionado(self):
        """Obtiene el ID del pago y llama al api_client para eliminarlo."""
        indexes = self.tabla_pagos.selectedIndexes()
        if not indexes:
            return

        # Obtener la fila seleccionada
        fila = indexes[0].row()
        
        # Obtener el ID del pago (almacenado en la columna 0, que está oculta)
        try:
            pago_id_item = self.tabla_pagos_model.item(fila, 0)
            if not pago_id_item:
                raise ValueError("No se encontró el item del ID de pago.")
            
            pago_id = int(pago_id_item.text())
            
            monto_item = self.tabla_pagos_model.item(fila, 2) # Columna "Monto" (índice 2)
            monto_str = monto_item.text() if monto_item else "[Monto desconocido]"

        except Exception as e:
            self.mostrar_mensaje("Error", f"No se pudo obtener el ID del pago: {e}", QMessageBox.Critical)
            return

        # Confirmación
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el pago de {monto_str}?\n\nEsta acción es irreversible y ajustará el saldo de la nota.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if respuesta == QMessageBox.No:
            return

        # Proceder con la eliminación
        try:
            nota_actualizada = api_client.eliminar_pago_proveedor(pago_id)
            
            if nota_actualizada:
                self.mostrar_mensaje("Éxito", "Pago eliminado y saldo revertido.", QMessageBox.Information)
                # Recargar toda la información de la nota
                self.cargar_nota(nota_actualizada)
            else:
                self.mostrar_mensaje("Error", "No se pudo eliminar el pago (respuesta nula de la BD).", QMessageBox.Critical)

        except ValueError as ve: # Errores de lógica de negocio
            self.mostrar_mensaje("Error de Validación", str(ve), QMessageBox.Critical)
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error inesperado al eliminar el pago: {e}", QMessageBox.Critical)

    def mostrar_mensaje(self, titulo, mensaje, tipo):
        """Muestra un mensaje al usuario (función existente)."""
        msg_box = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    
    try:
        from gui.api_client import api_client
        from dialogs.buscar_notas_proveedor_dialog import BuscarNotasProveedorDialog
        from gui.styles import *
    except ImportError as e:
        print(f"Error fatal en __main__: {e}")
        sys.path.insert(0, os.path.dirname(parent_dir))
        try:
            from gui.api_client import api_client
            from dialogs.buscar_notas_proveedor_dialog import BuscarNotasProveedorDialog
            from gui.styles import *
        except ImportError as e2:
            print(f"Error fatal en __main__ (segundo intento): {e2}")
            QMessageBox.critical(None, "Error de Importación", f"No se pudieron cargar las dependencias: {e2}")
            sys.exit(1)

    window = PagosNotaProveedorDialog()  
    window.show()
    sys.exit(app.exec_())
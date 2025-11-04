import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QGroupBox, QMessageBox, QTableView, QHeaderView, QFrame, 
    QWidget, QDateEdit, QApplication, QGridLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QFont

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from gui.db_helper import db_helper
    from gui.styles import (
        SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE,
        LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, MESSAGE_BOX_STYLE,
        FORM_BUTTON_STYLE
    )
except ImportError as e:
    print(f"Error de importación en EstadoCuentaProveedorDialog: {e}")
    # Definir estilos de fallback en caso de error
    SECONDARY_WINDOW_GRADIENT = "QDialog { background-color: #f0f0f0; }"
    BUTTON_STYLE_2 = "QPushButton { background-color: #00788E; color: white; padding: 10px; }"
    GROUP_BOX_STYLE = "QGroupBox { border: 1px solid #00788E; margin-top: 10px; }"
    LABEL_STYLE = "QLabel { color: white; font-weight: bold; background: transparent; }"
    INPUT_STYLE = "QDateEdit { padding: 5px; background-color: #F5F5F5; border-radius: 5px; border: 1px solid #CCC; }"
    TABLE_STYLE = "QTableView { background-color: white; }"
    MESSAGE_BOX_STYLE = "QMessageBox { background-color: white; }"
    FORM_BUTTON_STYLE = "QPushButton { background-color: #2CD5C4; color: white; padding: 8px; border-radius: 5px; }"

class EstadoCuentaProveedorDialog(QDialog):
    """
    Muestra el estado de cuenta de un proveedor, combinando notas y pagos.
    """
    def __init__(self, proveedor_id, proveedor_nombre, parent=None):
        super().__init__(parent)
        self.proveedor_id = proveedor_id
        self.proveedor_nombre = proveedor_nombre
        
        self.setWindowTitle(f"Estado de Cuenta - {self.proveedor_nombre}")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setMinimumSize(1000, 700)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        self.setup_ui()
        self.conectar_senales()
        self.cargar_datos()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.crear_grupo_filtros(main_layout)
        self.crear_tabla_estado_cuenta(main_layout)
        self.crear_panel_resumen(main_layout)
        
        # Botón de Cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_cerrar)
        
        main_layout.addLayout(bottom_layout)
        self.btn_cerrar = btn_cerrar

    def crear_grupo_filtros(self, parent_layout):
        grupo = QGroupBox()
        grupo.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QHBoxLayout()
        layout.setSpacing(10)

        lbl_ini = QLabel("Fecha Inicial:")
        lbl_ini.setStyleSheet(LABEL_STYLE)
        self.date_inicial = QDateEdit()
        self.date_inicial.setCalendarPopup(True)
        self.date_inicial.setDisplayFormat("dd/MM/yyyy")
        self.date_inicial.setStyleSheet(INPUT_STYLE)
        self.date_inicial.setDate(QDate.currentDate().addYears(-1))
        self.date_inicial.setFixedHeight(40) # <-- Altura fija
        
        lbl_fin = QLabel("Fecha Final:")
        lbl_fin.setStyleSheet(LABEL_STYLE)
        self.date_final = QDateEdit()
        self.date_final.setCalendarPopup(True)
        self.date_final.setDisplayFormat("dd/MM/yyyy")
        self.date_final.setStyleSheet(INPUT_STYLE)
        self.date_final.setDate(QDate.currentDate())
        self.date_final.setFixedHeight(40) # <-- Altura fija

        self.btn_filtrar = QPushButton("Generar Reporte")
        self.btn_filtrar.setStyleSheet(FORM_BUTTON_STYLE)
        self.btn_filtrar.setFixedHeight(50)

        layout.addWidget(lbl_ini, 0)
        layout.addWidget(self.date_inicial, 1)
        layout.addWidget(lbl_fin, 0)
        layout.addWidget(self.date_final, 1)
        layout.addStretch(2) # <-- Espacio flexible principal
        layout.addWidget(self.btn_filtrar, 0) # <-- Botón con estiramiento 0
        
        grupo.setLayout(layout)
        parent_layout.addWidget(grupo)

    def crear_tabla_estado_cuenta(self, parent_layout):
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels(
            ["Fecha", "Documento", "Concepto", "Cargo", "Abono", "Balance"]
        )
        
        self.tabla_statement = QTableView()
        self.tabla_statement.setModel(self.tabla_model)
        self.tabla_statement.setStyleSheet(TABLE_STYLE)
        self.tabla_statement.setEditTriggers(QTableView.NoEditTriggers)
        self.tabla_statement.setAlternatingRowColors(True)
        self.tabla_statement.setSelectionBehavior(QTableView.SelectRows)

        header = self.tabla_statement.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Fecha
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Documento
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Concepto
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Cargo
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Abono
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Balance
        
        parent_layout.addWidget(self.tabla_statement, 1) # Que la tabla crezca

    def crear_panel_resumen(self, parent_layout):
        """Crea el panel inferior con los totales del periodo."""
        totales_frame = QFrame()
        totales_frame.setFrameStyle(QFrame.StyledPanel)
        totales_frame.setStyleSheet("""
            QFrame {
                background: rgba(245, 245, 245, 250);
                border: 1px solid rgba(0, 120, 142, 0.2);
                border-radius: 8px;
                padding: 12px;
                margin-top: 10px;
            }
        """)
        
        main_layout = QHBoxLayout()
        main_layout.addStretch() # Empujar todo a la derecha

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        label_style = "QLabel { font-size: 16px; color: #333; background: transparent; }"
        valor_style = "QLabel { font-size: 16px; color: #00788E; font-weight: bold; background: transparent; }"
        
        # Definir estilos de saldo como atributos de clase
        base_saldo_style = "QLabel { font-size: 18px; font-weight: bold; background: transparent; color: %s; }"
        self.saldo_style_rojo = base_saldo_style % "#D32F2F"
        self.saldo_style_verde = base_saldo_style % "#006400" # Verde oscuro

        # Total Cargos (Notas de Proveedor)
        lbl_cargos_txt = QLabel("Total Cargos (Notas Prov):")
        lbl_cargos_txt.setStyleSheet(label_style)
        self.lbl_total_cargos = QLabel("$ 0.00")
        self.lbl_total_cargos.setStyleSheet(valor_style)
        self.lbl_total_cargos.setAlignment(Qt.AlignRight)
        
        # Total Abonos (Pagos a Proveedor)
        lbl_abonos_txt = QLabel("Total Abonos (Pagos Realizados):")
        lbl_abonos_txt.setStyleSheet(label_style)
        self.lbl_total_abonos = QLabel("$ 0.00")
        self.lbl_total_abonos.setStyleSheet(valor_style)
        self.lbl_total_abonos.setAlignment(Qt.AlignRight)
        
        # Saldo Final (Saldo por Pagar)
        lbl_saldo_txt = QLabel("Saldo por Pagar del Periodo:")
        lbl_saldo_txt.setStyleSheet(label_style + "font-weight: bold;")
        self.lbl_saldo_final = QLabel("$ 0.00")
        # Aplicar estilo rojo por defecto
        self.lbl_saldo_final.setStyleSheet(self.saldo_style_rojo)
        self.lbl_saldo_final.setAlignment(Qt.AlignRight)

        grid_layout.addWidget(lbl_cargos_txt, 0, 0)
        grid_layout.addWidget(self.lbl_total_cargos, 0, 1)
        grid_layout.addWidget(lbl_abonos_txt, 1, 0)
        grid_layout.addWidget(self.lbl_total_abonos, 1, 1)
        grid_layout.addWidget(lbl_saldo_txt, 2, 0)
        grid_layout.addWidget(self.lbl_saldo_final, 2, 1)

        main_layout.addLayout(grid_layout)
        totales_frame.setLayout(main_layout)
        parent_layout.addWidget(totales_frame)

    def conectar_senales(self):
        self.btn_filtrar.clicked.connect(self.cargar_datos)
        self.btn_cerrar.clicked.connect(self.accept)

    def cargar_datos(self):
        self.tabla_model.setRowCount(0)
        
        fecha_ini = self.date_inicial.date().toPyDate()
        fecha_fin = self.date_final.date().toPyDate()

        transacciones = []
        
        try:
            # 1. Obtener todas las notas del proveedor
            notas_proveedor = db_helper.buscar_notas_proveedor(proveedor_id=self.proveedor_id)
            
            if not notas_proveedor:
                self.mostrar_mensaje("Información", "El proveedor no tiene notas registradas.", QMessageBox.Information)
                return

            for nota in notas_proveedor:
                # Ignorar notas canceladas
                if nota.get('estado') == 'Cancelada':
                    continue
                
                # 2. Agregar la Nota (Cargo - Lo que debemos)
                nota_fecha = datetime.strptime(nota['fecha'], "%d/%m/%Y").date()
                if fecha_ini <= nota_fecha <= fecha_fin:
                    transacciones.append({
                        'fecha': nota_fecha,
                        'tipo': 'Nota',
                        'documento': nota['folio'],
                        'concepto': nota['observaciones'] or 'Nota de Proveedor',
                        'cargo': nota['total'],
                        'abono': 0
                    })
                
                # 3. Agregar los Pagos (Abono - Lo que pagamos)
                for pago in nota.get('pagos', []):
                    pago_fecha = datetime.strptime(pago['fecha_pago'], "%d/%m/%Y %H:%M").date()
                    if fecha_ini <= pago_fecha <= fecha_fin:
                        transacciones.append({
                            'fecha': pago_fecha,
                            'tipo': 'Pago',
                            'documento': nota['folio'], # Referencia a la nota que paga
                            'concepto': pago['memo'] or f"Pago ({pago['metodo_pago']})",
                            'cargo': 0,
                            'abono': pago['monto']
                        })

            # 4. Ordenar todas las transacciones por fecha
            transacciones.sort(key=lambda x: x['fecha'])

            # 5. Poblar la tabla y calcular balance corriente
            balance_actual = 0.0
            total_cargos = 0.0
            total_abonos = 0.0
            
            font_bold = QFont()
            font_bold.setBold(True)

            for trx in transacciones:
                balance_actual += (trx['cargo'] - trx['abono'])
                total_cargos += trx['cargo']
                total_abonos += trx['abono']
                
                item_fecha = QStandardItem(trx['fecha'].strftime("%d/%m/%Y"))
                item_doc = QStandardItem(trx['documento'])
                item_concepto = QStandardItem(trx['concepto'])
                
                # Cargo
                item_cargo = QStandardItem(f"${trx['cargo']:,.2f}" if trx['cargo'] > 0 else "")
                item_cargo.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Abono
                item_abono = QStandardItem(f"${trx['abono']:,.2f}" if trx['abono'] > 0 else "")
                item_abono.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item_abono.setForeground(QColor(0, 100, 0)) # Color verde oscuro para abonos
                
                # Balance
                item_balance = QStandardItem(f"${balance_actual:,.2f}")
                item_balance.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item_balance.setFont(font_bold)

                self.tabla_model.appendRow([
                    item_fecha, item_doc, item_concepto, item_cargo, item_abono, item_balance
                ])
            
            # 6. Actualizar panel de resumen
            self.lbl_total_cargos.setText(f"$ {total_cargos:,.2f}")
            self.lbl_total_abonos.setText(f"$ {total_abonos:,.2f}")
            self.lbl_saldo_final.setText(f"$ {balance_actual:,.2f}")
            
            # Si el saldo es positivo (debemos dinero), rojo. Si es negativo o cero (pagado), verde.
            if balance_actual > 0.01:
                self.lbl_saldo_final.setStyleSheet(self.saldo_style_rojo) # Rojo
            else:
                self.lbl_saldo_final.setStyleSheet(self.saldo_style_verde) # Verde

        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar datos: {e}", QMessageBox.Critical)
            import traceback
            traceback.print_exc()

    def mostrar_mensaje(self, titulo, mensaje, tipo):
        msg_box = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Simular la carga del diálogo (se necesita un ID de proveedor de la BD, ej: 1)
    try:
        dialog = EstadoCuentaProveedorDialog(proveedor_id=1, proveedor_nombre="Proveedor de Prueba (ID 1)")
        dialog.show()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"No se pudo iniciar: {e}\nAsegúrese de que la BD esté poblada.")
    
    sys.exit(app.exec_())
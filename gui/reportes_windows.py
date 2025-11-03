import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QDateEdit, QTableView, QHeaderView,
    QGroupBox, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE,
    LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, MESSAGE_BOX_STYLE
)


class ReportesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Reportes")
        self.setWindowFlags(
            self.windowFlags() | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowMaximizeButtonHint
        )

        self.setMinimumSize(1000, 700)
        self.setWindowState(Qt.WindowMaximized)
        self.setStyleSheet(SECONDARY_WINDOW_GRADIENT)

        # Datos de ejemplo para reportes
        self.datos_reportes = []
        
        self.setup_ui()
        self.cargar_datos_ejemplo()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Grupo de filtros
        self.crear_grupo_filtros(main_layout)

        # Tabla de resultados
        self.crear_tabla_reportes(main_layout)

        # Botones principales
        self.crear_botones_principales(main_layout)

        self.setLayout(main_layout)

    def crear_grupo_filtros(self, parent_layout):
        """Crear grupo de filtros para reportes"""
        grupo = QGroupBox("")
        grupo.setStyleSheet(GROUP_BOX_STYLE)

        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tipo de Reporte
        self.combo_tipo = self.crear_campo("Tipo de Reporte:", "combo")
        self.combo_tipo.addItems([
            "Ventas por Periodo",
            "Servicios Más Solicitados",
            "Clientes Frecuentes",
            "Inventario Bajo Stock",
            "Cuentas por Cobrar"
        ])
        layout.addLayout(self.crear_layout_campo("Tipo de Reporte:", self.combo_tipo))

        # Fecha Inicial
        self.fecha_inicial = self.crear_campo("Fecha Inicial:", "date")
        self.fecha_inicial.setDate(QDate.currentDate().addMonths(-1))
        layout.addLayout(self.crear_layout_campo("Fecha Inicial:", self.fecha_inicial))

        # Fecha Final
        self.fecha_final = self.crear_campo("Fecha Final:", "date")
        self.fecha_final.setDate(QDate.currentDate())
        layout.addLayout(self.crear_layout_campo("Fecha Final:", self.fecha_final))

        grupo.setLayout(layout)
        parent_layout.addWidget(grupo)

    def crear_campo(self, etiqueta, tipo):
        """Crear un campo según el tipo"""
        if tipo == "combo":
            campo = QComboBox()
            campo.setStyleSheet(INPUT_STYLE)
            campo.setFixedHeight(40)
        elif tipo == "date":
            campo = QDateEdit()
            campo.setStyleSheet(INPUT_STYLE)
            campo.setFixedHeight(40)
            campo.setCalendarPopup(True)
            campo.setDisplayFormat("dd/MM/yyyy")
        
        return campo

    def crear_layout_campo(self, etiqueta, campo):
        """Crear layout vertical con etiqueta y campo"""
        container = QVBoxLayout()
        container.setSpacing(2)

        lbl = QLabel(etiqueta)
        lbl.setStyleSheet(LABEL_STYLE)
        container.addWidget(lbl)
        container.addWidget(campo)
        
        return container

    def crear_tabla_reportes(self, parent_layout):
        """Crear tabla para mostrar resultados"""
        self.tabla_reportes = QTableView()
        self.tabla_reportes.setStyleSheet(TABLE_STYLE)
        self.tabla_reportes.setAlternatingRowColors(True)
        self.tabla_reportes.setSelectionBehavior(QTableView.SelectRows)
        self.tabla_reportes.setSelectionMode(QTableView.SingleSelection)

        # Modelo de la tabla
        self.tabla_model = QStandardItemModel()
        self.tabla_model.setHorizontalHeaderLabels([
            "ID", "Fecha", "Cliente", "Concepto", "Monto", "Estado"
        ])

        self.tabla_reportes.setModel(self.tabla_model)

        # Configuración de columnas
        header = self.tabla_reportes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.tabla_reportes.verticalHeader().setVisible(False)
        self.tabla_reportes.setMinimumHeight(300)

        parent_layout.addWidget(self.tabla_reportes)

    def crear_botones_principales(self, parent_layout):
        """Crear botones de acciones"""
        layout = QHBoxLayout()
        layout.setSpacing(15)

        botones = [
            ("Generar Reporte", self.generar_reporte),
            ("Exportar PDF", self.exportar_pdf),
            ("Exportar Excel", self.exportar_excel),
            ("Limpiar", self.limpiar_resultados),
            ("Cerrar", self.close)
        ]

        for texto, funcion in botones:
            btn = QPushButton(texto)
            btn.setStyleSheet(BUTTON_STYLE_2.replace("QToolButton", "QPushButton"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(funcion)
            layout.addWidget(btn)

        parent_layout.addLayout(layout)

    def generar_reporte(self):
        """Generar el reporte según los filtros seleccionados"""
        tipo = self.combo_tipo.currentText()
        fecha_ini = self.fecha_inicial.date().toString("dd/MM/yyyy")
        fecha_fin = self.fecha_final.date().toString("dd/MM/yyyy")

        # Limpiar tabla
        self.tabla_model.removeRows(0, self.tabla_model.rowCount())

        # Filtrar datos según el tipo de reporte
        datos_filtrados = [
            d for d in self.datos_reportes 
            if self.fecha_inicial.date() <= QDate.fromString(d['fecha'], "dd/MM/yyyy") 
            <= self.fecha_final.date()
        ]

        # Llenar tabla con datos filtrados
        for dato in datos_filtrados:
            fila = [
                QStandardItem(str(dato['id'])),
                QStandardItem(dato['fecha']),
                QStandardItem(dato['cliente']),
                QStandardItem(dato['concepto']),
                QStandardItem(f"${dato['monto']:,.2f}"),
                QStandardItem(dato['estado'])
            ]

            fila[0].setTextAlignment(Qt.AlignCenter)
            fila[1].setTextAlignment(Qt.AlignCenter)
            fila[4].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fila[5].setTextAlignment(Qt.AlignCenter)

            self.tabla_model.appendRow(fila)

        self.mostrar_mensaje(
            "Reporte Generado",
            f"Se generó el reporte '{tipo}'\n"
            f"Periodo: {fecha_ini} - {fecha_fin}\n"
            f"Registros encontrados: {len(datos_filtrados)}",
            QMessageBox.Information
        )

    def exportar_pdf(self):
        """Exportar reporte a PDF"""
        if self.tabla_model.rowCount() == 0:
            self.mostrar_mensaje(
                "Sin Datos",
                "Genera un reporte antes de exportar",
                QMessageBox.Warning
            )
            return

        self.mostrar_mensaje(
            "Exportar PDF",
            "Funcionalidad de exportación a PDF en desarrollo",
            QMessageBox.Information
        )

    def exportar_excel(self):
        """Exportar reporte a Excel"""
        if self.tabla_model.rowCount() == 0:
            self.mostrar_mensaje(
                "Sin Datos",
                "Genera un reporte antes de exportar",
                QMessageBox.Warning
            )
            return

        self.mostrar_mensaje(
            "Exportar Excel",
            "Funcionalidad de exportación a Excel en desarrollo",
            QMessageBox.Information
        )

    def limpiar_resultados(self):
        """Limpiar los resultados de la tabla"""
        self.tabla_model.removeRows(0, self.tabla_model.rowCount())

    def cargar_datos_ejemplo(self):
        """Cargar datos de ejemplo para los reportes"""
        self.datos_reportes = [
            {
                'id': 1, 'fecha': '15/09/2025', 'cliente': 'Juan Pérez',
                'concepto': 'Servicio de Mantenimiento', 'monto': 1500.00,
                'estado': 'Pagado'
            },
            {
                'id': 2, 'fecha': '20/09/2025', 'cliente': 'María López',
                'concepto': 'Reparación de Motor', 'monto': 3200.00,
                'estado': 'Pendiente'
            },
            {
                'id': 3, 'fecha': '25/09/2025', 'cliente': 'Carlos Ramírez',
                'concepto': 'Cambio de Aceite', 'monto': 450.00,
                'estado': 'Pagado'
            },
            {
                'id': 4, 'fecha': '01/10/2025', 'cliente': 'Ana Martínez',
                'concepto': 'Revisión General', 'monto': 800.00,
                'estado': 'Pagado'
            },
            {
                'id': 5, 'fecha': '05/10/2025', 'cliente': 'Luis González',
                'concepto': 'Cambio de Llantas', 'monto': 2100.00,
                'estado': 'Pendiente'
            }
        ]

    def mostrar_mensaje(self, titulo, mensaje, tipo):
        """Mostrar mensaje al usuario"""
        msg_box = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ReportesWindow()
    window.show()
    sys.exit(app.exec_())
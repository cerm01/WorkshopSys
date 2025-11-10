import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QDateEdit, QTableView, QHeaderView,
    QGroupBox, QMessageBox, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from gui.styles import (
    SECONDARY_WINDOW_GRADIENT, BUTTON_STYLE_2, GROUP_BOX_STYLE,
    LABEL_STYLE, INPUT_STYLE, TABLE_STYLE, MESSAGE_BOX_STYLE
)

from datetime import datetime
try:
    from gui.api_client import api_client as db_helper
    from gui.websocket_client import ws_client
except ImportError:
    print("Error: No se pudo importar 'api_client' o 'ws_client'.")
    sys.exit(1) 

try:
    from gui.pdf_generador import generar_pdf_reporte
except ImportError as e:
    print(f"Advertencia: No se pudo cargar pdf_generator (reportes): {e}")
    generar_pdf_reporte = None


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
        
        self.setup_ui()

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
        # Conectar el combo para habilitar/deshabilitar fechas
        self.combo_tipo.currentTextChanged.connect(self.actualizar_estado_fechas)
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
        
        # Estado inicial de fechas
        self.actualizar_estado_fechas(self.combo_tipo.currentText())

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
        self.tabla_reportes.setSortingEnabled(True) # Habilitar ordenamiento

        # Modelo de la tabla
        self.tabla_model = QStandardItemModel()
        # Headers iniciales (se cambiarán dinámicamente)
        self.tabla_model.setHorizontalHeaderLabels(["...", "...", "..."])

        self.tabla_reportes.setModel(self.tabla_model)

        # Configuración de columnas
        header = self.tabla_reportes.horizontalHeader()
        # Permitir que las columnas se ajusten
        header.setSectionResizeMode(QHeaderView.Interactive)

        self.tabla_reportes.verticalHeader().setVisible(False)
        self.tabla_reportes.setMinimumHeight(300)

        parent_layout.addWidget(self.tabla_reportes)

        self.ajustar_columnas_tabla()

    def crear_botones_principales(self, parent_layout):
        """Crear botones de acciones"""
        layout = QHBoxLayout()
        layout.setSpacing(15)

        botones = [
            ("Generar Reporte", self.generar_reporte),
            ("Exportar PDF", self.exportar_pdf),
            ("Exportar Excel", self.exportar_excel),
            ("Limpiar", self.limpiar_resultados)
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

    def showEvent(self, event):
        """
        Asegura que la ventana se muestre maximizada CADA VEZ que se abre.
        Esto soluciona el problema de que aparezca pequeña la segunda vez.
        """
        self.setWindowState(Qt.WindowMaximized)
        super().showEvent(event)
    
    def actualizar_estado_fechas(self, tipo_reporte):
        """Habilita o deshabilita los selectores de fecha según el reporte."""
        if tipo_reporte in ["Inventario Bajo Stock", "Cuentas por Cobrar"]:
            self.fecha_inicial.setEnabled(False)
            self.fecha_final.setEnabled(False)
        else:
            self.fecha_inicial.setEnabled(True)
            self.fecha_final.setEnabled(True)

    def generar_reporte(self):
        """Generar el reporte según los filtros seleccionados"""
        tipo = self.combo_tipo.currentText()
        
        # Obtener fechas como objetos date de Python
        fecha_ini = self.fecha_inicial.date().toPyDate()
        fecha_fin = self.fecha_final.date().toPyDate()
        
        # Convertir a datetime (ini al inicio del día, fin al final del día)
        fecha_ini_dt = datetime(fecha_ini.year, fecha_ini.month, fecha_ini.day, 0, 0, 0)
        fecha_fin_dt = datetime(fecha_fin.year, fecha_fin.month, fecha_fin.day, 23, 59, 59)
        self.tabla_model.clear() 

        try:
            datos_filtrados = []
            
            if tipo == "Ventas por Periodo":
                headers = ["Folio", "Fecha", "Cliente", "Total", "Saldo", "Estado"]
                self.tabla_model.setHorizontalHeaderLabels(headers) # Restablecer headers
                datos_filtrados = db_helper.get_reporte_ventas(fecha_ini_dt, fecha_fin_dt)
                self.poblar_tabla_ventas(datos_filtrados)
            
            elif tipo == "Servicios Más Solicitados":
                headers = ["Servicio/Producto", "Cantidad Vendida"]
                self.tabla_model.setHorizontalHeaderLabels(headers) # Restablecer headers
                datos_filtrados = db_helper.get_reporte_servicios(fecha_ini_dt, fecha_fin_dt)
                self.poblar_tabla_servicios(datos_filtrados)
            
            elif tipo == "Clientes Frecuentes":
                headers = ["Cliente", "Notas Emitidas", "Monto Total Comprado"]
                self.tabla_model.setHorizontalHeaderLabels(headers) # Restablecer headers
                datos_filtrados = db_helper.get_reporte_clientes(fecha_ini_dt, fecha_fin_dt)
                self.poblar_tabla_clientes(datos_filtrados)

            elif tipo == "Inventario Bajo Stock":
                headers = ["Código", "Nombre", "Categoría", "Stock Actual", "Stock Mínimo"]
                self.tabla_model.setHorizontalHeaderLabels(headers) # Restablecer headers
                # Este reporte no usa fechas
                datos_filtrados = db_helper.get_reporte_inventario_bajo_stock()
                self.poblar_tabla_inventario(datos_filtrados)

            elif tipo == "Cuentas por Cobrar":
                headers = ["Folio", "Fecha", "Cliente", "Total", "Pagado", "Saldo", "Estado"]
                self.tabla_model.setHorizontalHeaderLabels(headers) # Restablecer headers
                # Este reporte no usa fechas
                datos_filtrados = db_helper.get_reporte_cuentas_por_cobrar()
                self.poblar_tabla_cxc(datos_filtrados)

            self.ajustar_columnas_tabla()
            
            self.mostrar_mensaje(
                "Reporte Generado",
                f"Se generó el reporte '{tipo}'\n"
                f"Registros encontrados: {len(datos_filtrados)}",
                QMessageBox.Information
            )

        except Exception as e:
            self.mostrar_mensaje(
                "Error de Base de Datos",
                f"No se pudo generar el reporte: {e}",
                QMessageBox.Critical
            )
            import traceback
            traceback.print_exc()
            
    def ajustar_columnas_tabla(self):
        """Ajusta las columnas para que se repartan el espacio equitativamente."""
        for i in range(self.tabla_model.columnCount()):
            self.tabla_reportes.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

    def _formatear_fecha_iso(self, fecha_iso):
        """Convierte '2025-11-06T00:00:00' a '2025-11-06'."""
        if 'T' in fecha_iso:
            return fecha_iso.split('T')[0]
        return fecha_iso
    
    def poblar_tabla_ventas(self, datos):
        for dato in datos:
            fecha_formateada = self._formatear_fecha_iso(dato['fecha'])
            fila = [
                QStandardItem(dato['folio']),
                QStandardItem(fecha_formateada), # Fecha formateada
                QStandardItem(dato['cliente_nombre']),
                QStandardItem(f"${dato['total']:,.2f}"),
                QStandardItem(f"${dato['saldo']:,.2f}"),
                QStandardItem(dato['estado'])
            ]
            # Alineaciones
            fila[3].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fila[4].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fila[5].setTextAlignment(Qt.AlignCenter)
            self.tabla_model.appendRow(fila)

    def poblar_tabla_servicios(self, datos):
        for dato in datos:
            fila = [
                QStandardItem(dato['descripcion']),
                QStandardItem(str(dato['total_vendido']))
            ]
            fila[1].setTextAlignment(Qt.AlignCenter)
            self.tabla_model.appendRow(fila)

    def poblar_tabla_clientes(self, datos):
        for dato in datos:
            fila = [
                QStandardItem(dato['cliente']),
                QStandardItem(str(dato['total_notas'])),
                QStandardItem(f"${dato['monto_total']:,.2f}")
            ]
            fila[1].setTextAlignment(Qt.AlignCenter)
            fila[2].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla_model.appendRow(fila)

    def poblar_tabla_inventario(self, datos):
        for dato in datos:
            fila = [
                QStandardItem(dato['codigo']),
                QStandardItem(dato['nombre']),
                QStandardItem(dato['categoria']),
                QStandardItem(str(dato['stock_actual'])),
                QStandardItem(str(dato['stock_min']))
            ]
            fila[3].setTextAlignment(Qt.AlignCenter)
            fila[4].setTextAlignment(Qt.AlignCenter)
            self.tabla_model.appendRow(fila)

    def poblar_tabla_cxc(self, datos):
        for dato in datos:
            fecha_formateada = self._formatear_fecha_iso(dato['fecha'])
            fila = [
                QStandardItem(dato['folio']),
                QStandardItem(fecha_formateada), # Fecha formateada
                QStandardItem(dato['cliente_nombre']),
                QStandardItem(f"${dato['total']:,.2f}"),
                QStandardItem(f"${dato['total_pagado']:,.2f}"),
                QStandardItem(f"${dato['saldo']:,.2f}"),
                QStandardItem(dato['estado'])
            ]
            # Alineaciones
            fila[3].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fila[4].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fila[5].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            fila[6].setTextAlignment(Qt.AlignCenter)
            self.tabla_model.appendRow(fila)

    def exportar_pdf(self):
        """Exportar reporte a PDF"""
        if self.tabla_model.rowCount() == 0:
            self.mostrar_mensaje(
                "Sin Datos",
                "Genera un reporte antes de exportar",
                QMessageBox.Warning
            )
            return

        if not generar_pdf_reporte:
            self.mostrar_mensaje("Error", "El módulo de generación de PDF no está disponible.", QMessageBox.Critical)
            return
        
        try:
            # 1. Obtener datos de la empresa
            empresa_data = db_helper.get_config_empresa()
            if not empresa_data:
                self.mostrar_mensaje("Error", "No se pudieron obtener los datos de la empresa.", QMessageBox.Critical)
                return

            # 2. Obtener datos del reporte
            tipo = self.combo_tipo.currentText()
            fecha_ini_str = self.fecha_inicial.date().toString("dd/MM/yyyy")
            fecha_fin_str = self.fecha_final.date().toString("dd/MM/yyyy")
            fechas_habilitadas = self.fecha_inicial.isEnabled()
            
            # 3. Obtener Headers
            headers = []
            for i in range(self.tabla_model.columnCount()):
                headers.append(self.tabla_model.headerData(i, Qt.Horizontal))
            
            # 4. Obtener Datos
            data = []
            for row in range(self.tabla_model.rowCount()):
                row_data = []
                for col in range(self.tabla_model.columnCount()):
                    row_data.append(self.tabla_model.item(row, col).text())
                data.append(row_data)

            # 5. Preguntar dónde guardar
            default_filename = f"Reporte_{tipo.replace(' ', '_')}_{self.fecha_final.date().toString('yyyyMMdd')}.pdf"
            
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar PDF de Reporte",
                default_filename,
                "Archivos PDF (*.pdf)"
            )
            
            if save_path:
                # 6. Generar PDF
                exito = generar_pdf_reporte(
                    titulo_reporte=tipo,
                    fecha_ini_str=fecha_ini_str,
                    fecha_fin_str=fecha_fin_str,
                    headers=headers,
                    data=data,
                    empresa_data=empresa_data,
                    save_path=save_path,
                    fechas_habilitadas=fechas_habilitadas
                )

                if exito:
                    self.mostrar_mensaje("Éxito", f"PDF generado exitosamente en:\n{save_path}", QMessageBox.Information)
                    # 7. Abrir archivo
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
                    self.mostrar_mensaje("Error", "Ocurrió un error al generar el archivo PDF.", QMessageBox.Critical)
        
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al preparar la impresión: {e}", QMessageBox.Critical)
            import traceback
            traceback.print_exc()

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
            self.tabla_model.clear()
            self.tabla_model.setHorizontalHeaderLabels(["...", "...", "..."])
            self.ajustar_columnas_tabla()

    def mostrar_mensaje(self, titulo, mensaje, tipo):
        """Mostrar mensaje al usuario"""
        msg_box = QMessageBox(tipo, titulo, mensaje, QMessageBox.Ok, self)
        msg_box.setStyleSheet(MESSAGE_BOX_STYLE)
        msg_box.exec_()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    try:
        from gui.api_client import api_client as db_helper
    except ImportError:
        print("Error: No se pudo importar api_client. Asegúrate de que el servidor esté corriendo.")
        sys.exit(1)
        
    window = ReportesWindow()
    window.show()
    sys.exit(app.exec_())
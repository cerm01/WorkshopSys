from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import sys
import os
import traceback
import base64
from sqlalchemy.orm import joinedload

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_sync, SessionLocal
from server import crud
import json
from datetime import datetime

from server.models import (
    Cliente, Proveedor, Producto, MovimientoInventario,
    Orden, OrdenItem, Cotizacion, CotizacionItem,
    NotaVenta, NotaVentaItem, NotaVentaPago, Usuario,
    NotaProveedor, NotaProveedorItem, NotaProveedorPago,
    ConfigEmpresa
)

from pydantic import BaseModel
from server.crud import verificar_credenciales

app = FastAPI(title="Taller API Distribuida")

# Modelo Pydantic para el login
class LoginData(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== LOGIN ====================
@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    # verificar_credenciales ya existe en crud.py
    usuario = verificar_credenciales(db, data.username, data.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    # _usuario_to_dict ya está definido al final de main.py
    return _usuario_to_dict(usuario)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== WEBSOCKET MANAGER ====================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"status": "connected"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== CLIENTES ====================
@app.get("/clientes")
def get_clientes(db: Session = Depends(get_db)):
    clientes = crud.get_all_clientes(db)
    return [_cliente_to_dict(c) for c in clientes]

@app.get("/clientes/buscar/{texto}")
def buscar_clientes(texto: str, db: Session = Depends(get_db)):
    clientes = crud.search_clientes(db, texto)
    return [_cliente_to_dict(c) for c in clientes]

@app.post("/clientes")
async def crear_cliente(datos: Dict[str, Any], db: Session = Depends(get_db)):
    cliente = crud.create_cliente(db, datos)
    await manager.broadcast({
        "type": "cliente_creado",
        "data": _cliente_to_dict(cliente)
    })
    return _cliente_to_dict(cliente)

@app.put("/clientes/{cliente_id}")
async def actualizar_cliente(cliente_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    cliente = crud.update_cliente(db, cliente_id, datos)
    if cliente:
        await manager.broadcast({
            "type": "cliente_actualizado",
            "data": _cliente_to_dict(cliente)
        })
        return _cliente_to_dict(cliente)
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

@app.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    success = crud.delete_cliente(db, cliente_id)
    if success:
        await manager.broadcast({
            "type": "cliente_eliminado",
            "data": {"id": cliente_id}
        })
        return {"success": True}
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

# ==================== PROVEEDORES ====================
@app.get("/proveedores")
def get_proveedores(db: Session = Depends(get_db)):
    proveedores = crud.get_all_proveedores(db)
    return [_proveedor_to_dict(p) for p in proveedores]

@app.get("/proveedores/buscar/{texto}")
def buscar_proveedores_api(texto: str, db: Session = Depends(get_db)):
    proveedores = crud.search_proveedores(db, texto)
    return [_proveedor_to_dict(p) for p in proveedores]

@app.post("/proveedores")
async def crear_proveedor(datos: Dict[str, Any], db: Session = Depends(get_db)):
    proveedor = crud.create_proveedor(db, datos)
    await manager.broadcast({
        "type": "proveedor_creado",
        "data": _proveedor_to_dict(proveedor)
    })
    return _proveedor_to_dict(proveedor)

@app.put("/proveedores/{proveedor_id}")
async def actualizar_proveedor_api(proveedor_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    proveedor = crud.update_proveedor(db, proveedor_id, datos)
    if proveedor:
        await manager.broadcast({
            "type": "proveedor_actualizado",
            "data": _proveedor_to_dict(proveedor)
        })
        return _proveedor_to_dict(proveedor)
    raise HTTPException(status_code=404, detail="Proveedor no encontrado")

@app.delete("/proveedores/{proveedor_id}")
async def eliminar_proveedor_api(proveedor_id: int, db: Session = Depends(get_db)):
    success = crud.delete_proveedor(db, proveedor_id)
    if success:
        await manager.broadcast({
            "type": "proveedor_eliminado",
            "data": {"id": proveedor_id}
        })
        return {"success": True}
    raise HTTPException(status_code=404, detail="Proveedor no encontrado")

# ==================== PRODUCTOS ====================
@app.get("/productos")
def get_productos(db: Session = Depends(get_db)):
    productos = crud.get_all_productos(db)
    return [_producto_to_dict(p) for p in productos]

@app.get("/productos/buscar/{texto}")
def buscar_productos(texto: str, db: Session = Depends(get_db)):
    productos = crud.search_productos(db, texto)
    return [_producto_to_dict(p) for p in productos]

@app.post("/productos")
async def crear_producto(datos: Dict[str, Any], db: Session = Depends(get_db)):
    producto = crud.create_producto(db, datos)
    await manager.broadcast({
        "type": "producto_creado",
        "data": _producto_to_dict(producto)
    })
    
    if producto.stock_actual > 0:
        await manager.broadcast({
            "type": "stock_actualizado",
            "data": {
                "producto_id": producto.id,
                "tipo": "Entrada",
                "cantidad": producto.stock_actual
            }
        })
        
    return _producto_to_dict(producto)

@app.put("/productos/{producto_id}")
async def actualizar_producto(producto_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    producto = crud.update_producto(db, producto_id, datos)
    if producto:
        await manager.broadcast({
            "type": "producto_actualizado",
            "data": _producto_to_dict(producto)
        })
        return _producto_to_dict(producto)
    raise HTTPException(status_code=404)

@app.delete("/productos/{producto_id}")
async def eliminar_producto_api(producto_id: int, db: Session = Depends(get_db)):
    # Usamos soft_delete=True por defecto como en crud.py
    success = crud.delete_producto(db, producto_id, soft_delete=True)
    if success:
        await manager.broadcast({
            "type": "producto_eliminado",
            "data": {"id": producto_id}
        })
        return {"success": True}
    raise HTTPException(status_code=404, detail="Producto no encontrado")

# ==================== ORDENES ====================
@app.get("/ordenes")
def get_ordenes(estado: str = None, db: Session = Depends(get_db)):
    ordenes = crud.get_all_ordenes(db, estado=estado)
    return [_orden_to_dict(o) for o in ordenes]

@app.post("/ordenes")
async def crear_orden(datos: Dict[str, Any], db: Session = Depends(get_db)):
    items = datos.pop('items', [])

    if 'fecha_recepcion' in datos and isinstance(datos['fecha_recepcion'], str):
        try:
            datos['fecha_recepcion'] = datetime.fromisoformat(datos['fecha_recepcion'])
        except ValueError:
            datos['fecha_recepcion'] = datetime.now()
    elif 'fecha_recepcion' not in datos:
         datos['fecha_recepcion'] = datetime.now()

    orden = crud.create_orden(db, datos, items)
    await manager.broadcast({
        "type": "orden_creada",
        "data": _orden_to_dict(orden)
    })
    return _orden_to_dict(orden)

@app.get("/ordenes/buscar")
def buscar_ordenes_api(folio: str, db: Session = Depends(get_db)):
    """Busca órdenes por folio (usado por la UI)"""
    ordenes = crud.search_ordenes_by_folio(db, folio)
    return [_orden_to_dict(o) for o in ordenes]

@app.get("/ordenes/{orden_id}")
def get_orden_por_id(orden_id: int, db: Session = Depends(get_db)):
    orden = crud.get_orden(db, orden_id)
    if orden:
        return _orden_to_dict(orden)
    raise HTTPException(status_code=404, detail="Orden no encontrada")

@app.put("/ordenes/{orden_id}")
async def actualizar_orden_api(orden_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        items = datos.pop('items', None) 

        if 'fecha_recepcion' in datos and isinstance(datos['fecha_recepcion'], str):
            try:
                datos['fecha_recepcion'] = datetime.fromisoformat(datos['fecha_recepcion'])
            except ValueError:
                datos.pop('fecha_recepcion')
        
        orden = crud.update_orden(
            db=db,
            orden_id=orden_id,
            orden_data=datos,
            items=items
        )
        
        if not orden:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
            
        await manager.broadcast({
            "type": "orden_actualizada", 
            "data": _orden_to_dict(orden)
        })
        return _orden_to_dict(orden)
        
    except Exception as e:
        print(f"Error al actualizar orden API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ordenes/{orden_id}/cancelar")
async def cancelar_orden_api(orden_id: int, db: Session = Depends(get_db)):
    try:
        orden = crud.cambiar_estado_orden(db, orden_id, "Cancelada")
        if not orden:
             raise HTTPException(status_code=400, detail="No se pudo cancelar la orden")
        
        await manager.broadcast({
            "type": "orden_actualizada",
            "data": _orden_to_dict(orden)
        })
        return _orden_to_dict(orden)
    
    except Exception as e:
        print(f"Error al cancelar orden API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== COTIZACIONES ====================
@app.get("/cotizaciones")
def get_cotizaciones(estado: str = None, db: Session = Depends(get_db)):
    cotizaciones = crud.get_all_cotizaciones(db, estado=estado)
    return [_cotizacion_to_dict(c) for c in cotizaciones]

@app.post("/cotizaciones")
async def crear_cotizacion(datos: Dict[str, Any], db: Session = Depends(get_db)):
    items = datos.pop('items', [])
    cotizacion = crud.create_cotizacion(db, datos, items)
    await manager.broadcast({
        "type": "cotizacion_creada",
        "data": _cotizacion_to_dict(cotizacion)
    })
    return _cotizacion_to_dict(cotizacion)

@app.get("/cotizaciones/buscar")
def buscar_cotizaciones_api(folio: str, db: Session = Depends(get_db)):
    """Busca cotizaciones por folio (usado por la UI)"""
    cotizaciones = crud.search_cotizaciones_by_folio(db, folio)
    return [_cotizacion_to_dict(c) for c in cotizaciones]

@app.put("/cotizaciones/{cotizacion_id}")
async def actualizar_cotizacion_api(cotizacion_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        items = datos.pop('items', [])
        nota_folio = datos.pop('nota_folio', None) # Extraer el nota_folio

        # Convertir fecha si viene
        if 'vigencia' in datos and isinstance(datos['vigencia'], str):
            try:
                # El cliente GUI la envía como 'dd/MM/yyyy'
                fecha_obj = datetime.strptime(datos['vigencia'], '%d/%m/%Y').date()
                datos['vigencia'] = fecha_obj
            except ValueError as e:
                print(f"Advertencia: Fecha de vigencia inválida: {e}")
                datos.pop('vigencia') 
        
        cotizacion = crud.update_cotizacion(
            db=db,
            cotizacion_id=cotizacion_id,
            cotizacion_data=datos,
            items=items,
            nota_folio=nota_folio # Pasarlo al CRUD
        )
        
        if not cotizacion:
            raise HTTPException(status_code=404, detail="Cotización no encontrada")
            
        await manager.broadcast({
            "type": "cotizacion_actualizada", 
            "data": _cotizacion_to_dict(cotizacion)
        })
        return _cotizacion_to_dict(cotizacion)
        
    except Exception as e:
        print(f"Error al actualizar cotización API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/cotizaciones/buscar")
def buscar_cotizaciones_api(folio: Optional[str] = None, cliente_id: Optional[int] = None, db: Session = Depends(get_db)):
    cotizaciones = crud.search_cotizaciones(db, folio=folio, cliente_id=cliente_id)
    return [_cotizacion_to_dict(c) for c in cotizaciones]

@app.get("/cotizaciones/{cotizacion_id}")
def get_cotizacion_por_id(cotizacion_id: int, db: Session = Depends(get_db)):
    cotizacion = crud.get_cotizacion(db, cotizacion_id)
    if cotizacion:
        return _cotizacion_to_dict(cotizacion)
    raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
@app.post("/cotizaciones/{cotizacion_id}/cancelar")
async def cancelar_cotizacion_api(cotizacion_id: int, db: Session = Depends(get_db)):
    try:
        success = crud.cancelar_cotizacion(db, cotizacion_id)
        if not success:
             raise HTTPException(status_code=400, detail="No se pudo cancelar la cotización (ya aceptada o cancelada)")
        
        cotizacion = crud.get_cotizacion(db, cotizacion_id) 
        await manager.broadcast({
            "type": "cotizacion_actualizada", # Usamos señal genérica
            "data": _cotizacion_to_dict(cotizacion)
        })
        return _cotizacion_to_dict(cotizacion)
    
    except Exception as e:
        print(f"Error al cancelar cotización API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== NOTAS DE VENTA (CON DEBUG) ====================
@app.post("/notas")
async def crear_nota(datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        print("\n" + "="*60)
        print("📥 DATOS RECIBIDOS DEL CLIENTE:")
        print(f"   Datos completos: {datos}")
        print(f"   Tipo de datos: {type(datos)}")
        print("="*60 + "\n")
        
        items = datos.pop('items', [])
        estado = datos.pop('estado', 'Registrado')
        cotizacion_folio = datos.pop('cotizacion_folio', None)
        orden_folio = datos.pop('orden_folio', None)

        print(f"📦 Items extraídos: {items}")
        print(f"🏷️  Estado: {estado}")
        print(f"📋 Datos nota: {datos}")
        
        if 'fecha' in datos:
            print(f"📅 Fecha recibida: '{datos['fecha']}' (tipo: {type(datos['fecha'])})")
            if isinstance(datos['fecha'], str):
                try:
                    fecha_obj = datetime.strptime(datos['fecha'], '%Y-%m-%d')
                    datos['fecha'] = fecha_obj
                    print(f"✅ Fecha convertida: {fecha_obj}")
                except ValueError as ve:
                    print(f"⚠️  Error convirtiendo fecha: {ve}")
                    datos['fecha'] = datetime.now()

        print(f"\n🔧 Llamando crud.create_nota_venta...")
        nota = crud.create_nota_venta(db, nota_data=datos, items=items, estado=estado)
        print(f"✅ Nota creada: ID={nota.id}, Folio={nota.folio}")

        if cotizacion_folio or orden_folio:
            nota.cotizacion_folio = cotizacion_folio
            nota.orden_folio = orden_folio
            db.commit()
            db.refresh(nota)

        await manager.broadcast({"type": "nota_creada", "data": {"id": nota.id}})
        
        resultado = _nota_to_dict(nota)
        print(f"📤 Retornando: {resultado}\n")
        return resultado
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR AL CREAR NOTA:")
        print(f"   Mensaje: {str(e)}")
        print(f"   Tipo: {type(e).__name__}")
        print("\n📜 TRACEBACK COMPLETO:")
        print(traceback.format_exc())
        print("="*60 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notas")
def get_notas(db: Session = Depends(get_db)):
    notas = crud.get_all_notas(db) 
    return [_nota_to_dict(n) for n in notas]

@app.get("/notas/buscar")
def buscar_notas_api(
    folio: Optional[str] = None, 
    cliente_id: Optional[int] = None, 
    estado: Optional[str] = None,
    orden_folio: Optional[str] = None,
    cotizacion_folio: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Busca notas de venta por varios criterios"""
    notas = crud.search_notas(
        db, 
        folio=folio, 
        cliente_id=cliente_id, 
        estado=estado, 
        orden_folio=orden_folio,
        cotizacion_folio=cotizacion_folio
    )
    return [_nota_to_dict(n) for n in notas]

@app.get("/notas/{nota_id}")
def get_nota_por_id(nota_id: int, db: Session = Depends(get_db)):
    nota = crud.get_nota(db, nota_id)
    if nota:
        return _nota_to_dict(nota)
    raise HTTPException(status_code=404, detail="Nota no encontrada")

@app.put("/notas/{nota_id}")
async def actualizar_nota_api(nota_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        items = datos.pop('items', [])
        
        # Convertir fecha si viene
        if 'fecha' in datos and isinstance(datos['fecha'], str):
            try:
                # El cliente GUI la envía como 'yyyy-MM-dd'
                fecha_obj = datetime.strptime(datos['fecha'], '%Y-%m-%d').date()
                datos['fecha'] = fecha_obj
            except ValueError as ve:
                print(f"Advertencia: Fecha inválida, no se actualizará: {e}")
                datos.pop('fecha') # No actualizar si es inválida
        
        nota = crud.update_nota_venta(
            db=db,
            nota_id=nota_id,
            nota_data=datos,
            items=items
        )
        
        if not nota:
            raise HTTPException(status_code=404, detail="Nota no encontrada")
            
        await manager.broadcast({
            "type": "nota_actualizada", # Usamos una señal genérica
            "data": _nota_to_dict(nota)
        })
        return _nota_to_dict(nota)
        
    except Exception as e:
        print(f"Error al actualizar nota API: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/notas/{nota_id}/cancelar")
async def cancelar_nota_api(nota_id: int, db: Session = Depends(get_db)):
    try:
        # La función crud.cancelar_nota devuelve True/False
        success = crud.cancelar_nota(db, nota_id)
        if not success:
             raise HTTPException(status_code=400, detail="No se pudo cancelar la nota (ya pagada o cancelada)")
        
        # Si fue exitoso, obtenemos la nota actualizada para devolverla
        nota = crud.get_nota(db, nota_id) 
        await manager.broadcast({
            "type": "nota_actualizada",
            "data": _nota_to_dict(nota)
        })
        return _nota_to_dict(nota)
    
    except Exception as e:
        print(f"Error al cancelar nota API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/notas/{nota_id}/pagar")
async def registrar_pago_api(nota_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        # El cliente enviará la fecha como string ISO (YYYY-MM-DD)
        fecha_pago_obj = datetime.fromisoformat(datos['fecha_pago']).date()

        nota = crud.registrar_pago_nota(
            db=db,
            nota_id=nota_id,
            monto=float(datos['monto']),
            fecha_pago=fecha_pago_obj,
            metodo_pago=datos['metodo_pago'],
            memo=datos['memo']
        )
        await manager.broadcast({
            "type": "nota_actualizada", # Usamos una señal genérica
            "data": _nota_to_dict(nota)
        })
        return _nota_to_dict(nota)
    except Exception as e:
        print(f"Error al registrar pago API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/pagos/{pago_id}")
async def eliminar_pago_api(pago_id: int, db: Session = Depends(get_db)):
    try:
        nota = crud.eliminar_pago_nota(db, pago_id)
        await manager.broadcast({
            "type": "nota_actualizada",
            "data": _nota_to_dict(nota)
        })
        return _nota_to_dict(nota)
    except Exception as e:
        print(f"Error al eliminar pago API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== MOVIMIENTOS INVENTARIO ====================
@app.get("/inventario/movimientos")
def get_movimientos_api(
    producto_id: Optional[int] = None, 
    tipo: Optional[str] = None, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    try:
        movimientos = crud.get_movimientos_inventario(
            db, 
            producto_id=producto_id, 
            tipo=tipo, 
            limit=limit
        )
        # Usamos el nuevo _movimiento_to_dict que añadiremos abajo
        return [_movimiento_to_dict(m) for m in movimientos]
    except Exception as e:
        print(f"Error al obtener movimientos API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inventario/movimiento")
async def crear_movimiento(datos: Dict[str, Any], db: Session = Depends(get_db)):
    movimiento = crud.registrar_movimiento_inventario(
        db,
        producto_id=datos['producto_id'],
        tipo=datos['tipo'],
        cantidad=datos['cantidad'],
        motivo=datos['motivo'],
        usuario=datos.get('usuario', 'Sistema')
    )
    
    try:
        db.commit()
        db.refresh(movimiento)
    except Exception as e:
        db.rollback()
        print(f"Error al hacer commit del movimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar: {e}")

    await manager.broadcast({
        "type": "stock_actualizado",
        "data": {
            "producto_id": datos['producto_id'],
            "tipo": datos['tipo'],
            "cantidad": datos['cantidad']
        }
    })
    return {"success": True}

# ==================== REPORTES ====================

@app.get("/reportes/ventas")
def get_reporte_ventas(fecha_ini: datetime, fecha_fin: datetime, db: Session = Depends(get_db)):
    try:
        # Llama a la función existente en crud.py
        notas = crud.get_reporte_ventas_por_periodo(db, fecha_ini, fecha_fin)
        # Serializa los resultados usando la función _nota_to_dict que ya existe
        return [_nota_to_dict(n) for n in notas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reportes/servicios")
def get_reporte_servicios(fecha_ini: datetime, fecha_fin: datetime, db: Session = Depends(get_db)):
    try:
        # Llama a la función existente en crud.py
        resultados = crud.get_reporte_servicios_mas_solicitados(db, fecha_ini, fecha_fin)
        # Serializa la respuesta (lista de tuplas)
        return [{"descripcion": r[0], "total_vendido": r[1]} for r in resultados]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reportes/clientes")
def get_reporte_clientes(fecha_ini: datetime, fecha_fin: datetime, db: Session = Depends(get_db)):
    try:
        # Llama a la función existente en crud.py
        resultados = crud.get_reporte_clientes_frecuentes(db, fecha_ini, fecha_fin)
        # Serializa la respuesta (lista de tuplas)
        return [{"cliente": r[0], "total_notas": r[1], "monto_total": r[2]} for r in resultados]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reportes/inventario_bajo")
def get_reporte_inventario_bajo(db: Session = Depends(get_db)):
    try:
        # Llama a la función existente en crud.py (get_productos_bajo_stock)
        productos = crud.get_productos_bajo_stock(db)
        return [_producto_to_dict(p) for p in productos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reportes/cxc")
def get_reporte_cxc(db: Session = Depends(get_db)):
    try:
        # Llama a la función existente en crud.py
        notas = crud.get_reporte_cuentas_por_cobrar(db)
        return [_nota_to_dict(n) for n in notas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== NOTAS DE PROVEEDOR ====================
@app.post("/notas_proveedor")
async def crear_nota_proveedor_api(datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        items = datos.pop('items', [])
        
        if 'fecha' in datos and isinstance(datos['fecha'], str):
            try:
                # Convertir de ISO 'YYYY-MM-DD'
                datos['fecha'] = datetime.fromisoformat(datos['fecha'])
            except ValueError:
                datos['fecha'] = datetime.now()

        nota = crud.create_nota_proveedor(db, nota_data=datos, items=items)
        
        await manager.broadcast({
            "type": "nota_proveedor_creada", 
            "data": _nota_proveedor_to_dict(nota)
        })
        return _nota_proveedor_to_dict(nota)
        
    except Exception as e:
        print(f"Error al crear nota proveedor API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/notas_proveedor/{nota_id}")
async def actualizar_nota_proveedor_api(nota_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        items = datos.pop('items', [])
        
        if 'fecha' in datos and isinstance(datos['fecha'], str):
            try:
                # Convertir de ISO 'YYYY-MM-DD'
                datos['fecha'] = datetime.fromisoformat(datos['fecha'])
            except ValueError:
                datos.pop('fecha') 
        
        nota = crud.update_nota_proveedor(
            db=db,
            nota_id=nota_id,
            nota_data=datos,
            items=items
        )
        
        if not nota:
            raise HTTPException(status_code=404, detail="Nota de proveedor no encontrada")
            
        await manager.broadcast({
            "type": "nota_proveedor_actualizada", 
            "data": _nota_proveedor_to_dict(nota)
        })
        return _nota_proveedor_to_dict(nota)
        
    except Exception as e:
        print(f"Error al actualizar nota proveedor API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/notas_proveedor")
def get_notas_proveedor(db: Session = Depends(get_db)):
    notas = crud.get_all_notas_proveedor(db)
    return [_nota_proveedor_to_dict(n) for n in notas]

@app.get("/notas_proveedor/buscar")
def buscar_notas_proveedor_api(
    folio: Optional[str] = None, 
    proveedor_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(NotaProveedor).options(joinedload(NotaProveedor.proveedor))
    if folio:
        query = query.filter(NotaProveedor.folio.ilike(f"%{folio}%"))
    if proveedor_id:
        query = query.filter(NotaProveedor.proveedor_id == proveedor_id)
    
    notas = query.order_by(NotaProveedor.fecha.desc()).all()
    return [_nota_proveedor_to_dict(n) for n in notas]


@app.get("/notas_proveedor/{nota_id}")
def get_nota_proveedor(nota_id: int, db: Session = Depends(get_db)):
    nota = crud.get_nota_proveedor(db, nota_id)
    if nota:
        return _nota_proveedor_to_dict(nota)
    raise HTTPException(status_code=404, detail="Nota de proveedor no encontrada")

@app.post("/notas_proveedor/{nota_id}/pagar")
async def registrar_pago_proveedor_api(nota_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        fecha_pago_obj = datetime.fromisoformat(datos['fecha_pago']).date()

        nota = crud.registrar_pago_nota_proveedor(
            db=db,
            nota_id=nota_id,
            monto=float(datos['monto']),
            fecha_pago=fecha_pago_obj,
            metodo_pago=datos['metodo_pago'],
            memo=datos['memo']
        )
        await manager.broadcast({
            "type": "nota_proveedor_actualizada",
            "data": _nota_proveedor_to_dict(nota)
        })
        return _nota_proveedor_to_dict(nota)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/pagos_proveedor/{pago_id}")
async def eliminar_pago_proveedor_api(pago_id: int, db: Session = Depends(get_db)):
    try:
        nota = crud.eliminar_pago_nota_proveedor(db, pago_id)
        await manager.broadcast({
            "type": "nota_proveedor_actualizada",
            "data": _nota_proveedor_to_dict(nota)
        })
        return _nota_proveedor_to_dict(nota)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/notas_proveedor/{nota_id}/cancelar")
async def cancelar_nota_proveedor_api(nota_id: int, db: Session = Depends(get_db)):
    try:
        # La función crud ya previene cancelar notas pagadas o canceladas
        success = crud.cancelar_nota_proveedor(db, nota_id)
        
        if not success:
             raise HTTPException(status_code=400, detail="No se pudo cancelar la nota (ya pagada o cancelada)")
        
        # Obtenemos la nota actualizada para notificar a todos
        nota = crud.get_nota_proveedor(db, nota_id) 
        await manager.broadcast({
            "type": "nota_proveedor_actualizada",
            "data": _nota_proveedor_to_dict(nota)
        })
        return _nota_proveedor_to_dict(nota)
    
    except Exception as e:
        print(f"Error al cancelar nota proveedor API: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== NUEVO: CONFIGURACION ====================

@app.get("/configuracion")
def get_configuracion_api(db: Session = Depends(get_db)):
    config = crud.get_config_empresa(db)
    return _config_to_dict(config)

@app.post("/configuracion")
async def guardar_configuracion_api(datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        # Decodificar logo si existe
        if 'logo_data' in datos and datos['logo_data']:
            datos['logo_data'] = base64.b64decode(datos['logo_data'].encode('utf-8'))
        
        success = crud.guardar_config_empresa(db, datos)
        if success:
            config = crud.get_config_empresa(db)
            await manager.broadcast({
                "type": "config_actualizada",
                "data": _config_to_dict(config)
            })
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="No se pudo guardar la configuración")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== NUEVO: USUARIOS ====================

@app.get("/usuarios")
def get_usuarios_api(db: Session = Depends(get_db)):
    usuarios = crud.get_usuarios(db)
    return [_usuario_to_dict(u) for u in usuarios]

@app.get("/usuarios/{usuario_id}")
def get_usuario_api(usuario_id: int, db: Session = Depends(get_db)):
    usuario = crud.get_usuario(db, usuario_id)
    if usuario:
        return _usuario_to_dict(usuario)
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.get("/usuarios/contar_admins")
def get_contar_admins_api(db: Session = Depends(get_db)):
    count = crud.contar_admins_activos(db)
    return {"admins_activos": count}

@app.post("/usuarios")
async def crear_usuario_api(datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        usuario = crud.crear_usuario_crud(db, datos)
        if usuario:
            await manager.broadcast({
                "type": "usuario_creado",
                "data": _usuario_to_dict(usuario)
            })
            return _usuario_to_dict(usuario)
        else:
            raise HTTPException(status_code=400, detail="No se pudo crear el usuario (¿username duplicado?)")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/usuarios/{usuario_id}")
async def actualizar_usuario_api(usuario_id: int, datos: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        usuario = crud.actualizar_usuario(db, usuario_id, datos)
        if usuario:
            await manager.broadcast({
                "type": "usuario_actualizado",
                "data": _usuario_to_dict(usuario)
            })
            return _usuario_to_dict(usuario)
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/usuarios/{usuario_id}")
async def eliminar_usuario_api(usuario_id: int, db: Session = Depends(get_db)):
    try:
        success = crud.eliminar_usuario(db, usuario_id)
        if success:
            await manager.broadcast({
                "type": "usuario_eliminado",
                "data": {"id": usuario_id}
            })
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== CONVERSORES (Serializers) ====================
def _cliente_to_dict(c):
    if not c:
        return None
    return {
        'id': c.id,
        'nombre': c.nombre,
        'tipo': c.tipo,
        'email': c.email or '',
        'telefono': c.telefono or '',
        'rfc': c.rfc or '',
        'calle': c.calle or '',
        'colonia': c.colonia or '',
        'ciudad': c.ciudad or '',
        'estado': c.estado or '',
        'cp': c.cp or '',
        'pais': c.pais or 'México',
    }

def _proveedor_to_dict(p):
    if not p:
        return None
    return {
        'id': p.id,
        'nombre': p.nombre,
        'tipo': p.tipo,
        'email': p.email or '',
        'telefono': p.telefono or '',
        'rfc': p.rfc or '',
        'calle': p.calle or '',
        'colonia': p.colonia or '',
        'ciudad': p.ciudad or '',
        'estado': p.estado or '',
        'cp': p.cp or '',
        'pais': p.pais or 'México',
    }

def _producto_to_dict(p):
    if not p:
        return None
    return {
        'id': p.id,
        'codigo': p.codigo,
        'nombre': p.nombre,
        'categoria': p.categoria or '',
        'ubicacion': p.ubicacion or '',
        'proveedor_id': p.proveedor_id,
        'proveedor_nombre': p.proveedor.nombre if p.proveedor else 'N/A',
        'precio_compra': float(p.precio_compra or 0),
        'precio_venta': float(p.precio_venta or 0),
        'stock_actual': p.stock_actual or 0,
        'stock_min': p.stock_min or 0,
        'descripcion': p.descripcion or ''
    }

def _orden_to_dict(o):
    if not o:
        return None
    return {
        'id': o.id,
        'folio': o.folio,
        'cliente_id': o.cliente_id,
        'cliente_nombre': o.cliente.nombre if o.cliente else 'N/A',
        'vehiculo_marca': o.vehiculo_marca or '',
        'vehiculo_modelo': o.vehiculo_modelo or '',
        'vehiculo_ano': o.vehiculo_ano or '', 
        'vehiculo_placas': o.vehiculo_placas or '', # Añadido
        'vehiculo_vin': o.vehiculo_vin or '', # Añadido
        'vehiculo_color': o.vehiculo_color or '', # Añadido
        'vehiculo_kilometraje': o.vehiculo_kilometraje or '', # Añadido
        'estado': o.estado,
        'fecha_recepcion': o.fecha_recepcion.isoformat() if o.fecha_recepcion else '',
        'fecha_promesa': o.fecha_promesa.isoformat() if o.fecha_promesa else '', # Añadido
        'fecha_entrega': o.fecha_entrega.isoformat() if o.fecha_entrega else '', # Añadido
        'mecanico_asignado': o.mecanico_asignado or '',
        'observaciones': o.observaciones or '', # Añadido
        'nota_folio': o.nota_folio or '',
        'items': [{
            'id': i.id,
            'cantidad': i.cantidad,
            'descripcion': i.descripcion
        } for i in o.items] if hasattr(o, 'items') else []
    }

def _cotizacion_to_dict(c):
    if not c:
        return None
    return {
        'id': c.id,
        'folio': c.folio,
        'cliente_id': c.cliente_id,
        'cliente_nombre': c.cliente.nombre if c.cliente else 'N/A',
        'estado': c.estado,
        'vigencia': c.vigencia or '30 días',
        'subtotal': float(c.subtotal or 0),
        'impuestos': float(c.impuestos or 0), 
        'total': float(c.total or 0),
        'observaciones': c.observaciones or '',
        'fecha': c.created_at.isoformat() if c.created_at else '', # Cambiado a 'fecha' para consistencia
        'created_at': c.created_at.isoformat() if c.created_at else '', # Mantenemos created_at

        'nota_folio': c.nota_folio or '',
        'items': [{
            'id': i.id,
            'cantidad': i.cantidad,
            'descripcion': i.descripcion,
            'precio_unitario': float(i.precio_unitario or 0),
            'importe': float(i.importe or 0),
            'impuesto': float(i.impuesto or 0)
        } for i in c.items] if hasattr(c, 'items') else []
    }

def _nota_to_dict(n):
    if not n:
        return None
    return {
        'id': n.id,
        'folio': n.folio,
        'cliente_id': n.cliente_id,
        'cliente_nombre': n.cliente.nombre if n.cliente else '',
        'estado': n.estado,
        'metodo_pago': n.metodo_pago or '',
        'subtotal': float(n.subtotal or 0),
        'impuestos': float(n.impuestos or 0),
        'total': float(n.total or 0),
        'total_pagado': float(n.total_pagado or 0),
        'saldo': float(n.saldo or 0),
        'fecha': n.fecha.isoformat() if n.fecha else '',
        'observaciones': n.observaciones or '',
        'cotizacion_folio': n.cotizacion_folio or '',
        'orden_folio': n.orden_folio or '',
        'items': [{
            'id': i.id,
            'cantidad': i.cantidad,
            'descripcion': i.descripcion,
            'precio_unitario': float(i.precio_unitario or 0),
            'importe': float(i.importe or 0),
            'impuesto': float(i.impuesto or 0)
        } for i in n.items] if hasattr(n, 'items') else [],
        'pagos': [{
            'id': p.id,
            'monto': float(p.monto),
            'fecha_pago': p.fecha_pago.isoformat() if p.fecha_pago else '',
            'metodo_pago': p.metodo_pago,
            'memo': p.memo or ''
        } for p in n.pagos] if hasattr(n, 'pagos') else []
    }

def _pago_proveedor_to_dict(pago):
    if not pago: return {}
    return {
        'id': pago.id,
        'nota_id': pago.nota_id,
        'monto': float(pago.monto),
        # Corregido a ISO para consistencia
        'fecha_pago': pago.fecha_pago.isoformat() if pago.fecha_pago else '',
        'metodo_pago': pago.metodo_pago,
        'memo': pago.memo or ''
    }

def _nota_proveedor_to_dict(nota):
    if not nota: return {}
    return {
        'id': nota.id,
        'folio': nota.folio,
        'proveedor_id': nota.proveedor_id,
        'proveedor_nombre': nota.proveedor.nombre if nota.proveedor else '',
        'estado': nota.estado or 'Registrado',
        'metodo_pago': nota.metodo_pago or 'Efectivo',
        'fecha': nota.fecha.isoformat() if nota.fecha else '', # Corregido a ISO
        'observaciones': nota.observaciones or '',
        'subtotal': float(nota.subtotal or 0),
        'impuestos': float(nota.impuestos or 0),
        'total': float(nota.total or 0),
        'total_pagado': float(nota.total_pagado or 0),
        'saldo': float(nota.saldo or 0),
        'items': [{
            'id': i.id, # Agregado ID de item
            'cantidad': i.cantidad,
            'descripcion': i.descripcion,
            'precio_unitario': float(i.precio_unitario or 0),
            'importe': float(i.importe or 0),
            'impuesto': float(i.impuesto or 0)
        } for i in nota.items],
        'pagos': [_pago_proveedor_to_dict(p) for p in nota.pagos]
    }

def _movimiento_to_dict(m):
    if not m:
        return None
    return {
        'id': m.id,
        'producto_id': m.producto_id,
        'producto': m.producto.nombre if m.producto else 'N/A', 
        'tipo': m.tipo,
        'cantidad': m.cantidad,
        'motivo': m.motivo or '',
        'usuario': m.usuario or '',
        'fecha': m.created_at.isoformat() if m.created_at else ''
    }

# --- NUEVO SERIALIZER ---
def _config_to_dict(c: Optional[ConfigEmpresa]) -> Optional[Dict]:
    """Convierte un objeto ConfigEmpresa ORM a dict, codificando el logo."""
    if not c:
        return None
    
    logo_b64 = None
    if c.logo_data:
        logo_b64 = base64.b64encode(c.logo_data).decode('utf-8')
        
    return {
        'id': c.id,
        'nombre_comercial': c.nombre_comercial,
        'razon_social': c.razon_social or '',
        'rfc': c.rfc or '',
        'calle': c.calle or '',
        'colonia': c.colonia or '',
        'ciudad': c.ciudad or '',
        'estado': c.estado or '',
        'cp': c.cp or '',
        'pais': c.pais or 'México',
        'telefono1': c.telefono1 or '',
        'telefono2': c.telefono2 or '',
        'email': c.email or '',
        'sitio_web': c.sitio_web or '',
        'logo_data': logo_b64 # Enviar como string Base64
    }

# --- SERIALIZER ACTUALIZADO ---
def _usuario_to_dict(usuario: Optional[Usuario]) -> Optional[Dict]:
    """Convierte un objeto Usuario ORM a dict."""
    if not usuario: 
        return None
    return {
        'id': usuario.id,
        'username': usuario.username,
        'password_hash': usuario.password_hash, # Necesario para login
        'nombre_completo': usuario.nombre_completo,
        'email': usuario.email or '',
        'rol': usuario.rol,
        'activo': usuario.activo,
        'ultimo_acceso': usuario.ultimo_acceso.isoformat() if usuario.ultimo_acceso else ''
    }

# ==================== RUTA RAÍZ ====================
@app.get("/")
def root():
    return {"message": "Taller API Distribuida - Sistema funcionando"}

if __name__ == "__main__":
    import uvicorn
    # Asegúrate de importar los modelos antes de crear tablas
    from server import models
    from server.database import crear_tablas
    
    print("Creando tablas si no existen...")
    crear_tablas() # Esto es seguro, no borra datos existentes
    
    print("Iniciando servidor Uvicorn en 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
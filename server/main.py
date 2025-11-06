from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import get_db_sync, SessionLocal
from server import crud
import json
from datetime import datetime

app = FastAPI(title="Taller API Distribuida")

# CORS para permitir conexiones
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
        """Enviar mensaje a todos los clientes conectados"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# ==================== WEBSOCKET ENDPOINT ====================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Mantener conexión viva
            await websocket.send_json({"status": "connected"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ==================== HELPER ====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/proveedores")
async def crear_proveedor(datos: Dict[str, Any], db: Session = Depends(get_db)):
    proveedor = crud.create_proveedor(db, datos)
    await manager.broadcast({
        "type": "proveedor_creado",
        "data": _proveedor_to_dict(proveedor)
    })
    return _proveedor_to_dict(proveedor)

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

# ==================== ORDENES ====================
@app.get("/ordenes")
def get_ordenes(estado: str = None, db: Session = Depends(get_db)):
    ordenes = crud.get_all_ordenes(db, estado=estado)
    return [_orden_to_dict(o) for o in ordenes]

@app.post("/ordenes")
async def crear_orden(datos: Dict[str, Any], db: Session = Depends(get_db)):
    items = datos.pop('items', [])
    orden = crud.create_orden(db, datos, items)
    await manager.broadcast({
        "type": "orden_creada",
        "data": _orden_to_dict(orden)
    })
    return _orden_to_dict(orden)

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

# ==================== NOTAS DE VENTA ====================
@app.get("/notas")
def get_notas(db: Session = Depends(get_db)):
    notas = crud.get_all_notas_venta(db)
    return [_nota_to_dict(n) for n in notas]

@app.post("/notas")
async def crear_nota(datos: Dict[str, Any], db: Session = Depends(get_db)):
    nota = crud.create_nota_venta(db, datos)
    await manager.broadcast({
        "type": "nota_creada",
        "data": {"id": nota.id}
    })
    return _nota_to_dict(nota)

# ==================== MOVIMIENTOS INVENTARIO ====================
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
    await manager.broadcast({
        "type": "stock_actualizado",
        "data": {
            "producto_id": datos['producto_id'],
            "tipo": datos['tipo'],
            "cantidad": datos['cantidad']
        }
    })
    return {"success": True}

# ==================== CONVERSORES ====================
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
        'notas': c.notas or ''
    }

def _proveedor_to_dict(p):
    if not p:
        return None
    return {
        'id': p.id,
        'nombre': p.nombre,
        'email': p.email or '',
        'telefono': p.telefono or '',
        'rfc': p.rfc or '',
        'calle': p.calle or '',
        'colonia': p.colonia or '',
        'ciudad': p.ciudad or '',
        'estado': p.estado or '',
        'cp': p.cp or ''
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
        'vehiculo_marca': o.vehiculo_marca or '',
        'vehiculo_modelo': o.vehiculo_modelo or '',
        'estado': o.estado,
        'total': float(o.total or 0),
        'fecha': o.fecha_ingreso.isoformat() if o.fecha_ingreso else ''
    }

def _cotizacion_to_dict(c):
    if not c:
        return None
    return {
        'id': c.id,
        'folio': c.folio,
        'cliente_id': c.cliente_id,
        'estado': c.estado,
        'subtotal': float(c.subtotal or 0),
        'total': float(c.total or 0),
        'fecha': c.fecha_cotizacion.isoformat() if c.fecha_cotizacion else ''
    }

def _nota_to_dict(n):
    if not n:
        return None
    return {
        'id': n.id,
        'folio': n.folio,
        'cliente_id': n.cliente_id,
        'total': float(n.total or 0),
        'pagado': float(n.pagado or 0),
        'saldo': float(n.saldo or 0),
        'estado_pago': n.estado_pago
    }

@app.get("/")
def root():
    return {"message": "Taller API Distribuida - Sistema funcionando"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

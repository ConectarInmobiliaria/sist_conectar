# database.py - Módulo de Gestión de Base de Datos
import sqlite3
import bcrypt
from datetime import datetime
from typing import Optional, List, Dict, Any


class DatabaseManager:
    """Gestiona todas las operaciones de base de datos SQLite local"""
    
    def __init__(self, db_name="inmobiliaria.db"):
        self.db_name = db_name
        self.conn = None
        self.init_database()
    
    def get_connection(self):
        """Obtiene conexión a la base de datos"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre_completo TEXT NOT NULL,
                email TEXT,
                rol TEXT DEFAULT 'usuario',
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_sync TIMESTAMP
            )
        ''')
        
        # Tabla de propietarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS propietarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cuit_dni TEXT UNIQUE NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT,
                direccion TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modificado INTEGER DEFAULT 0,
                ultimo_sync TIMESTAMP
            )
        ''')
        
        # Tabla de inquilinos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inquilinos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cuit_dni TEXT UNIQUE NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT,
                direccion TEXT NOT NULL,
                fecha_nacimiento DATE,
                ocupacion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modificado INTEGER DEFAULT 0,
                ultimo_sync TIMESTAMP
            )
        ''')
        
        # Tabla de inmuebles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inmuebles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                propietario_id INTEGER,
                tipo TEXT NOT NULL,
                direccion TEXT NOT NULL,
                ciudad TEXT DEFAULT 'Posadas',
                provincia TEXT DEFAULT 'Misiones',
                codigo_postal TEXT,
                superficie REAL,
                habitaciones INTEGER,
                banos INTEGER,
                precio_venta REAL,
                precio_alquiler REAL,
                partida_inmobiliaria TEXT,
                conexion_emsa TEXT,
                conexion_samsa TEXT,
                estado TEXT DEFAULT 'disponible',
                descripcion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modificado INTEGER DEFAULT 0,
                ultimo_sync TIMESTAMP,
                FOREIGN KEY (propietario_id) REFERENCES propietarios(id)
            )
        ''')
        
        # Tabla de contratos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contratos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inmueble_id INTEGER,
                inquilino_id INTEGER,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE NOT NULL,
                monto_mensual REAL NOT NULL,
                deposito REAL,
                gastos_comunes REAL DEFAULT 0,
                tipo_ajuste TEXT DEFAULT 'IPC',
                frecuencia_ajuste INTEGER DEFAULT 4,
                fecha_ultimo_ajuste DATE,
                fecha_proximo_ajuste DATE,
                estado TEXT DEFAULT 'activo',
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modificado INTEGER DEFAULT 0,
                ultimo_sync TIMESTAMP,
                FOREIGN KEY (inmueble_id) REFERENCES inmuebles(id),
                FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
            )
        ''')
        
        # Tabla de pagos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contrato_id INTEGER,
                fecha_pago DATE NOT NULL,
                periodo_mes INTEGER NOT NULL,
                periodo_anio INTEGER NOT NULL,
                monto_alquiler REAL NOT NULL,
                monto_expensas REAL DEFAULT 0,
                monto_emsa REAL DEFAULT 0,
                monto_samsa REAL DEFAULT 0,
                monto_otros REAL DEFAULT 0,
                monto_total REAL NOT NULL,
                concepto TEXT,
                metodo_pago TEXT,
                comprobante TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modificado INTEGER DEFAULT 0,
                ultimo_sync TIMESTAMP,
                FOREIGN KEY (contrato_id) REFERENCES contratos(id)
            )
        ''')
        
        # Tabla de ajustes de contratos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ajustes_contratos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contrato_id INTEGER,
                fecha_ajuste DATE NOT NULL,
                monto_anterior REAL NOT NULL,
                monto_nuevo REAL NOT NULL,
                porcentaje_ajuste REAL,
                tipo_indice TEXT,
                valor_indice REAL,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contrato_id) REFERENCES contratos(id)
            )
        ''')
        
        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT,
                fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cola de sincronización
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tabla TEXT NOT NULL,
                registro_id INTEGER NOT NULL,
                accion TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                procesado INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        self.create_default_admin()
    
    def create_default_admin(self):
        """Crea usuario administrador por defecto"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            password = "admin123"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            cursor.execute('''
                INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash.decode('utf-8'), 'Administrador', 'admin'))
            
            conn.commit()
            print("✅ Usuario admin creado - Contraseña: admin123")
    
    # ========================================
    # MÉTODOS CRUD GENÉRICOS
    # ========================================
    
    def insert(self, tabla: str, datos: Dict[str, Any]) -> Optional[int]:
        """Inserta un registro y retorna el ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            columnas = ', '.join(datos.keys())
            placeholders = ', '.join(['?' for _ in datos])
            valores = tuple(datos.values())
            
            query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
            cursor.execute(query, valores)
            conn.commit()
            
            # Agregar a cola de sincronización
            self.add_to_sync_queue(tabla, cursor.lastrowid, 'INSERT')
            
            return cursor.lastrowid
        except Exception as e:
            print(f"Error insertando en {tabla}: {e}")
            return None
    
    def update(self, tabla: str, id: int, datos: Dict[str, Any]) -> bool:
        """Actualiza un registro"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Agregar campo modificado
            datos['modificado'] = 1
            
            set_clause = ', '.join([f"{k} = ?" for k in datos.keys()])
            valores = tuple(datos.values()) + (id,)
            
            query = f"UPDATE {tabla} SET {set_clause} WHERE id = ?"
            cursor.execute(query, valores)
            conn.commit()
            
            # Agregar a cola de sincronización
            self.add_to_sync_queue(tabla, id, 'UPDATE')
            
            return True
        except Exception as e:
            print(f"Error actualizando {tabla} ID {id}: {e}")
            return False
    
    def delete(self, tabla: str, id: int) -> bool:
        """Elimina un registro"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = f"DELETE FROM {tabla} WHERE id = ?"
            cursor.execute(query, (id,))
            conn.commit()
            
            # Agregar a cola de sincronización
            self.add_to_sync_queue(tabla, id, 'DELETE')
            
            return True
        except Exception as e:
            print(f"Error eliminando de {tabla} ID {id}: {e}")
            return False
    
    def get_by_id(self, tabla: str, id: int) -> Optional[Dict]:
        """Obtiene un registro por ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = f"SELECT * FROM {tabla} WHERE id = ?"
            cursor.execute(query, (id,))
            result = cursor.fetchone()
            
            return dict(result) if result else None
        except Exception as e:
            print(f"Error obteniendo de {tabla} ID {id}: {e}")
            return None
    
    def get_all(self, tabla: str, order_by: str = "id DESC", limit: int = None) -> List[Dict]:
        """Obtiene todos los registros de una tabla"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = f"SELECT * FROM {tabla} ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error obteniendo todos de {tabla}: {e}")
            return []
    
    def search(self, tabla: str, campo: str, valor: str) -> List[Dict]:
        """Busca registros por un campo específico"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = f"SELECT * FROM {tabla} WHERE {campo} LIKE ?"
            cursor.execute(query, (f"%{valor}%",))
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error buscando en {tabla}: {e}")
            return []
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Ejecuta una consulta SQL personalizada"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error ejecutando query: {e}")
            return []
    
    # ========================================
    # MÉTODOS DE SINCRONIZACIÓN
    # ========================================
    
    def add_to_sync_queue(self, tabla: str, registro_id: int, accion: str):
        """Agrega un cambio a la cola de sincronización"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sync_queue (tabla, registro_id, accion)
                VALUES (?, ?, ?)
            ''', (tabla, registro_id, accion))
            
            conn.commit()
        except Exception as e:
            print(f"Error agregando a cola de sync: {e}")
    
    def get_pending_syncs(self, limit: int = 50) -> List[Dict]:
        """Obtiene cambios pendientes de sincronizar"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, tabla, registro_id, accion 
                FROM sync_queue 
                WHERE procesado = 0 
                ORDER BY timestamp ASC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error obteniendo syncs pendientes: {e}")
            return []
    
    def mark_sync_processed(self, sync_id: int):
        """Marca un cambio como sincronizado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sync_queue SET procesado = 1 
                WHERE id = ?
            ''', (sync_id,))
            
            conn.commit()
        except Exception as e:
            print(f"Error marcando sync procesado: {e}")
    
    # ========================================
    # MÉTODOS ESPECÍFICOS ÚTILES
    # ========================================
    
    def get_inmuebles_disponibles(self) -> List[Dict]:
        """Obtiene inmuebles disponibles"""
        query = '''
            SELECT i.*, p.nombre || ' ' || p.apellido as propietario_nombre
            FROM inmuebles i
            LEFT JOIN propietarios p ON i.propietario_id = p.id
            WHERE i.estado = 'disponible'
            ORDER BY i.fecha_creacion DESC
        '''
        return self.execute_query(query)
    
    def get_contratos_activos(self) -> List[Dict]:
        """Obtiene contratos activos con información completa"""
        query = '''
            SELECT c.*, 
                   i.direccion as inmueble_direccion,
                   inq.nombre || ' ' || inq.apellido as inquilino_nombre,
                   p.nombre || ' ' || p.apellido as propietario_nombre
            FROM contratos c
            JOIN inmuebles i ON c.inmueble_id = i.id
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            LEFT JOIN propietarios p ON i.propietario_id = p.id
            WHERE c.estado = 'activo'
            ORDER BY c.fecha_inicio DESC
        '''
        return self.execute_query(query)
    
    def get_contratos_proximos_vencer(self, dias: int = 60) -> List[Dict]:
        """Obtiene contratos próximos a vencer"""
        query = '''
            SELECT c.*, 
                   i.direccion as inmueble_direccion,
                   inq.nombre || ' ' || inq.apellido as inquilino_nombre
            FROM contratos c
            JOIN inmuebles i ON c.inmueble_id = i.id
            JOIN inquilinos inq ON c.inquilino_id = inq.id
            WHERE c.estado = 'activo' 
            AND date(c.fecha_fin) <= date('now', ? || ' days')
            ORDER BY c.fecha_fin ASC
        ''', (f'+{dias}',)
        return self.execute_query(query[0], query[1])
    
    def get_estadisticas_dashboard(self) -> Dict:
        """Obtiene estadísticas para el dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total inmuebles
        cursor.execute("SELECT COUNT(*) FROM inmuebles")
        stats['total_inmuebles'] = cursor.fetchone()[0]
        
        # Inmuebles por estado
        cursor.execute("SELECT COUNT(*) FROM inmuebles WHERE estado = 'disponible'")
        stats['inmuebles_disponibles'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inmuebles WHERE estado = 'alquilado'")
        stats['inmuebles_alquilados'] = cursor.fetchone()[0]
        
        # Contratos activos
        cursor.execute("SELECT COUNT(*) FROM contratos WHERE estado = 'activo'")
        stats['contratos_activos'] = cursor.fetchone()[0]
        
        # Propietarios e inquilinos
        cursor.execute("SELECT COUNT(*) FROM propietarios")
        stats['total_propietarios'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inquilinos")
        stats['total_inquilinos'] = cursor.fetchone()[0]
        
        # Ingresos mensuales
        cursor.execute("SELECT SUM(monto_mensual) FROM contratos WHERE estado = 'activo'")
        stats['ingresos_mensuales'] = cursor.fetchone()[0] or 0
        
        # Ocupación
        if stats['total_inmuebles'] > 0:
            stats['ocupacion'] = (stats['inmuebles_alquilados'] / stats['total_inmuebles']) * 100
        else:
            stats['ocupacion'] = 0
        
        return stats
    
    def verificar_cuit_dni_existe(self, cuit_dni: str, tabla: str, excluir_id: int = None) -> bool:
        """Verifica si un CUIT/DNI ya existe"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if excluir_id:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE cuit_dni = ? AND id != ?", 
                          (cuit_dni, excluir_id))
        else:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE cuit_dni = ?", (cuit_dni,))
        
        return cursor.fetchone()[0] > 0
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            self.conn = None

# supabase_sync.py - Módulo de Sincronización con Supabase
from typing import Optional
from supabase import create_client, Client
from database import DatabaseManager

# Configuración de Supabase
SUPABASE_URL = "https://hqicpusqpzphmnbgwhao.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhxaWNwdXNxcHpwaG1uYmd3aGFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0MzQ4ODcsImV4cCI6MjA4MTAxMDg4N30.HNrA6Zd-Mk3vus9txWqYbYQFAH9FChSQlEPrKuDTkKU"


class SupabaseSync:
    """Maneja la sincronización bidireccional con Supabase"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.supabase: Optional[Client] = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """Conecta con Supabase"""
        try:
            self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.test_connection()
            print("✅ Conectado a Supabase")
        except Exception as e:
            print(f"⚠️ Error conectando a Supabase: {e}")
            self.connected = False
    
    def test_connection(self) -> bool:
        """Prueba la conexión con Supabase"""
        try:
            # Intentar una consulta simple
            response = self.supabase.table('configuracion').select('*').limit(1).execute()
            self.connected = True
            return True
        except Exception as e:
            print(f"⚠️ Error en test de conexión: {e}")
            self.connected = False
            return False
    
    def sync_now(self) -> bool:
        """
        Ejecuta sincronización inmediata de todos los cambios pendientes
        Retorna True si fue exitosa
        """
        if not self.connected or not self.supabase:
            print("⚠️ No hay conexión a Supabase")
            return False
        
        try:
            # Obtener cambios pendientes
            cambios = self.db_manager.get_pending_syncs(limit=100)
            
            if not cambios:
                print("✅ No hay cambios pendientes para sincronizar")
                return True
            
            print(f"🔄 Sincronizando {len(cambios)} cambios...")
            sincronizados = 0
            
            for cambio in cambios:
                sync_id = cambio['id']
                tabla = cambio['tabla']
                registro_id = cambio['registro_id']
                accion = cambio['accion']
                
                try:
                    if accion == 'INSERT' or accion == 'UPDATE':
                        # Obtener datos del registro
                        registro = self.db_manager.get_by_id(tabla, registro_id)
                        
                        if registro:
                            # Limpiar campos que no van a Supabase
                            datos = {k: v for k, v in registro.items() 
                                   if k not in ['modificado', 'ultimo_sync']}
                            
                            # Upsert en Supabase
                            self.supabase.table(tabla).upsert(datos).execute()
                            sincronizados += 1
                    
                    elif accion == 'DELETE':
                        # Eliminar en Supabase
                        self.supabase.table(tabla).delete().eq('id', registro_id).execute()
                        sincronizados += 1
                    
                    # Marcar como procesado
                    self.db_manager.mark_sync_processed(sync_id)
                    
                except Exception as e:
                    print(f"❌ Error sincronizando {tabla} ID {registro_id}: {e}")
                    continue
            
            print(f"✅ Sincronizados {sincronizados}/{len(cambios)} cambios")
            return sincronizados == len(cambios)
            
        except Exception as e:
            print(f"❌ Error en sincronización: {e}")
            return False
    
    def sync_from_supabase(self, tabla: str) -> bool:
        """
        Descarga datos de Supabase a la base local
        Útil para la primera sincronización o restauración
        """
        if not self.connected or not self.supabase:
            return False
        
        try:
            # Obtener todos los registros de Supabase
            response = self.supabase.table(tabla).select('*').execute()
            registros = response.data
            
            print(f"📥 Descargando {len(registros)} registros de {tabla}...")
            
            for registro in registros:
                # Verificar si ya existe localmente
                local = self.db_manager.get_by_id(tabla, registro['id'])
                
                if local:
                    # Actualizar si es más reciente
                    self.db_manager.update(tabla, registro['id'], registro)
                else:
                    # Insertar nuevo
                    self.db_manager.insert(tabla, registro)
            
            print(f"✅ {tabla} sincronizada desde Supabase")
            return True
            
        except Exception as e:
            print(f"❌ Error descargando {tabla}: {e}")
            return False
    
    def full_sync(self) -> bool:
        """
        Sincronización completa bidireccional
        Primero sube cambios locales, luego descarga de Supabase
        """
        if not self.connected:
            return False
        
        # Subir cambios locales
        self.sync_now()
        
        # Descargar desde Supabase
        tablas = ['propietarios', 'inquilinos', 'inmuebles', 'contratos', 'pagos']
        
        for tabla in tablas:
            self.sync_from_supabase(tabla)
        
        print("✅ Sincronización completa finalizada")
        return True
    
    def get_status(self) -> dict:
        """Retorna el estado de la sincronización"""
        pendientes = len(self.db_manager.get_pending_syncs())
        
        return {
            'connected': self.connected,
            'pending_syncs': pendientes,
            'supabase_url': SUPABASE_URL
        }

#!/usr/bin/env python3
"""
Script mejorado para crear usuario administrador y datos de prueba
"""

import sys
import os
import bcrypt
from datetime import datetime, timedelta
import uuid

# Añadir el directorio raíz al path para importar los módulos
# Subimos 3 niveles: scripts/simulation/ -> raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

print(f"🔍 Buscando módulos en: {project_root}")

try:
    from sqlalchemy.orm import Session
    from app.database import SessionLocal, engine
    from app.models.database_models import User, Category, Task, Base
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("📂 Directorios en sys.path:")
    for path in sys.path:
        print(f"   - {path}")
    sys.exit(1)

def get_password_hash(password: str) -> str:
    """Genera hash de contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_admin_user():
    """Crear usuario administrador con datos de prueba"""
    db = SessionLocal()
    try:
        # Datos del administrador
        admin_email = "admin@taskapp.com"
        admin_password = "Admin123!"
        admin_name = "Administrador"
        
        # Verificar si el admin ya existe
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print(f"⚠️  El usuario administrador con email {admin_email} ya existe")
            # Limpiar datos existentes para prueba
            db.query(Task).filter(Task.user_id == existing_admin.id).delete()
            db.query(Category).filter(Category.user_id == existing_admin.id).delete()
        else:
            # Crear nuevo usuario administrador
            admin_user = User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                name=admin_name,
                is_admin=True,
                is_active=True,
                energy_level="high",
                preferences={
                    "notifications": True,
                    "energy_tracking": True,
                    "default_view": "priority"
                }
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            existing_admin = admin_user
            print("✅ Usuario administrador creado exitosamente!")

        # Crear categorías de ejemplo
        categories = [
            {"name": "Trabajo", "color": "#FF6B6B", "description": "Tareas relacionadas con trabajo"},
            {"name": "Personal", "color": "#4ECDC4", "description": "Tareas personales"},
            {"name": "Estudio", "color": "#45B7D1", "description": "Tareas de estudio y aprendizaje"}
        ]
        
        category_objs = []
        for cat_data in categories:
            category = Category(
                user_id=existing_admin.id,
                **cat_data
            )
            db.add(category)
            category_objs.append(category)
        
        db.commit()
        
        # Crear algunas tareas completadas para entrenamiento inicial
        completed_tasks = [
            {
                "title": "Revisar documentación del proyecto",
                "description": "Revisar y actualizar la documentación técnica del proyecto actual",
                "urgency": "high",
                "impact": "high",
                "status": "completed",
                "priority_level": "high",
                "energy_required": "medium",
                "deadline": datetime.now() - timedelta(days=2),
                "completed_at": datetime.now() - timedelta(days=1),
                "actual_duration": 120
            },
            {
                "title": "Preparar reunión de equipo",
                "description": "Preparar agenda y materiales para la reunión semanal del equipo",
                "urgency": "medium", 
                "impact": "medium",
                "status": "completed",
                "priority_level": "medium",
                "energy_required": "low",
                "deadline": datetime.now() - timedelta(days=5),
                "completed_at": datetime.now() - timedelta(days=4),
                "actual_duration": 45
            }
        ]
        
        for task_data in completed_tasks:
            task = Task(
                user_id=existing_admin.id,
                category_id=category_objs[0].id,
                **task_data
            )
            db.add(task)
        
        db.commit()
        
        print("✅ Datos de prueba creados exitosamente!")
        print(f"📧 Credenciales de administrador:")
        print(f"   Email: {admin_email}")
        print(f"   Contraseña: {admin_password}")
        print(f"👤 Categorías creadas: {len(categories)}")
        print(f"📊 Tareas de entrenamiento: {len(completed_tasks)}")
        
    except Exception as e:
        print(f"❌ Error al crear datos de prueba: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🛠️  Script de inicialización de datos de prueba")
    print("=" * 50)
    
    # Crear tablas si no existen
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas de base de datos verificadas")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        sys.exit(1)
    
    create_admin_user()
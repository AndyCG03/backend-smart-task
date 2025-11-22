#!/usr/bin/env python3
"""
Script para crear un usuario administrador en la base de datos
"""

import sys
import os
import bcrypt

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.database_models import User, Base

def check_admin_column_exists():
    """Verificar si la columna is_admin existe"""
    try:
        db = SessionLocal()
        # Intentar una consulta que use is_admin
        test_user = db.query(User).filter(User.is_admin == True).first()
        db.close()
        return True
    except Exception as e:
        if "is_admin" in str(e):
            return False
        raise e

def create_admin_column():
    """Crear la columna is_admin si no existe"""
    print("🔧 Verificando estructura de la base de datos...")
    
    if not check_admin_column_exists():
        print("❌ La columna 'is_admin' no existe en la tabla users")
        print("📋 Creando la columna...")
        
        try:
            # Ejecutar SQL directo para añadir la columna
            from sqlalchemy import text
            db = SessionLocal()
            db.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            db.commit()
            db.close()
            print("✅ Columna 'is_admin' creada exitosamente")
        except Exception as e:
            print(f"❌ Error al crear la columna: {e}")
            return False
    
    return True

def get_password_hash(password: str) -> str:
    """Genera hash de contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_admin_user():
    """Crear usuario administrador"""
    if not create_admin_column():
        return
    
    db = SessionLocal()
    try:
        # Datos del administrador
        admin_email = "admin@taskapp.com"
        admin_password = "Admin123!"  # Cambiar en producción
        admin_name = "Administrador"
        
        # Verificar si el admin ya existe
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print(f"⚠️  El usuario administrador con email {admin_email} ya existe")
            
            # Actualizar a administrador
            existing_admin.password_hash = get_password_hash(admin_password)
            existing_admin.is_admin = True
            existing_admin.is_active = True
            db.commit()
            print("✅ Usuario actualizado como administrador")
            print(f"📧 Email: {admin_email}")
            print(f"🔑 Contraseña: {admin_password}")
            return
        
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
        
        print("✅ Usuario administrador creado exitosamente!")
        print(f"📧 Email: {admin_email}")
        print(f"🔑 Contraseña: {admin_password}")
        print("⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        
    except Exception as e:
        print(f"❌ Error al crear el administrador: {e}")
        db.rollback()
    finally:
        db.close()

def create_admin_interactive():
    """Crear administrador con datos interactivos"""
    if not create_admin_column():
        return
    
    db = SessionLocal()
    try:
        print("👤 Creación de usuario administrador")
        print("=" * 40)
        
        email = input("Email del administrador [admin@taskapp.com]: ").strip()
        if not email:
            email = "admin@taskapp.com"
        
        password = input("Contraseña [Admin123!]: ").strip()
        if not password:
            password = "Admin123!"
        
        name = input("Nombre [Administrador]: ").strip()
        if not name:
            name = "Administrador"
        
        # Verificar si ya existe
        existing_admin = db.query(User).filter(User.email == email).first()
        if existing_admin:
            print(f"⚠️  El usuario con email {email} ya existe")
            response = input("¿Deseas convertirlo en administrador? (s/n): ").lower()
            if response == 's':
                existing_admin.is_admin = True
                existing_admin.is_active = True
                existing_admin.password_hash = get_password_hash(password)
                db.commit()
                print("✅ Usuario convertido a administrador")
            return
        
        # Crear nuevo admin
        admin_user = User(
            email=email,
            password_hash=get_password_hash(password),
            name=name,
            is_admin=True,
            is_active=True,
            energy_level="high"
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Usuario administrador creado exitosamente!")
        print(f"📧 Email: {email}")
        print(f"👤 Nombre: {name}")
        print("🔐 Rol: Administrador")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🛠️  Script de creación de administrador")
    print("=" * 50)
    
    # Crear tablas si no existen
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas de base de datos verificadas")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        sys.exit(1)
    
    # Opciones
    print("\nOpciones:")
    print("1. Crear administrador con valores por defecto")
    print("2. Crear administrador con datos personalizados")
    
    choice = input("\nSelecciona una opción (1/2): ").strip()
    
    if choice == "1":
        create_admin_user()
    elif choice == "2":
        create_admin_interactive()
    else:
        print("❌ Opción no válida")
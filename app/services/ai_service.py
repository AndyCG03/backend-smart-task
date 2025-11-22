# app/services/task_agent.py
import pandas as pd
from sklearn.linear_model import SGDRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
import joblib
from io import BytesIO
import traceback
from typing import List, Dict, Any
import uuid

from app.models.database_models import Task, TaskMLData, MLFeedback, AIModel

class TaskAgent:
    def __init__(self, db: Session, user_id: uuid.UUID = None):
        self.db = db
        self.user_id = user_id
        self.modelo = None
        self.vectorizador = TfidfVectorizer(max_features=100)
        self.encoder = LabelEncoder()
        self.fecha_min = None
        self.fecha_max = None

        # Cargar modelo si existe
        self._cargar_modelo()

    def _cargar_modelo(self):
        """Cargar modelo desde la tabla AIModel"""
        try:
            modelo_db = self.db.query(AIModel).filter(
                AIModel.user_id == self.user_id,
                AIModel.is_active == True
            ).order_by(AIModel.trained_at.desc()).first()
            
            if modelo_db and modelo_db.model_data:
                modelo = joblib.load(BytesIO(modelo_db.model_data))
                self.modelo = modelo
                print("✅ Modelo cargado desde la base de datos.")
        except Exception as e:
            print(f"❌ Error al cargar modelo: {e}")
            traceback.print_exc()

    def _guardar_modelo(self, modelo, model_type: str = "priority_predictor"):
        """Guardar modelo en la tabla AIModel"""
        try:
            # Desactivar modelos anteriores
            self.db.query(AIModel).filter(
                AIModel.user_id == self.user_id,
                AIModel.model_type == model_type
            ).update({"is_active": False})
            
            buffer = BytesIO()
            joblib.dump(modelo, buffer)
            modelo_bin = buffer.getvalue()
            
            nuevo_modelo = AIModel(
                user_id=self.user_id,
                model_type=model_type,
                model_version="1.0",
                model_data=modelo_bin,
                feature_weights={},  # Podrías extraer feature importance aquí
                accuracy_metrics={},
                is_active=True
            )
            self.db.add(nuevo_modelo)
            self.db.commit()
            print("✅ Modelo guardado en base de datos.")
        except Exception as e:
            print(f"❌ Error al guardar modelo: {e}")
            self.db.rollback()

    def _preparar_datos_entrenamiento(self, tasks: List[Task]):
        """Preparar datos para entrenamiento desde las tareas"""
        if not tasks:
            return None, None
            
        datos = []
        for task in tasks:
            if task.completed_at and task.deadline:  # Solo tareas completadas con deadline
                datos.append({
                    "descripcion": task.description or "",
                    "prioridad": task.priority_level or "medium",
                    "fecha_vencimiento": task.deadline.isoformat(),
                    "completada": 1,
                    "duracion_real": self._calcular_duracion(task),
                    "titulo": task.title
                })
        
        return pd.DataFrame(datos) if datos else None

    def _calcular_duracion(self, task: Task) -> int:
        """Calcular duración real de la tarea en horas"""
        if task.completed_at and task.created_at:
            diferencia = task.completed_at - task.created_at
            return int(diferencia.total_seconds() / 3600)  # Horas
        return 1  # Valor por defecto

    def entrenar_modelo_prioridad(self):
        """Entrenar modelo de predicción de prioridad"""
        try:
            # Obtener tareas históricas del usuario
            tareas = self.db.query(Task).filter(
                Task.user_id == self.user_id,
                Task.completed_at.isnot(None)
            ).all()
            
            df = self._preparar_datos_entrenamiento(tareas)
            if df is None or len(df) < 5:
                print(f"ℹ️ No hay suficientes datos para entrenar: {len(df) if df else 0}/5")
                return False

            # Preparar características
            df['fecha_ordinal'] = pd.to_datetime(df['fecha_vencimiento']).map(datetime.toordinal)
            
            # Escalar fechas
            self.fecha_min = df['fecha_ordinal'].min()
            self.fecha_max = df['fecha_ordinal'].max()
            X_fecha = ((df['fecha_ordinal'] - self.fecha_min) / 
                      (self.fecha_max - self.fecha_min + 1)).values.reshape(-1, 1)

            # Vectorizar texto y codificar prioridad
            X_texto = self.vectorizador.fit_transform(df['descripcion'])
            X_prioridad = self.encoder.fit_transform(df['prioridad']).reshape(-1, 1)

            X = np.hstack([X_texto.toarray(), X_fecha, X_prioridad])
            y = df['completada'].astype(float)

            # Entrenar modelo
            if self.modelo is None:
                self.modelo = SGDRegressor(
                    learning_rate='adaptive',
                    eta0=0.01,
                    random_state=42,
                    alpha=0.01
                )

            self.modelo.partial_fit(X, y)
            self._guardar_modelo(self.modelo, "priority_predictor")
            return True

        except Exception as e:
            print(f"❌ Error durante el entrenamiento: {e}")
            traceback.print_exc()
            return False

    def predecir_prioridad_tareas(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Predecir prioridad para lista de tareas pendientes"""
        try:
            if not tasks:
                return []

            # Preparar datos para predicción
            datos_pred = []
            for task in tasks:
                if task.deadline:  # Solo tareas con deadline
                    datos_pred.append({
                        "id": str(task.id),
                        "titulo": task.title,
                        "descripcion": task.description or "",
                        "prioridad": task.priority_level or "medium",
                        "fecha_vencimiento": task.deadline.isoformat(),
                        "task_obj": task
                    })

            if not datos_pred:
                return []

            df = pd.DataFrame(datos_pred)
            
            # Si no hay modelo, usar reglas básicas
            if self.modelo is None:
                return self._prioridad_por_reglas(datos_pred)

            # Preprocesamiento para predicción
            df['fecha_ordinal'] = pd.to_datetime(df['fecha_vencimiento']).map(datetime.toordinal)
            
            if self.fecha_min is None or self.fecha_max is None:
                X_fecha = ((df['fecha_ordinal'] - 738000) / 365.0).values.reshape(-1, 1)
            else:
                X_fecha = ((df['fecha_ordinal'] - self.fecha_min) / 
                          (self.fecha_max - self.fecha_min + 1)).values.reshape(-1, 1)

            X_texto = self.vectorizador.transform(df['descripcion'])
            X_prioridad = self.encoder.transform(df['prioridad']).reshape(-1, 1)

            X = np.hstack([X_texto.toarray(), X_fecha, X_prioridad])

            # Predicción
            predicciones = self.modelo.predict(X)
            df['puntaje_ml'] = predicciones

            # Guardar resultados en TaskMLData
            resultados = []
            for _, row in df.iterrows():
                task_ml_data = TaskMLData(
                    task_id=uuid.UUID(row['id']),
                    user_id=self.user_id,
                    ml_priority_score=float(row['puntaje_ml']),
                    features={
                        "descripcion_length": len(row['descripcion']),
                        "prioridad_original": row['prioridad'],
                        "dias_until_deadline": (datetime.fromisoformat(row['fecha_vencimiento']) - datetime.now()).days
                    }
                )
                self.db.add(task_ml_data)
                
                resultados.append({
                    "task_id": row['id'],
                    "titulo": row['titulo'],
                    "descripcion": row['descripcion'],
                    "prioridad_original": row['prioridad'],
                    "puntaje_ml": float(row['puntaje_ml']),
                    "task_obj": row['task_obj']
                })

            self.db.commit()
            return sorted(resultados, key=lambda x: x['puntaje_ml'], reverse=True)

        except Exception as e:
            print(f"❌ Error en predecir_prioridad_tareas: {e}")
            traceback.print_exc()
            return self._prioridad_por_reglas(datos_pred)

    def _prioridad_por_reglas(self, tareas: List[Dict]) -> List[Dict]:
        """Sistema de reglas cuando no hay modelo entrenado"""
        prioridad_map = {"high": 3, "medium": 2, "low": 1}
        
        for tarea in tareas:
            puntaje = prioridad_map.get(tarea['prioridad'], 1)
            if 'urgent' in tarea['descripcion'].lower():
                puntaje += 2
            tarea['puntaje_ml'] = float(puntaje)
            
        return sorted(tareas, key=lambda x: x['puntaje_ml'], reverse=True)

    def recomendar_horario(self, task: Task) -> str:
        """Recomendar horario para una tarea específica"""
        try:
            # Obtener tareas completadas del usuario
            tareas_completadas = self.db.query(Task).filter(
                Task.user_id == self.user_id,
                Task.completed_at.isnot(None)
            ).all()
            
            if not tareas_completadas:
                return "09:00"  # Horario por defecto

            # Analizar horarios preferidos
            horas = [t.completed_at.hour for t in tareas_completadas if t.completed_at]
            if not horas:
                return "09:00"
                
            from collections import Counter
            hora_mas_comun = Counter(horas).most_common(1)[0][0]
            
            # Guardar recomendación
            task_ml_data = TaskMLData(
                task_id=task.id,
                user_id=self.user_id,
                recommended_schedule=f"{hora_mas_comun:02d}:00"
            )
            self.db.add(task_ml_data)
            self.db.commit()
            
            return f"{hora_mas_comun:02d}:00"

        except Exception as e:
            print(f"❌ Error en recomendar_horario: {e}")
            return "09:00"
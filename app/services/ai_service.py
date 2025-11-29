import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
import joblib
from io import BytesIO
import traceback
from typing import List, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)

from app.models.database_models import Task, MLFeedback, AIModel


# Mapeos fijos (no requieren persistencia)
URGENCIA_MAP = {"low": 0, "medium": 1, "high": 2}
IMPACTO_MAP = {"low": 0, "medium": 1, "high": 2}
ENERGIA_MAP = {"low": 0, "medium": 1, "high": 2}
PRIORIDAD_MAP = {"low": 1, "medium": 2, "high": 3}


def _normalizar_nivel(valor: str) -> str:
    if not valor:
        return "medium"
    v = str(valor).lower().strip()
    if v in ("high", "critical", "crític", "urgent", "crucial"):
        return "high"
    elif v in ("low", "baja", "minimum"):
        return "low"
    else:
        return "medium"


class TaskAgent:
    """
    Agente de priorización con ML robusto y reglas de respaldo.
    Usa DecisionTreeClassifier para clasificar tareas en niveles de prioridad.
    """

    def __init__(self, db: Session, user_id: uuid.UUID):
        self.db = db
        self.user_id = user_id
        self.modelo = None
        self.feature_names = [
            'urgencia_encoded', 'impacto_encoded', 'energia_encoded',
            'duracion_estimada', 'longitud_descripcion',
            'tiene_urgente', 'tiene_bug', 'deadline_proximo'
        ]
        logger.info(f"🔄 Inicializando TaskAgent para usuario: {user_id}")
        self._cargar_modelo()

    def _cargar_modelo(self):
        """Carga el modelo ML más reciente y activo del usuario"""
        try:
            logger.info("🔍 Buscando modelo ML en base de datos...")
            modelo_db = self.db.query(AIModel).filter(
                AIModel.user_id == self.user_id,
                AIModel.is_active == True
            ).order_by(AIModel.trained_at.desc()).first()

            if modelo_db and modelo_db.model_data and len(modelo_db.model_data) > 0:
                logger.info(f"✅ Modelo encontrado ({len(modelo_db.model_data)} bytes)")
                try:
                    buffer = BytesIO(modelo_db.model_data)
                    self.modelo = joblib.load(buffer)
                    logger.info(f"✅ Modelo cargado exitosamente: {type(self.modelo)}")
                except Exception as e:
                    logger.error(f"❌ Error al cargar el modelo: {e}")
                    logger.error(traceback.format_exc())
                    self.modelo = None
            else:
                logger.info("ℹ️ No se encontró modelo activo. Se usará sistema de reglas.")
                self.modelo = None

        except Exception as e:
            logger.error(f"❌ Error en _cargar_modelo: {e}")
            logger.error(traceback.format_exc())
            self.modelo = None

    def _preparar_datos_entrenamiento(self):
        """Prepara datos de tareas completadas para entrenamiento"""
        try:
            tareas = self.db.query(Task).filter(
                Task.user_id == self.user_id,
                Task.status == 'completed'
            ).all()
            logger.info(f"📊 Tareas completadas encontradas para entrenamiento: {len(tareas)}")

            if len(tareas) < 3:
                logger.warning(f"⚠️ Insuficientes tareas completadas ({len(tareas)}/3). No se entrenará ML.")
                return None, None

            datos = []
            objetivos = []
            
            for task in tareas:
                # Obtener feedback para esta tarea
                feedback = self.db.query(MLFeedback).filter(
                    MLFeedback.task_id == task.id,
                    MLFeedback.actual_priority.isnot(None)
                ).order_by(MLFeedback.created_at.desc()).first()
                
                # Determinar prioridad objetivo
                prioridad_objetivo = feedback.actual_priority if feedback else task.priority_level
                prioridad_objetivo = _normalizar_nivel(prioridad_objetivo)
                
                # Calcular si tiene deadline próximo
                deadline_proximo = 0
                if task.deadline:
                    dias = (task.deadline - datetime.now()).days
                    deadline_proximo = 1 if dias <= 1 else 0
                
                dato = {
                    "urgencia_encoded": URGENCIA_MAP.get(_normalizar_nivel(task.urgency), 1),
                    "impacto_encoded": IMPACTO_MAP.get(_normalizar_nivel(task.impact), 1),
                    "energia_encoded": ENERGIA_MAP.get(_normalizar_nivel(task.energy_required), 1),
                    "duracion_estimada": float(task.estimated_duration or 60),
                    "longitud_descripcion": len(task.description or ""),
                    "tiene_urgente": 1 if "urgent" in (task.description or "").lower() or "crític" in (task.title or "").lower() else 0,
                    "tiene_bug": 1 if "bug" in (task.title or "").lower() or "fix" in (task.title or "").lower() else 0,
                    "deadline_proximo": deadline_proximo
                }
                datos.append(dato)
                objetivos.append(PRIORIDAD_MAP[prioridad_objetivo])

            return pd.DataFrame(datos), np.array(objetivos)

        except Exception as e:
            logger.error(f"❌ Error en _preparar_datos_entrenamiento: {e}")
            logger.error(traceback.format_exc())
            return None, None

    def entrenar_modelo_prioridad(self) -> bool:
        """Entrena un modelo con DecisionTreeClassifier"""
        X_df, y = self._preparar_datos_entrenamiento()
        if X_df is None or y is None or len(X_df) < 3:
            logger.warning("🧠 No hay suficientes datos para entrenar modelo ML. Usando reglas.")
            self.modelo = None
            return False

        try:
            logger.info(f"🎯 Entrenando modelo con {len(X_df)} tareas...")
            logger.info(f"Dataset de entrenamiento:\n{X_df.head()}")
            logger.info(f"Objetivos (prioridades): {y}")

            # Entrenar modelo
            self.modelo = DecisionTreeClassifier(
                max_depth=3,  # Evitar overfitting
                random_state=42,
                class_weight="balanced"
            )
            self.modelo.fit(X_df.values, y)

            # Guardar modelo
            self._guardar_modelo()
            logger.info("✅ Modelo entrenado y guardado exitosamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error fatal en entrenamiento: {e}")
            logger.error(traceback.format_exc())
            self.modelo = None
            return False

    def _guardar_modelo(self):
        """Guarda el modelo en la base de datos"""
        if self.modelo is None:
            logger.warning("⚠️ No se puede guardar: modelo no entrenado.")
            return

        try:
            # Desactivar versiones anteriores
            self.db.query(AIModel).filter(
                AIModel.user_id == self.user_id,
                AIModel.model_type == "priority_predictor_v3"
            ).update({"is_active": False})
            self.db.commit()

            # Guardar nuevo modelo
            buffer = BytesIO()
            joblib.dump(self.modelo, buffer)
            modelo_bin = buffer.getvalue()

            nuevo_modelo = AIModel(
                user_id=self.user_id,
                model_type="priority_predictor_v3",
                model_version="3.1",
                model_data=modelo_bin,
                is_active=True
            )

            self.db.add(nuevo_modelo)
            self.db.commit()
            logger.info(f"💾 Modelo guardado ({len(modelo_bin)} bytes)")

        except Exception as e:
            logger.error(f"❌ Error al guardar el modelo: {e}")
            logger.error(traceback.format_exc())
            self.db.rollback()

    def _post_procesamiento(self, resultados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aplica ajustes contextuales a los puntajes"""
        try:
            hora_actual = datetime.now().hour
            logger.info(f"⏰ Hora actual: {hora_actual}:00")

            # Identificar tareas con feedback negativo reciente
            veinticuatro_horas = datetime.now() - pd.Timedelta(hours=24)
            feedbacks_negativos = self.db.query(MLFeedback).filter(
                MLFeedback.user_id == self.user_id,
                MLFeedback.created_at >= veinticuatro_horas,
                MLFeedback.was_useful == False
            ).all()
            task_ids_con_feedback = {f.task_id for f in feedbacks_negativos}

            for item in resultados:
                task = item['task_obj']
                energia = task.energy_required or "medium"
                duracion = task.estimated_duration or 60
                ajuste = 1.0

                # Ajuste por hora del día y energía
                if hora_actual >= 18:  # Tarde/noche
                    if energia == "high":
                        ajuste *= 0.7
                    elif energia == "low":
                        ajuste *= 1.3
                elif 7 <= hora_actual <= 10:  # Mañana
                    if energia == "high":
                        ajuste *= 1.2

                # Penalizar tareas largas al final del día
                if hora_actual >= 17 and duracion > 120:
                    ajuste *= 0.8

                # Ajuste por feedback negativo reciente (el sistema subestimó esta tarea)
                if task.id in task_ids_con_feedback:
                    ajuste *= 1.3
                    logger.info(f"📈 Aumentando prioridad por feedback negativo en tarea: {task.title}")

                # Ajuste por deadline próximo
                if task.deadline:
                    dias = (task.deadline - datetime.now()).days
                    if dias < 0:
                        ajuste *= 1.5
                    elif dias == 0:
                        ajuste *= 1.4
                    elif dias <= 1:
                        ajuste *= 1.2

                puntaje_original = item['puntaje_ml']
                item['puntaje_ml'] = max(puntaje_original * ajuste, 0.5)
                logger.debug(f"📊 {task.title[:30]}: {puntaje_original:.2f} → {item['puntaje_ml']:.2f} (ajuste: {ajuste:.2f})")

            logger.info("✅ Post-procesamiento aplicado correctamente")
            return resultados
        except Exception as e:
            logger.error(f"❌ Error en post-procesamiento: {e}")
            logger.error(traceback.format_exc())
            return resultados

    def _prioridad_por_reglas(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Sistema de respaldo basado en reglas heurísticas"""
        logger.info("📋 Usando sistema de reglas para priorización (no hay suficientes datos para ML)")
        prioridad_map = {"high": 3.0, "medium": 2.0, "low": 1.0}
        urgencia_map = {"high": 1.4, "medium": 1.1, "low": 1.0}
        impacto_map = {"high": 1.3, "medium": 1.1, "low": 1.0}

        resultados = []
        for task in tasks:
            puntaje = prioridad_map.get(task.priority_level or "medium", 2.0)
            titulo = (task.title or "").lower()
            desc = (task.description or "").lower()

            # Ajuste por palabras clave en título
            if any(w in titulo for w in ['bug', 'fix', 'crític', 'urgent', 'hotfix', 'error', 'caído', 'seguridad']):
                puntaje *= 1.8
                logger.debug(f"🔧 Palabra clave crítica en título: {task.title}")
            # Ajuste por palabras clave en descripción
            elif any(w in desc for w in ['urgent', 'important', 'critical', 'importante', 'crític']):
                puntaje *= 1.5
                logger.debug(f"❗ Palabra clave urgente en descripción: {task.title}")

            # Ajuste por metadatos
            puntaje *= urgencia_map.get(task.urgency or "medium", 1.0)
            puntaje *= impacto_map.get(task.impact or "medium", 1.0)

            # Ajuste por deadline
            if task.deadline:
                dias = (task.deadline - datetime.now()).days
                if dias < 0:
                    puntaje *= 2.5
                    logger.debug(f"🚨 Deadline vencido: {task.title}")
                elif dias == 0:
                    puntaje *= 2.0
                    logger.debug(f"⏳ Deadline hoy: {task.title}")
                elif dias <= 1:
                    puntaje *= 1.7
                    logger.debug(f"📅 Deadline mañana: {task.title}")
                elif dias <= 3:
                    puntaje *= 1.3
                    logger.debug(f"📅 Deadline en 3 días: {task.title}")

            resultados.append({
                'task_obj': task,
                'puntaje_ml': float(puntaje),
                'titulo': task.title
            })
            logger.debug(f"🔖 Tarea '{task.title[:20]}' asignado puntaje por reglas: {puntaje:.2f}")

        return self._post_procesamiento(resultados)

    def predecir_prioridad_tareas(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Predice prioridad usando ML si hay suficientes datos, si no usa reglas"""
        if not tasks:
            return []

        # Verificar si hay suficientes datos para ML
        completed_count = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.status == 'completed'
        ).count()
        logger.info(f"✅ Tareas completadas disponibles: {completed_count}")

        # Si no hay suficientes datos o modelo no cargado, usar reglas
        if self.modelo is None or completed_count < 3:
            logger.warning(f"🧠 Usando sistema de reglas (modelo no disponible o solo {completed_count}/3 tareas completadas)")
            return self._prioridad_por_reglas(tasks)

        try:
            logger.info("🤖 Usando modelo ML para predicción")
            datos_pred = []
            
            for task in tasks:
                # Calcular si tiene deadline próximo
                deadline_proximo = 0
                if task.deadline:
                    dias = (task.deadline - datetime.now()).days
                    deadline_proximo = 1 if dias <= 1 else 0
                
                d = {
                    'task_obj': task,
                    'urgencia_encoded': URGENCIA_MAP.get(_normalizar_nivel(task.urgency), 1),
                    'impacto_encoded': IMPACTO_MAP.get(_normalizar_nivel(task.impact), 1),
                    'energia_encoded': ENERGIA_MAP.get(_normalizar_nivel(task.energy_required), 1),
                    'duracion_estimada': float(task.estimated_duration or 60),
                    'longitud_descripcion': len(task.description or ""),
                    'tiene_urgente': 1 if "urgent" in (task.description or "").lower() or "crític" in (task.title or "").lower() else 0,
                    'tiene_bug': 1 if "bug" in (task.title or "").lower() or "fix" in (task.title or "").lower() else 0,
                    'deadline_proximo': deadline_proximo
                }
                datos_pred.append(d)

            # Preparar datos para predicción
            X_pred = []
            for d in datos_pred:
                x = [
                    d['urgencia_encoded'],
                    d['impacto_encoded'],
                    d['energia_encoded'],
                    d['duracion_estimada'],
                    d['longitud_descripcion'],
                    d['tiene_urgente'],
                    d['tiene_bug'],
                    d['deadline_proximo']
                ]
                X_pred.append(x)

            X_pred = np.array(X_pred)
            logger.info(f"📊 Datos para predicción (shape: {X_pred.shape}):\n{X_pred}")

            # Realizar predicciones
            predicciones = self.modelo.predict(X_pred)
            logger.info(f"🎯 Predicciones del modelo (niveles de prioridad): {predicciones}")

            # Convertir a puntajes (1, 2, 3)
            resultados = []
            for i, d in enumerate(datos_pred):
                puntaje = float(predicciones[i])  # Ya es 1, 2 o 3
                resultados.append({
                    'task_obj': d['task_obj'],
                    'puntaje_ml': puntaje,
                    'titulo': d['task_obj'].title
                })
                logger.info(f"📈 Tarea '{d['task_obj'].title[:20]}': prioridad ML = {puntaje:.0f}")

            # Aplicar post-procesamiento
            resultados = self._post_procesamiento(resultados)
            
            # Ordenar por puntaje
            resultados_ordenados = sorted(resultados, key=lambda x: x['puntaje_ml'], reverse=True)
            logger.info("✅ Predicción con ML completada exitosamente")
            return resultados_ordenados

        except Exception as e:
            logger.error(f"❌ Error crítico en predicción ML: {e}")
            logger.error(traceback.format_exc())
            logger.warning("🔄 Fallback a sistema de reglas tras error en ML")
            return self._prioridad_por_reglas(tasks)

    def recomendar_horario(self, task: Task) -> str:
        """Recomienda hora basado en energía y tipo de tarea"""
        try:
            energia = task.energy_required or "medium"
            titulo = (task.title or "").lower()
            
            if energia == "high" or any(w in titulo for w in ['bug', 'fix', 'critical', 'error', 'caído', 'seguridad']):
                return "08:00"
            elif 10 <= datetime.now().hour < 15 and energia == "medium":
                return "12:00"
            elif energia == "medium":
                return "14:00"
            else:
                return "16:00"
        except Exception as e:
            logger.error(f"❌ Error en recomendar_horario: {e}")
            logger.error(traceback.format_exc())
            return "10:00"